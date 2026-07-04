import shutil
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, UploadFile
from qdrant_client.models import PointStruct

from app.core.logger import logger
from app.services.document_processor import DocumentProcessor
from app.services.embedding_service import EmbeddingService
from app.services.qdrant_service import QdrantService
from app.services.text_chunker import TextChunker

router = APIRouter()

processor = DocumentProcessor()
chunker = TextChunker()
embedding_service = EmbeddingService()
qdrant_service = QdrantService()


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    logger.info(f"Upload started: {file.filename}")

    upload_dir = Path("data")
    upload_dir.mkdir(exist_ok=True)

    file_path = upload_dir / file.filename

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    text = processor.extract_text(str(file_path))
    chunks = chunker.chunk_text(text)
    embeddings = embedding_service.embed_texts(chunks)

    points = [
        PointStruct(
            id=str(uuid4()),
            vector=vector,
            payload={"text": chunk, "source": file.filename},
        )
        for chunk, vector in zip(chunks, embeddings)
    ]

    qdrant_service.insert_chunks(points)

    logger.info(f"Stored {len(points)} vectors from {file.filename}")

    return {
        "filename": file.filename,
        "characters": len(text),
        "num_chunks": len(chunks),
        "stored_vectors": len(points),
        "sample_chunk": chunks[0][:200] if chunks else "",
    }
