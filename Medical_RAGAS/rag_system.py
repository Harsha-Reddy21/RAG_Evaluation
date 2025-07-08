import os
import pdfplumber
from typing import List, Dict, Tuple, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# LangChain imports - updated to new package structure
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA

# RAGAS imports
from ragas.metrics import (
    context_precision,
    context_recall,
    faithfulness,
    answer_relevancy
)
from ragas import evaluate
from datasets import Dataset

# Initialize global variables
VECTOR_DB_PATH = "vector_db"
os.makedirs(VECTOR_DB_PATH, exist_ok=True)

# Document Processing Functions
def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from a PDF file"""
    all_text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    all_text += text + "\n"
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
    return all_text

def split_text(text: str) -> List[str]:
    """Split text into chunks for embedding"""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    return text_splitter.split_text(text)

def process_document(text: str, doc_name: str) -> None:
    """Process a document and add it to the vector store"""
    # Split text into chunks
    chunks = split_text(text)
    
    # Create document metadata
    metadatas = [{"source": doc_name, "chunk": i} for i in range(len(chunks))]
    
    # Initialize embedding model
    embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")
    
    # Create or update vector store
    if os.path.exists(f"{VECTOR_DB_PATH}/index.faiss"):
        # Load existing vector store
        vectorstore = FAISS.load_local(VECTOR_DB_PATH, embedding_model)
        # Add new documents
        vectorstore.add_texts(chunks, metadatas=metadatas)
    else:
        # Create new vector store
        vectorstore = FAISS.from_texts(chunks, embedding=embedding_model, metadatas=metadatas)
    
    # Save vector store
    vectorstore.save_local(VECTOR_DB_PATH)

# RAG Query Functions
def get_retriever():
    """Get the retriever from the vector store"""
    embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")
    
    if os.path.exists(f"{VECTOR_DB_PATH}/index.faiss"):
        vectorstore = FAISS.load_local(VECTOR_DB_PATH, embedding_model)
        return vectorstore.as_retriever(search_type="similarity", k=4)
    else:
        raise FileNotFoundError("Vector store not found. Please add documents first.")

def ask_medical_question(query: str) -> Tuple[str, List[Any]]:
    """Ask a medical question and get answer with source documents"""
    # Initialize LLM
    llm = ChatOpenAI(model_name="gpt-4", temperature=0)
    
    # Get retriever
    retriever = get_retriever()
    
    # Create QA chain
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True
    )
    
    # Get answer
    result = qa_chain(query)
    return result["result"], result["source_documents"]

# Evaluation Functions
def evaluate_response(query: str, answer: str, contexts: List[str]) -> Dict[str, float]:
    """Evaluate a response using RAGAS metrics"""
    # Create dataset
    data = {
        "question": [query],
        "contexts": [contexts],
        "answer": [answer],
        # Note: In a real system, you would have ground truth answers for evaluation
        # For this demo, we'll use the generated answer as ground truth
        "ground_truth": [answer]
    }
    
    ds = Dataset.from_dict(data)
    
    # Evaluate
    ragas_results = evaluate(
        dataset=ds,
        metrics=[context_precision, context_recall, faithfulness, answer_relevancy]
    )
    
    # Convert to dict
    metrics_df = ragas_results.to_pandas()
    metrics = {
        "context_precision": float(metrics_df["context_precision"].iloc[0]),
        "context_recall": float(metrics_df["context_recall"].iloc[0]),
        "faithfulness": float(metrics_df["faithfulness"].iloc[0]),
        "answer_relevancy": float(metrics_df["answer_relevancy"].iloc[0])
    }
    
    return metrics 