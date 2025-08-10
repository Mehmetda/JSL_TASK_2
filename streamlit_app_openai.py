import streamlit as st
import os
from dotenv import load_dotenv
from rag_openai import query_system, upload_file
from qdrant_client import QdrantClient

load_dotenv()

def clear_cache():
    try:
        client = QdrantClient(url="http://localhost:6333")
        client.delete_collection("vector_db")
        client.create_collection("vector_db")
        
        for file in os.listdir("."):
            if file.startswith("temp_"):
                os.remove(file)
        
        st.cache_data.clear()
        st.cache_resource.clear()
        return True
    except Exception as e:
        return False

st.set_page_config(page_title="Medical RAG QA App", page_icon="🏥")

with st.sidebar:
    st.image("jsl_logo.svg", width=200)
    st.selectbox("Choose LLM Type", ["gpt-4o", "gpt-3.5-turbo", "gpt-4"], index=0)
    
    # RAG Parametreleri
    st.markdown("---")
    st.markdown("### RAG Settings")
    
    top_k = st.slider(
        "Select Top K values", 
        min_value=1, 
        max_value=50, 
        value=5,
        help="Vektör veritabanından kaç doküman alınacağı"
    )
    
    score_threshold = st.slider(
        "Select Score Threshold", 
        min_value=0.1, 
        max_value=1.0, 
        value=0.3,
        step=0.1,
        help="Minimum benzerlik skoru (0.1-1.0)"
    )

st.title("Medical RAG QA App")

uploaded_files = st.file_uploader("Upload Documents", accept_multiple_files=True, type=['pdf', 'txt', 'md'])

if uploaded_files:
    for uploaded_file in uploaded_files:
        temp_file_path = f"temp_{uploaded_file.name}"
        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        with st.spinner(f"Processing {uploaded_file.name}..."):
            result = upload_file(temp_file_path)
        
        if result.get("success"):
            st.success(f"✅ {uploaded_file.name} uploaded successfully")
        else:
            st.error(f"❌ Error: {result.get('message', 'Unknown error')}")
        
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

st.markdown("---")

question = st.text_area("Question:", placeholder="Example: What are the symptoms of diabetes?", height=100)

col1, col2 = st.columns([1, 1])

with col1:
    if st.button("Submit", type="primary"):
        if question.strip():
            with st.spinner("Processing..."):
                try:
                    response = query_system(question, top_k, score_threshold)
                    
                    if "error" in response:
                        st.error(f"Error: {response['error']}")
                    else:
                        st.markdown("### Answer")
                        st.write(response.get("answer", "No answer found"))
                        
                        if response.get("source_document"):
                            st.markdown("---")
                            st.markdown("### Context:")
                            st.write(response.get("source_document", ""))
                        
                        if response.get("doc"):
                            st.markdown("**Source Document:**")
                            st.code(response.get("doc", ""), language="text")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.warning("Please enter a question")

with col2:
    if st.button("Clear Cache", type="primary"):
        if clear_cache():
            st.success("✅ Cache cleared successfully!")
        else:
            st.error("❌ Error clearing cache")

 