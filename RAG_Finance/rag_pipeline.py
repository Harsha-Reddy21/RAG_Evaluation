import logging
import time
from typing import Dict, Any, List, Optional
import asyncio
from datetime import datetime

from vector_store import vector_store
from llm import openai_client
from cache import cache
from metrics import metrics
from models import QueryMetrics
from database import get_db

# Configure logging
logger = logging.getLogger(__name__)

class RAGPipeline:
    """Retrieval-Augmented Generation pipeline for financial queries"""
    
    def __init__(self):
        """Initialize the RAG pipeline"""
        logger.info("RAG pipeline initialized")
    
    async def process_query(self, company: str, question: str, api_key: str) -> Dict[str, Any]:
        """
        Process a financial query through the RAG pipeline
        
        Args:
            company: Company to query about
            question: Question to answer
            api_key: API key for tracking
            
        Returns:
            Dictionary with answer and metadata
        """
        start_time = time.time()
        metrics.increment_concurrent()
        
        try:
            # Check cache first
            cache_key = cache.get_cache_key(company, question)
            cached_answer = await cache.get(cache_key)
            
            if cached_answer:
                # Cache hit
                logger.info(f"Cache hit for query: {company} - {question[:50]}...")
                latency = time.time() - start_time
                metrics.record_query(company, latency, cache_hit=True)
                
                # Record metrics in database
                await self._record_query_metrics(
                    company=company,
                    question=question,
                    latency=latency,
                    cache_hit=True,
                    api_key=api_key
                )
                
                return {
                    "answer": cached_answer,
                    "source": "cache",
                    "latency_seconds": latency
                }
            
            # Cache miss - need to generate answer
            logger.info(f"Cache miss for query: {company} - {question[:50]}...")
            
            # 1. Generate embedding for the question
            question_embedding = await openai_client.get_embedding_async(question)
            
            # 2. Query vector store for relevant documents
            matches = vector_store.query(question_embedding, company)
            
            if not matches:
                logger.warning(f"No relevant documents found for: {company} - {question[:50]}...")
                return {
                    "answer": f"I don't have enough information about {company} to answer this question.",
                    "source": "generated",
                    "latency_seconds": time.time() - start_time
                }
            
            # 3. Build context from retrieved documents
            context = self._build_context(matches)
            
            # 4. Generate answer with LLM
            answer = await openai_client.generate_answer_async(context, question)
            
            # 5. Determine if this is real-time or historical data
            is_real_time = self._is_real_time_query(question)
            
            # 6. Cache the result
            await cache.set(cache_key, answer, is_real_time)
            
            # Record metrics
            latency = time.time() - start_time
            metrics.record_query(company, latency, cache_hit=False)
            
            # Record metrics in database
            await self._record_query_metrics(
                company=company,
                question=question,
                latency=latency,
                cache_hit=False,
                api_key=api_key
            )
            
            return {
                "answer": answer,
                "source": "generated",
                "latency_seconds": latency
            }
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            latency = time.time() - start_time
            return {
                "answer": "Sorry, I encountered an error while processing your question.",
                "source": "error",
                "latency_seconds": latency,
                "error": str(e)
            }
        finally:
            metrics.decrement_concurrent()
    
    def _build_context(self, matches: List[Dict[str, Any]]) -> str:
        """
        Build context from retrieved documents
        
        Args:
            matches: List of matching documents from vector store
            
        Returns:
            Context string for the LLM
        """
        context_parts = []
        
        for match in matches:
            metadata = match.get('metadata', {})
            score = match.get('score', 0)
            
            # Only include documents with reasonable similarity
            if score < 0.7:
                continue
                
            # Format document content with metadata
            doc_context = (
                f"{metadata.get('company', 'Unknown')} {metadata.get('report_type', 'Report')} "
                f"({metadata.get('report_date', 'Unknown date')}):\n{metadata.get('content', '')}"
            )
            context_parts.append(doc_context)
        
        # Join all context parts
        return "\n\n".join(context_parts)
    
    def _is_real_time_query(self, question: str) -> bool:
        """
        Determine if a query is about real-time/current data
        
        Args:
            question: Question text
            
        Returns:
            True if the query is about real-time data, False if historical
        """
        question_lower = question.lower()
        real_time_indicators = [
            "current", "latest", "now", "today", "present", "recent",
            "this quarter", "this year", "this month", "this week"
        ]
        
        for indicator in real_time_indicators:
            if indicator in question_lower:
                return True
        
        return False
    
    async def _record_query_metrics(self, company: str, question: str, latency: float, 
                                   cache_hit: bool, api_key: str):
        """
        Record query metrics in database
        
        Args:
            company: Company being queried
            question: Question text
            latency: Query latency in seconds
            cache_hit: Whether the query was served from cache
            api_key: API key used for the query
        """
        try:
            db = next(get_db())
            
            query_metric = QueryMetrics(
                query_text=question,
                company=company,
                latency_seconds=latency,
                cache_hit=1 if cache_hit else 0,
                api_key=api_key
            )
            
            db.add(query_metric)
            db.commit()
        except Exception as e:
            logger.error(f"Error recording query metrics: {str(e)}")

# Create a RAG pipeline instance
rag_pipeline = RAGPipeline() 