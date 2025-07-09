import logging
import time
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime

from vector_store import vector_store
from llm import openai_client
from database import get_db
from models import FinancialReport

# Configure logging
logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Document processor for ingesting financial reports"""
    
    def __init__(self):
        """Initialize the document processor"""
        logger.info("Document processor initialized")
    
    async def process_document(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a financial document for ingestion
        
        Args:
            document: Document data including company, report_type, report_date, section, content
            
        Returns:
            Dictionary with processing status and metadata
        """
        start_time = time.time()
        
        try:
            # Extract document data
            company = document.get('company')
            report_type = document.get('report_type')
            report_date = document.get('report_date')
            section = document.get('section')
            content = document.get('content')
            
            # Validate required fields
            if not all([company, report_type, report_date, content]):
                return {
                    "success": False,
                    "error": "Missing required fields: company, report_type, report_date, content",
                    "processing_time": time.time() - start_time
                }
            
            # Generate document ID
            doc_id = f"{company}_{report_type}_{report_date}_{uuid.uuid4().hex[:8]}"
            
            # Generate embedding
            embedding = await openai_client.get_embedding_async(content)
            
            # Prepare metadata
            metadata = {
                "company": company,
                "report_type": report_type,
                "report_date": report_date,
                "section": section,
                "content": content[:300]  # Store preview in metadata
            }
            
            # Store in vector database
            vector_store.upsert_documents([{
                "id": doc_id,
                "embedding": embedding,
                "metadata": metadata
            }])
            
            # Store in relational database
            await self._store_in_database(
                doc_id=doc_id,
                company=company,
                report_type=report_type,
                report_date=report_date,
                section=section,
                content=content
            )
            
            processing_time = time.time() - start_time
            logger.info(f"Document processed successfully: {doc_id} in {processing_time:.2f}s")
            
            return {
                "success": True,
                "document_id": doc_id,
                "processing_time": processing_time
            }
            
        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "processing_time": time.time() - start_time
            }
    
    async def _store_in_database(self, doc_id: str, company: str, report_type: str, 
                               report_date: str, section: str, content: str):
        """
        Store document in relational database
        
        Args:
            doc_id: Document ID
            company: Company name
            report_type: Type of report
            report_date: Date of report
            section: Section of report
            content: Document content
        """
        try:
            db = next(get_db())
            
            # Parse date string to datetime
            try:
                parsed_date = datetime.fromisoformat(report_date)
            except ValueError:
                # Fallback to current date if parsing fails
                parsed_date = datetime.now()
            
            report = FinancialReport(
                company=company,
                report_type=report_type,
                report_date=parsed_date,
                section=section or "General",
                content=content,
                embedding_id=doc_id
            )
            
            db.add(report)
            db.commit()
            logger.info(f"Document stored in database: {doc_id}")
            
        except Exception as e:
            logger.error(f"Error storing document in database: {str(e)}")
            raise
    
    async def batch_process_documents(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process a batch of documents
        
        Args:
            documents: List of document dictionaries
            
        Returns:
            Dictionary with processing statistics
        """
        start_time = time.time()
        results = []
        
        for document in documents:
            result = await self.process_document(document)
            results.append(result)
        
        # Calculate statistics
        successful = sum(1 for r in results if r.get('success', False))
        failed = len(results) - successful
        
        return {
            "total_documents": len(documents),
            "successful": successful,
            "failed": failed,
            "processing_time": time.time() - start_time
        }

# Create a document processor instance
document_processor = DocumentProcessor() 