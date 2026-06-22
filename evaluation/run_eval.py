import json

import requests

with open("evaluation/sample_questions.json") as f:
    questions = json.load(f)

for item in questions:
    response = requests.post(
        "http://localhost:8000/chat", json={"question": item["question"]}
    )

    print("\nQuestion:", item["question"])

    print("Answer:", response.json())
