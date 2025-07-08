import os
import time
import json
import asyncio
from typing import Dict, List, Optional, Any
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from .intent_classifier import init_classifier, detect_intent
from .llm_router import LLMRouter, start_queue_processor
from .rag_engine import retrieve_context, build_prompt, save_query_data
from .evaluation import relevance_score, context_utilization_score, calculate_metrics, generate_test_set

# Initialize FastAPI app
app = FastAPI(title="RAG Pipeline with Intent Detection")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
intent_classifier = init_classifier()
llm_router_local = LLMRouter(use_openai=False)
llm_router_openai = LLMRouter(use_openai=True)

# Create data directory
data_dir = Path("./data")
data_dir.mkdir(exist_ok=True)

# Request models
class QueryRequest(BaseModel):
    query: str
    use_openai: bool = False
    true_intent: Optional[str] = None  # For evaluation purposes

class TestRequest(BaseModel):
    num_samples: int = 5
    use_openai: bool = False

class EvaluationResponse(BaseModel):
    metrics: Dict[str, Any]

# Response models
class QueryResponse(BaseModel):
    query: str
    intent: str
    confidence: float
    response: str
    latency: float
    context: List[str]
    relevance: Optional[float] = None
    context_utilization: Optional[float] = None

@app.on_event("startup")
async def startup_event():
    """Initialize components on startup"""
    # Start the queue processor
    asyncio.create_task(start_queue_processor())

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "RAG Pipeline with Intent Detection API"}

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """
    Process a user query
    
    Args:
        request: QueryRequest object containing the query
        
    Returns:
        QueryResponse object containing the response
    """
    try:
        # 1. Detect intent
        if intent_classifier is None:
            raise HTTPException(status_code=500, detail="Intent classifier not initialized")
        
        intent, confidence = detect_intent(request.query, intent_classifier)
        
        # 2. Retrieve context
        context = retrieve_context(intent, request.query)
        
        # 3. Build prompt
        prompt = build_prompt(intent, request.query, context)
        
        # 4. Generate response
        llm_router = llm_router_openai if request.use_openai else llm_router_local
        response, latency = llm_router.query(prompt)
        
        # 5. Calculate metrics if true intent is provided
        relevance = None
        context_utilization = None
        
        # 6. Create response
        query_response = {
            "query": request.query,
            "intent": intent,
            "confidence": confidence,
            "response": response,
            "latency": latency,
            "context": context,
            "relevance": relevance,
            "context_utilization": context_utilization
        }
        
        # 7. Save query data for evaluation if true intent is provided
        if request.true_intent:
            # Calculate metrics
            context_util = context_utilization_score(response, context)
            
            # Save query data
            query_data = {
                "query": request.query,
                "true_intent": request.true_intent,
                "predicted_intent": intent,
                "confidence": confidence,
                "response": response,
                "context": context,
                "latency": latency,
                "context_utilization": context_util,
                "timestamp": time.time(),
                "model": "openai" if request.use_openai else "local"
            }
            
            save_query_data(query_data)
            
            # Update response
            query_response["context_utilization"] = context_util
        
        return query_response
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@app.post("/query/stream")
async def stream_query(request: QueryRequest):
    """
    Stream a response to a user query
    
    Args:
        request: QueryRequest object containing the query
        
    Returns:
        StreamingResponse object
    """
    try:
        # 1. Detect intent
        if intent_classifier is None:
            raise HTTPException(status_code=500, detail="Intent classifier not initialized")
        
        intent, confidence = detect_intent(request.query, intent_classifier)
        
        # 2. Retrieve context
        context = retrieve_context(intent, request.query)
        
        # 3. Build prompt
        prompt = build_prompt(intent, request.query, context)
        
        # 4. Stream response
        llm_router = llm_router_openai if request.use_openai else llm_router_local
        
        async def generate():
            start_time = time.time()
            full_response = ""
            
            # Send metadata first
            metadata = {
                "type": "metadata",
                "intent": intent,
                "confidence": confidence,
                "context": context
            }
            yield f"data: {json.dumps(metadata)}\n\n"
            
            async for chunk in llm_router.query_stream(prompt):
                full_response += chunk
                yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"
            
            # Send completion message
            latency = time.time() - start_time
            context_util = context_utilization_score(full_response, context)
            
            completion = {
                "type": "completion",
                "latency": latency,
                "context_utilization": context_util
            }
            yield f"data: {json.dumps(completion)}\n\n"
            
            # Save query data if true intent is provided
            if request.true_intent:
                query_data = {
                    "query": request.query,
                    "true_intent": request.true_intent,
                    "predicted_intent": intent,
                    "confidence": confidence,
                    "response": full_response,
                    "context": context,
                    "latency": latency,
                    "context_utilization": context_util,
                    "timestamp": time.time(),
                    "model": "openai" if request.use_openai else "local"
                }
                
                save_query_data(query_data)
        
        return StreamingResponse(generate(), media_type="text/event-stream")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error streaming response: {str(e)}")

@app.post("/test", response_model=EvaluationResponse)
async def run_test(request: TestRequest, background_tasks: BackgroundTasks):
    """
    Run tests on the RAG pipeline
    
    Args:
        request: TestRequest object containing test parameters
        background_tasks: FastAPI BackgroundTasks object
        
    Returns:
        EvaluationResponse object containing metrics
    """
    try:
        # Get test set
        test_set = generate_test_set()
        
        # Limit number of samples if requested
        if request.num_samples < len(test_set):
            test_set = test_set[:request.num_samples]
        
        # Run tests in background
        background_tasks.add_task(run_tests_background, test_set, request.use_openai)
        
        # Return current metrics
        metrics = calculate_metrics()
        
        return {"metrics": metrics}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running tests: {str(e)}")

@app.get("/metrics", response_model=EvaluationResponse)
async def get_metrics():
    """
    Get evaluation metrics
    
    Returns:
        EvaluationResponse object containing metrics
    """
    try:
        metrics = calculate_metrics()
        return {"metrics": metrics}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting metrics: {str(e)}")

async def run_tests_background(test_set: List[Dict], use_openai: bool):
    """
    Run tests in background
    
    Args:
        test_set: List of test queries
        use_openai: Whether to use OpenAI
    """
    llm_router = llm_router_openai if use_openai else llm_router_local
    
    for test in test_set:
        try:
            # 1. Detect intent
            intent, confidence = detect_intent(test["query"], intent_classifier)
            
            # 2. Retrieve context
            context = retrieve_context(intent, test["query"])
            
            # 3. Build prompt
            prompt = build_prompt(intent, test["query"], context)
            
            # 4. Generate response
            response, latency = llm_router.query(prompt)
            
            # 5. Calculate metrics
            rel_score = relevance_score(response, test["ideal_answer"])
            context_util = context_utilization_score(response, context)
            
            # 6. Save query data
            query_data = {
                "query": test["query"],
                "true_intent": test["true_intent"],
                "predicted_intent": intent,
                "confidence": confidence,
                "response": response,
                "context": context,
                "latency": latency,
                "relevance": rel_score,
                "context_utilization": context_util,
                "timestamp": time.time(),
                "model": "openai" if use_openai else "local"
            }
            
            save_query_data(query_data)
            
            # Sleep to avoid overwhelming the LLM API
            await asyncio.sleep(1)
            
        except Exception as e:
            print(f"Error running test: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 