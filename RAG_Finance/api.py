import logging
import time
from typing import List, Dict, Any, Optional
import asyncio
import uvicorn

from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import API_HOST, API_PORT, API_WORKERS
from models import QueryRequest, DocumentRequest, QueryResponse, MetricsResponse
from database import db, get_db
from cache import cache
from rate_limiter import rate_limiter
from metrics import metrics
from rag_pipeline import rag_pipeline
from document_processor import document_processor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Financial RAG API",
    description="Financial Retrieval-Augmented Generation API for corporate financial data",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware for request tracking
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# API key validation dependency
async def validate_api_key(api_key: str):
    """Validate API key (placeholder for actual validation logic)"""
    if not api_key or len(api_key) < 8:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return api_key

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": time.time()}

# Query endpoint
@app.post("/query", response_model=QueryResponse)
async def query_endpoint(query: QueryRequest, background_tasks: BackgroundTasks):
    """
    Process a financial query
    
    Args:
        query: Query request with company, question, and API key
        
    Returns:
        Query response with answer and metadata
    """
    # Validate API key
    await validate_api_key(query.api_key)
    
    # Check rate limit
    if not await rate_limiter.check_rate_limit(query.api_key):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    # Process query through RAG pipeline
    result = await rag_pipeline.process_query(
        company=query.company,
        question=query.question,
        api_key=query.api_key
    )
    
    # Update cache size metrics in background
    if cache.redis:
        background_tasks.add_task(
            metrics.update_cache_size,
            await cache.redis.dbsize()
        )
    
    return result

# Document ingestion endpoint
@app.post("/ingest")
async def ingest_document(document: DocumentRequest, background_tasks: BackgroundTasks):
    """
    Ingest a financial document
    
    Args:
        document: Document data including company, report_type, report_date, section, content
        
    Returns:
        Processing status and metadata
    """
    # Validate API key
    await validate_api_key(document.api_key)
    
    # Check rate limit
    if not await rate_limiter.check_rate_limit(document.api_key):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    # Process document in background
    background_tasks.add_task(
        document_processor.process_document,
        {
            "company": document.company,
            "report_type": document.report_type,
            "report_date": document.report_date,
            "section": document.section,
            "content": document.content
        }
    )
    
    return {"status": "Document queued for processing"}

# Batch document ingestion endpoint
@app.post("/ingest/batch")
async def ingest_batch(documents: List[DocumentRequest], background_tasks: BackgroundTasks):
    """
    Ingest a batch of financial documents
    
    Args:
        documents: List of document data
        
    Returns:
        Processing status
    """
    if not documents:
        raise HTTPException(status_code=400, detail="No documents provided")
    
    # Validate API key (use first document's API key)
    api_key = documents[0].api_key
    await validate_api_key(api_key)
    
    # Check rate limit
    if not await rate_limiter.check_rate_limit(api_key):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    # Convert to dictionary format
    docs_dict = [
        {
            "company": doc.company,
            "report_type": doc.report_type,
            "report_date": doc.report_date,
            "section": doc.section,
            "content": doc.content
        }
        for doc in documents
    ]
    
    # Process documents in background
    background_tasks.add_task(
        document_processor.batch_process_documents,
        docs_dict
    )
    
    return {"status": f"Batch of {len(documents)} documents queued for processing"}

# Metrics endpoint
@app.get("/metrics", response_model=MetricsResponse)
async def get_metrics():
    """Get system metrics"""
    # Get metrics from metrics manager
    metrics_summary = metrics.get_metrics_summary()
    
    # Get cache stats
    cache_stats = await cache.get_cache_stats()
    
    # Combine metrics
    combined_metrics = {
        "query_count": metrics_summary["total_queries"],
        "cache_hit_ratio": cache_stats["hit_ratio"],
        "concurrent_requests": metrics.concurrent_requests._value,
        "average_latency": metrics_summary.get("queries_per_second", 0),
        "cache_size": cache_stats["cache_size"]
    }
    
    return combined_metrics

# Rate limit status endpoint
@app.get("/rate-limit")
async def rate_limit_status(api_key: str):
    """Get rate limit status for an API key"""
    # Validate API key
    await validate_api_key(api_key)
    
    # Get remaining requests
    status = rate_limiter.get_remaining_requests(api_key)
    
    return {
        "api_key": api_key[:8] + "...",
        "remaining_requests": status["remaining"],
        "reset_seconds": status["reset_seconds"]
    }

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize connections and services on startup"""
    try:
        # Initialize database
        db.connect()
        
        # Initialize Redis cache
        await cache.connect()
        
        # Initialize vector store
        vector_store.connect()
        
        # Start metrics server
        metrics.start_metrics_server()
        
        logger.info("Financial RAG API started successfully")
    except Exception as e:
        logger.error(f"Startup error: {str(e)}")
        raise

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Close connections on shutdown"""
    try:
        # Close database connection
        db.close()
        
        # Close Redis connection
        await cache.close()
        
        logger.info("Financial RAG API shut down successfully")
    except Exception as e:
        logger.error(f"Shutdown error: {str(e)}")

# Run the application
if __name__ == "__main__":
    uvicorn.run(
        "api:app",
        host=API_HOST,
        port=API_PORT,
        workers=API_WORKERS
    ) 