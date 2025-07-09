import logging
import uvicorn
import os
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Import all necessary modules
from config import API_HOST, API_PORT, API_WORKERS
from api import app
from database import db
from cache import cache
from vector_store import vector_store
from metrics import metrics
from rag_pipeline import rag_pipeline
from document_processor import document_processor

logger = logging.getLogger(__name__)

def main():
    """Main entry point for the application"""
    logger.info("Starting Financial RAG API")
    
    # Run the API
    uvicorn.run(
        "api:app",
        host=API_HOST,
        port=API_PORT,
        workers=API_WORKERS,
        log_level="info"
    )

if __name__ == "__main__":
    main() 