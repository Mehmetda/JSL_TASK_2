import openai
from langchain_huggingface import HuggingFaceEmbeddings
from qdrant_client import QdrantClient
from langchain_qdrant import QdrantVectorStore
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from rank_bm25 import BM25Okapi
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.environ.get("OPENAI_API_KEY")

embeddings = HuggingFaceEmbeddings(model_name="NeuML/pubmedbert-base-embeddings")
client = QdrantClient(url="http://localhost:6333")
db = QdrantVectorStore(client=client, collection_name="vector_db", embedding=embeddings)

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
        
        # Add metadata to each text chunk
        for i, text in enumerate(texts):
            filename = os.path.basename(file_path)
            if filename.startswith("temp_"):
                filename = filename[5:]  # Remove temp_ prefix
            
            # Calculate actual page number based on document structure
            # Assuming each chunk represents roughly equal content distribution
            total_pages = len(docs) if docs else 1
            chunk_pages = len(texts)
            
            if chunk_pages > 0:
                # Distribute chunks across actual pages
                page_number = min((i * total_pages // chunk_pages) + 1, total_pages)
            else:
                page_number = 1
            
            text.metadata.update({
                "source": filename,
                "page": f"{page_number}",
                "split": f"{i+1} of {len(texts)}"
            })
        
        db.add_documents(texts)
        return {"success": True, "message": f"Processed {ext} file successfully"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}

def query_system(question, top_k=5, score_threshold=0.3, re_rank_retrievals=True, bm25_enabled=False):
    try:
        # Vector search
        retriever = db.as_retriever(search_kwargs={"k": top_k, "score_threshold": score_threshold})
        docs = retriever.invoke(question)
        
        if not docs:
            return {
                "answer": "I don't have enough information. Please upload relevant documents first.",
                "source_document": "",
                "doc": "",
                "metadata": {}
            }

        # BM25 re-ranking if enabled
        if bm25_enabled and docs:
            all_docs = db.get()
            if all_docs:
                corpus = [doc.page_content for doc in all_docs]
                bm25 = BM25Okapi(corpus)
                bm25_scores = bm25.get_scores(question.split())
                
                # Combine and sort by BM25 scores
                doc_scores = [(doc, bm25_scores[i] if i < len(bm25_scores) else 0) for i, doc in enumerate(docs)]
                doc_scores.sort(key=lambda x: x[1], reverse=True)
                docs = [doc for doc, score in doc_scores[:top_k]]

        # Simple re-ranking if enabled
        if re_rank_retrievals and docs:
            question_words = set(question.lower().split())
            doc_scores = []
            
            for doc in docs:
                doc_words = set(doc.page_content.lower().split())
                overlap = len(question_words.intersection(doc_words))
                doc_scores.append((doc, overlap))
            
            doc_scores.sort(key=lambda x: x[1], reverse=True)
            docs = [doc for doc, score in doc_scores[:top_k]]

        # Generate answer
        context = "\n".join([doc.page_content for doc in docs])
        prompt = f"Based on this medical text, answer: {question}\n\nText: {context}\n\nAnswer:"
        
        response = openai.responses.create(model="gpt-4o", input=prompt)

        # Prepare metadata
        doc = docs[0]
        page_info = doc.metadata.get('page', 'N/A')
        split_info = doc.metadata.get('split', 'N/A')

        metadata = {
            "source": doc.metadata.get('source', 'Unknown'),
            "page": page_info,
            "split": split_info
        }

        return {
            "answer": response.output_text,
            "source_document": doc.page_content,
            "doc": doc.metadata.get('source', 'Unknown'),
            "metadata": metadata
        }
        
    except Exception as e:
        return {"error": f"System error: {str(e)}"}

def upload_file(file_path):
    os.makedirs("data", exist_ok=True)
    return process_file(file_path)

if __name__ == "__main__":
    question = "What are the symptoms of diabetes?"
    response = query_system(question, top_k=5, score_threshold=0.3, re_rank_retrievals=True, bm25_enabled=False)
    print(f"Question: {question}")
    print(f"Answer: {response.get('answer', 'No answer')}")
    print(f"Source Document: {response.get('source_document', '')}")
    print(f"Doc: {response.get('doc', '')}") 