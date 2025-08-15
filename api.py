from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from rag_openai import upload_file as rag_upload_file, query_system as rag_query_system
import tempfile
import shutil
import os


app = FastAPI(title="RAG Backend API")


class QueryRequest(BaseModel):
    question: str
    top_k: int = 5
    score_threshold: float = 0.3


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    try:
        suffix = os.path.splitext(file.filename)[1] or ".tmp"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(file.file, tmp)
            temp_path = tmp.name

        result = rag_upload_file(temp_path)

        if os.path.exists(temp_path):
            os.remove(temp_path)

        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/query")
async def query(request: QueryRequest):
    try:
        response = rag_query_system(
            question=request.question,
            top_k=request.top_k,
            score_threshold=request.score_threshold,
        )
        return response
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))



