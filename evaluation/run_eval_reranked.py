import json
import math
import os
import time

import requests
from datasets import Dataset
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import ChatOllama
from ragas import evaluate
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.llms import LangchainLLMWrapper
from ragas.metrics import (
    answer_relevancy,
    context_precision,
    faithfulness,
)
from ragas.run_config import RunConfig

# --------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------

BASE_URL = "http://localhost:7860"

API_KEY = os.getenv("API_KEY", "")

QUESTIONS_FILE = "evaluation/sample_questions.json"

BASELINE_FILE = "evaluation_results/baseline_results.json"

RESULTS_FILE = "evaluation_results/reranked_results.json"

HEADERS = {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY,
}

os.makedirs("evaluation_results", exist_ok=True)

# --------------------------------------------------------------------
# Judge LLM
# --------------------------------------------------------------------

print("Loading Groq evaluation model...")

judge_llm = LangchainLLMWrapper(
    ChatOllama(
        model="qwen2.5-coder:14b-instruct",
        temperature=0,
    )
)

print("Judge ready.")

# --------------------------------------------------------------------
# Embeddings
# --------------------------------------------------------------------

print("Loading BAAI embeddings...")

judge_embeddings = LangchainEmbeddingsWrapper(
    HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")
)

print("Embeddings ready.\n")

# --------------------------------------------------------------------
# Backend helper
# --------------------------------------------------------------------


def ask_question(
    question: str,
    rerank: bool = True,
) -> dict:
    """
    Calls backend /chat endpoint with reranking enabled.

    Returns

    {
        answer,
        contexts,
        sources
    }
    """

    response = requests.post(
        f"{BASE_URL}/chat",
        headers=HEADERS,
        json={
            "question": question,
            "rerank": rerank,
        },
        timeout=120,
    )

    response.raise_for_status()

    return response.json()


# --------------------------------------------------------------------
# Score helper
# --------------------------------------------------------------------


def safe_score(value):
    """
    Convert RAGAS outputs into a float.
    """

    if isinstance(value, list):
        valid = [
            v
            for v in value
            if (v is not None and not (isinstance(v, float) and math.isnan(v)))
        ]

        if not valid:
            return 0.0

        return sum(valid) / len(valid)

    if value is None:
        return 0.0

    if isinstance(value, float) and math.isnan(value):
        return 0.0

    return float(value)


# --------------------------------------------------------------------
# Main evaluation
# --------------------------------------------------------------------


def run_evaluation():
    print("=" * 70)
    print("RAGAS Evaluation — With Cross-Encoder Reranking")
    print("=" * 70)

    with open(QUESTIONS_FILE) as f:
        questions = json.load(f)

    rows = {
        "question": [],
        "answer": [],
        "contexts": [],
        "ground_truth": [],
    }

    print(f"\nRunning {len(questions)} evaluation questions...\n")

    for idx, item in enumerate(questions, start=1):
        question = item["question"]
        ground_truth = item.get("ground_truth", "")

        print(f"[{idx}/{len(questions)}] {question}")

        try:
            result = ask_question(
                question=question,
                rerank=True,
            )

            answer = result.get("answer", "")
            contexts = result.get("contexts", [])

            rows["question"].append(question)
            rows["answer"].append(answer)
            rows["contexts"].append(contexts)
            rows["ground_truth"].append(ground_truth)

            print(f"  ✓ {len(contexts)} chunks | {answer[:70]}...")

            # avoid Groq rate limits
            time.sleep(1)

        except Exception as e:
            print(f"  ✗ {e}")

    if len(rows["question"]) == 0:
        print("\nNo successful evaluations.")
        return

    print("\n")
    print("=" * 70)
    print("Running RAGAS Evaluation...")
    print("=" * 70)

    dataset = Dataset.from_dict(rows)

    scores = evaluate(
        dataset=dataset,
        metrics=[
            faithfulness,
            answer_relevancy,
            context_precision,
        ],
        llm=judge_llm,
        embeddings=judge_embeddings,
        run_config=RunConfig(
            timeout=600,
            max_workers=1,
            max_retries=2,
        ),
        raise_exceptions=False,
    )

    faithfulness_score = safe_score(scores["faithfulness"])

    answer_relevancy_score = safe_score(scores["answer_relevancy"])

    context_precision_score = safe_score(scores["context_precision"])

    average_score = (
        faithfulness_score + answer_relevancy_score + context_precision_score
    ) / 3

    print("\n")
    print("=" * 70)
    print("Reranked Results")
    print("=" * 70)

    print(f"Faithfulness      : {faithfulness_score:.4f}")
    print(f"Answer Relevancy  : {answer_relevancy_score:.4f}")
    print(f"Context Precision : {context_precision_score:.4f}")
    print("-" * 70)
    print(f"Average           : {average_score:.4f}")

    # --------------------------------------------------------------
    # Compare against baseline
    # --------------------------------------------------------------

    if os.path.exists(BASELINE_FILE):
        with open(BASELINE_FILE) as f:
            baseline = json.load(f)

        baseline_scores = baseline["scores"]

        print("\n")
        print("=" * 70)
        print("Improvement over Baseline")
        print("=" * 70)

        comparisons = [
            (
                "Faithfulness",
                faithfulness_score,
                baseline_scores["faithfulness"],
            ),
            (
                "Answer Relevancy",
                answer_relevancy_score,
                baseline_scores["answer_relevancy"],
            ),
            (
                "Context Precision",
                context_precision_score,
                baseline_scores["context_precision"],
            ),
            (
                "Average",
                average_score,
                baseline_scores["average"],
            ),
        ]

        for name, new_score, old_score in comparisons:
            diff = new_score - old_score

            if diff > 0:
                arrow = "↑"
            elif diff < 0:
                arrow = "↓"
            else:
                arrow = "="

            print(
                f"{name:<20}"
                f"{old_score:.4f}"
                f"  ->  "
                f"{new_score:.4f}"
                f"   ({arrow} {diff:+.4f})"
            )

    else:
        print("\nBaseline results not found.")
        print("Run baseline evaluation first:")
        print("python3.12 evaluation/run_eval.py")

    # --------------------------------------------------------------
    # Save results
    # --------------------------------------------------------------

    output = {
        "run": "reranked",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "num_questions": len(rows["question"]),
        "scores": {
            "faithfulness": round(
                faithfulness_score,
                4,
            ),
            "answer_relevancy": round(
                answer_relevancy_score,
                4,
            ),
            "context_precision": round(
                context_precision_score,
                4,
            ),
            "average": round(
                average_score,
                4,
            ),
        },
    }

    with open(
        RESULTS_FILE,
        "w",
    ) as f:
        json.dump(
            output,
            f,
            indent=2,
        )

    print("\n")
    print(f"✓ Results saved to {RESULTS_FILE}")

    return output


# --------------------------------------------------------------------
# Entry Point
# --------------------------------------------------------------------

if __name__ == "__main__":
    run_evaluation()
