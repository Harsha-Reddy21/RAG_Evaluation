import requests
import time
import os
import json
from typing import Dict, Tuple, List, Optional, Generator
import openai
from dotenv import load_dotenv
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Request queue for handling concurrent requests
request_queue = asyncio.Queue()
MAX_CONCURRENT_REQUESTS = 3  # Adjust based on your system's capacity
executor = ThreadPoolExecutor(max_workers=MAX_CONCURRENT_REQUESTS)

class LLMRouter:
    def __init__(self, use_openai=False, model="llama3"):
        """
        Initialize the LLM router
        
        Args:
            use_openai: Whether to use OpenAI (True) or local Ollama (False)
            model: Model name to use with Ollama
        """
        self.use_openai = use_openai
        self.local_model = model
        self.openai_model = "gpt-4o-mini"  # Default OpenAI model
        self.ollama_base_url = "http://localhost:11434/api"
        
    def query(self, prompt: str) -> Tuple[str, float]:
        """
        Send a query to the LLM and get the response
        
        Args:
            prompt: The prompt to send to the LLM
            
        Returns:
            Tuple of (response text, latency in seconds)
        """
        try:
            if self.use_openai:
                return self._query_openai(prompt)
            else:
                return self._query_ollama(prompt)
        except Exception as e:
            print(f"Error querying LLM: {e}")
            # Fallback to OpenAI if local model fails
            if not self.use_openai:
                print("Falling back to OpenAI")
                self.use_openai = True
                return self.query(prompt)
            return f"Error generating response: {str(e)}", 0.0
    
    def _query_openai(self, prompt: str) -> Tuple[str, float]:
        """Query OpenAI API"""
        start = time.time()
        try:
            response = openai.chat.completions.create(
                model=self.openai_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
            )
            latency = time.time() - start
            return response.choices[0].message.content.strip(), latency
        except Exception as e:
            print(f"OpenAI API error: {e}")
            latency = time.time() - start
            raise e
    
    def _query_ollama(self, prompt: str) -> Tuple[str, float]:
        """Query local Ollama instance"""
        start = time.time()
        try:
            res = requests.post(
                f"{self.ollama_base_url}/generate", 
                json={
                    "model": self.local_model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=60
            )
            res.raise_for_status()
            latency = time.time() - start
            return res.json()['response'], latency
        except requests.exceptions.RequestException as e:
            print(f"Ollama API error: {e}")
            latency = time.time() - start
            raise e
    
    async def query_stream(self, prompt: str) -> Generator[str, None, None]:
        """
        Stream responses from the LLM
        
        Args:
            prompt: The prompt to send to the LLM
            
        Yields:
            Chunks of the response as they become available
        """
        try:
            if self.use_openai:
                async for chunk in self._stream_openai(prompt):
                    yield chunk
            else:
                async for chunk in self._stream_ollama(prompt):
                    yield chunk
        except Exception as e:
            print(f"Error streaming from LLM: {e}")
            # Fallback to OpenAI if local model fails
            if not self.use_openai:
                print("Falling back to OpenAI for streaming")
                self.use_openai = True
                async for chunk in self.query_stream(prompt):
                    yield chunk
            else:
                yield f"Error generating response: {str(e)}"
    
    async def _stream_openai(self, prompt: str) -> Generator[str, None, None]:
        """Stream from OpenAI API"""
        try:
            response = await asyncio.get_event_loop().run_in_executor(
                executor,
                lambda: openai.chat.completions.create(
                    model=self.openai_model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    stream=True
                )
            )
            
            for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            print(f"OpenAI streaming error: {e}")
            raise e
    
    async def _stream_ollama(self, prompt: str) -> Generator[str, None, None]:
        """Stream from local Ollama instance"""
        try:
            response = requests.post(
                f"{self.ollama_base_url}/generate",
                json={
                    "model": self.local_model,
                    "prompt": prompt,
                    "stream": True
                },
                stream=True,
                timeout=60
            )
            
            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    if "response" in data:
                        yield data["response"]
        except Exception as e:
            print(f"Ollama streaming error: {e}")
            raise e

# Queue processor for handling concurrent requests
async def process_queue():
    """Process requests from the queue"""
    while True:
        task = await request_queue.get()
        try:
            await task
        except Exception as e:
            print(f"Error processing task: {e}")
        finally:
            request_queue.task_done()

# Start queue processor
async def start_queue_processor():
    """Start the queue processor"""
    for _ in range(MAX_CONCURRENT_REQUESTS):
        asyncio.create_task(process_queue()) 