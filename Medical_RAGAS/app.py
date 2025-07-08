import os
from fastapi import FastAPI, HTTPException, BackgroundTasks, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn
import time
from datetime import datetime
import json

# RAG components
from rag_system import (
    extract_text_from_pdf,
    process_document,
    ask_medical_question,
    evaluate_response
)

# Initialize FastAPI app
app = FastAPI(title="Medical Knowledge Assistant API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class QueryRequest(BaseModel):
    query: str
    evaluation: bool = True

class QueryResponse(BaseModel):
    query: str
    answer: str
    sources: List[str]
    evaluation_metrics: Optional[Dict[str, float]] = None
    latency: float

class DocumentUpload(BaseModel):
    success: bool
    filename: str
    message: str

# Metrics storage
metrics_history = []

@app.get("/")
async def root():
    return {"message": "Medical Knowledge Assistant API"}

@app.post("/query", response_model=QueryResponse)
async def query_endpoint(request: QueryRequest, background_tasks: BackgroundTasks):
    start_time = time.time()
    
    try:
        # Get answer from RAG system
        answer, source_docs = ask_medical_question(request.query)
        
        # Extract source content for response
        sources = [doc.page_content for doc in source_docs]
        
        # Calculate latency
        latency = time.time() - start_time
        
        # Prepare response
        response = {
            "query": request.query,
            "answer": answer,
            "sources": sources,
            "latency": latency,
            "evaluation_metrics": None
        }
        
        # Run evaluation in background if requested
        if request.evaluation:
            # For demo, evaluate immediately, but in production this could be a background task
            metrics = evaluate_response(request.query, answer, sources)
            response["evaluation_metrics"] = metrics
            
            # Store metrics for monitoring
            metrics_entry = {
                "timestamp": datetime.now().isoformat(),
                "query": request.query,
                "metrics": metrics,
                "latency": latency
            }
            metrics_history.append(metrics_entry)
            
            # Safety check based on faithfulness threshold
            if metrics["faithfulness"] < 0.90:
                response["answer"] = "I cannot provide a reliable answer to this question based on the available information."
        
        return response
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload", response_model=DocumentUpload)
async def upload_document(file: UploadFile = File(...)):
    try:
        # Save the uploaded file temporarily
        file_location = f"uploads/{file.filename}"
        os.makedirs("uploads", exist_ok=True)
        
        with open(file_location, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Process the document
        if file.filename.endswith('.pdf'):
            text = extract_text_from_pdf(file_location)
            process_document(text, file.filename)
            return {"success": True, "filename": file.filename, "message": "PDF processed successfully"}
        else:
            return {"success": False, "filename": file.filename, "message": "Unsupported file format"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics")
async def get_metrics():
    return {"metrics_history": metrics_history}

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True) 