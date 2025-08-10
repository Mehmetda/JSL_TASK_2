import openai
from langchain_community.embeddings import SentenceTransformerEmbeddings
from qdrant_client import QdrantClient
from langchain_community.vectorstores import Qdrant
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.environ.get("OPENAI_API_KEY")

embeddings = SentenceTransformerEmbeddings(model_name="NeuML/pubmedbert-base-embeddings")
client = QdrantClient(url="http://localhost:6333")
db = Qdrant(client=client, embeddings=embeddings, collection_name="vector_db")

def process_file(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    try:
        if ext == '.pdf':
            loader = PyPDFLoader(file_path)
        elif ext in ['.txt', '.md']:
            loader = TextLoader(file_path)
        else:
            return {"success": False, "message": f"Unsupported file type: {ext}"}

        docs = loader.load()
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        texts = splitter.split_documents(docs)
        db.add_documents(texts)
        return {"success": True, "message": f"Processed {ext} file successfully"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}

def query_system(question, top_k=5, score_threshold=0.3):
    try:
        retriever = db.as_retriever(search_kwargs={"k": top_k, "score_threshold": score_threshold})
        docs = retriever.get_relevant_documents(question)

        if not docs:
            return {
                "answer": "I don't have enough information. Please upload relevant documents first.",
                "source_document": "",
                "doc": ""
            }

        context = "\n".join([doc.page_content for doc in docs])
        prompt = f"Context: {context}\nQuestion: {question}\nAnswer:"
        response = openai.responses.create(model="gpt-4o", input=prompt)

        source_document = docs[0].page_content if docs else ""
        doc = docs[0].metadata.get('source', 'Unknown') if docs else ""

        return {
            "answer": response.output_text,
            "source_document": source_document,
            "doc": doc
        }
    except Exception as e:
        return {"error": f"System error: {str(e)}"}

def upload_file(file_path):
    os.makedirs("data", exist_ok=True)
    return process_file(file_path)

if __name__ == "__main__":
    question = "What are the symptoms of diabetes?"
    response = query_system(question, top_k=5, score_threshold=0.3)
    print(f"Question: {question}")
    print(f"Answer: {response.get('answer', 'No answer')}")
    print(f"Source Document: {response.get('source_document', '')}")
    print(f"Doc: {response.get('doc', '')}") 