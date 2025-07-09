from pinecone import Pinecone, ServerlessSpec
import logging
from typing import List, Dict, Any, Optional
import time
from config import (
    PINECONE_API_KEY,
    PINECONE_INDEX_NAME,
    PINECONE_DIMENSION,
    PINECONE_CLOUD,
    PINECONE_REGION
)

# Configure logging
logger = logging.getLogger(__name__)

class PineconeManager:
    """Pinecone vector store manager for the financial RAG system"""
    
    def __init__(self):
        self.client = None
        self.index = None
    
    def connect(self):
        """Initialize Pinecone connection and index"""
        try:
            # Initialize Pinecone client
            self.client = Pinecone(api_key=PINECONE_API_KEY)
            
            # Check if index exists, create if not
            if PINECONE_INDEX_NAME not in self.client.list_indexes():
                logger.info(f"Creating Pinecone index: {PINECONE_INDEX_NAME}")
                self.client.create_index(
                    name=PINECONE_INDEX_NAME,
                    dimension=PINECONE_DIMENSION,
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud=PINECONE_CLOUD,
                        region=PINECONE_REGION
                    )
                )
                # Wait for index to be ready
                time.sleep(5)
            
            # Connect to the index
            self.index = self.client.Index(PINECONE_INDEX_NAME)
            logger.info(f"Connected to Pinecone index: {PINECONE_INDEX_NAME}")
            
        except Exception as e:
            logger.error(f"Pinecone connection error: {str(e)}")
            raise
    
    def upsert_documents(self, documents: List[Dict[str, Any]]):
        """
        Upload documents to Pinecone
        
        Args:
            documents: List of document dictionaries with id, embedding, and metadata
        """
        if not self.index:
            self.connect()
        
        try:
            # Format documents for Pinecone
            pinecone_docs = [(doc["id"], doc["embedding"], doc["metadata"]) for doc in documents]
            
            # Upsert to Pinecone
            self.index.upsert(vectors=pinecone_docs)
            logger.info(f"Upserted {len(documents)} documents to Pinecone")
            
        except Exception as e:
            logger.error(f"Pinecone upsert error: {str(e)}")
            raise
    
    def query(self, embedding: List[float], company: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Query Pinecone for similar documents
        
        Args:
            embedding: Query vector embedding
            company: Company to filter results by
            top_k: Number of results to return
            
        Returns:
            List of matching documents
        """
        if not self.index:
            self.connect()
        
        try:
            # Query Pinecone with company filter
            results = self.index.query(
                vector=embedding,
                top_k=top_k,
                include_metadata=True,
                filter={"company": {"$eq": company}}
            )
            
            return results.get("matches", [])
            
        except Exception as e:
            logger.error(f"Pinecone query error: {str(e)}")
            return []
    
    def delete_documents(self, ids: List[str]):
        """Delete documents from Pinecone by ID"""
        if not self.index:
            self.connect()
        
        try:
            self.index.delete(ids=ids)
            logger.info(f"Deleted {len(ids)} documents from Pinecone")
        except Exception as e:
            logger.error(f"Pinecone delete error: {str(e)}")
            raise

# Create a vector store instance
vector_store = PineconeManager() 