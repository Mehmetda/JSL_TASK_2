# FastAPI uygulaması için Dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN pip install langchain_community
CMD ["uvicorn", "rag:app", "--host", "0.0.0.0", "--port", "8000"] 