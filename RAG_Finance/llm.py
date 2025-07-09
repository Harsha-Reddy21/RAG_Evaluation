from openai import OpenAI
import httpx
import logging
import asyncio
from typing import List, Dict, Any
import time
from config import OPENAI_API_KEY, OPENAI_EMBEDDING_MODEL, OPENAI_COMPLETION_MODEL

# Configure logging
logger = logging.getLogger(__name__)

class OpenAIClient:
    """OpenAI client for embeddings and completions"""
    
    def __init__(self):
        self.client = None
        self.last_request_time = 0
        self.min_request_interval = 0.05  # 50ms minimum between requests to avoid rate limits
    
    def connect(self):
        """Initialize OpenAI client"""
        try:
            self.client = OpenAI(api_key=OPENAI_API_KEY)
            logger.info("OpenAI client initialized")
        except Exception as e:
            logger.error(f"OpenAI client initialization error: {str(e)}")
            raise
    
    def _rate_limit(self):
        """Simple rate limiting to avoid OpenAI API rate limits"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        
        self.last_request_time = time.time()
    
    def get_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for text using OpenAI API
        
        Args:
            text: Text to embed
            
        Returns:
            List of embedding values
        """
        if not self.client:
            self.connect()
        
        self._rate_limit()
        
        try:
            response = self.client.embeddings.create(
                input=[text],
                model=OPENAI_EMBEDDING_MODEL
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"OpenAI embedding error: {str(e)}")
            raise
    
    async def get_embedding_async(self, text: str) -> List[float]:
        """
        Generate embedding for text using OpenAI API asynchronously
        
        Args:
            text: Text to embed
            
        Returns:
            List of embedding values
        """
        self._rate_limit()
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.openai.com/v1/embeddings",
                    headers={
                        "Authorization": f"Bearer {OPENAI_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "input": text,
                        "model": OPENAI_EMBEDDING_MODEL
                    },
                    timeout=30.0
                )
                result = response.json()
                return result["data"][0]["embedding"]
        except Exception as e:
            logger.error(f"OpenAI async embedding error: {str(e)}")
            raise
    
    def generate_answer(self, context: str, question: str) -> str:
        """
        Generate answer using OpenAI completion API
        
        Args:
            context: Retrieved context for the question
            question: User's question
            
        Returns:
            Generated answer
        """
        if not self.client:
            self.connect()
        
        self._rate_limit()
        
        try:
            messages = [
                {
                    "role": "system",
                    "content": "You are a financial analyst assistant. Answer questions based on the provided context."
                },
                {
                    "role": "user",
                    "content": f"Context:\n{context}\n\nQuestion:\n{question}"
                }
            ]
            
            response = self.client.chat.completions.create(
                model=OPENAI_COMPLETION_MODEL,
                messages=messages
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI completion error: {str(e)}")
            raise
    
    async def generate_answer_async(self, context: str, question: str) -> str:
        """
        Generate answer using OpenAI completion API asynchronously
        
        Args:
            context: Retrieved context for the question
            question: User's question
            
        Returns:
            Generated answer
        """
        if not self.client:
            self.connect()
        
        self._rate_limit()
        
        try:
            messages = [
                {
                    "role": "system",
                    "content": "You are a financial analyst assistant. Answer questions based on the provided context."
                },
                {
                    "role": "user",
                    "content": f"Context:\n{context}\n\nQuestion:\n{question}"
                }
            ]
            
            # Use asyncio to run the synchronous OpenAI client in a thread pool
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=OPENAI_COMPLETION_MODEL,
                messages=messages
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI async completion error: {str(e)}")
            raise

# Create an OpenAI client instance
openai_client = OpenAIClient() 