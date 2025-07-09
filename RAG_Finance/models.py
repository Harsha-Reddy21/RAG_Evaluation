from sqlalchemy import Column, Integer, String, DateTime, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

# Database models
Base = declarative_base()

class FinancialReport(Base):
    """SQLAlchemy model for financial reports"""
    __tablename__ = "financial_reports"
    
    id = Column(Integer, primary_key=True)
    company = Column(String(100), index=True)
    report_type = Column(String(100))
    report_date = Column(DateTime)
    section = Column(String(100))
    content = Column(Text)
    embedding_id = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)

class QueryMetrics(Base):
    """SQLAlchemy model for tracking query metrics"""
    __tablename__ = "query_metrics"
    
    id = Column(Integer, primary_key=True)
    query_text = Column(Text)
    company = Column(String(100))
    latency_seconds = Column(Float)
    cache_hit = Column(Integer)  # 0 for miss, 1 for hit
    timestamp = Column(DateTime, default=datetime.utcnow)
    api_key = Column(String(100))

# API Request/Response models
class QueryRequest(BaseModel):
    """Request schema for financial queries"""
    company: str = Field(..., description="Company name to query about")
    question: str = Field(..., description="Question about the company's financials")
    api_key: str = Field(..., description="API key for authentication and rate limiting")

class DocumentRequest(BaseModel):
    """Request schema for document ingestion"""
    company: str = Field(..., description="Company name")
    report_type: str = Field(..., description="Type of report (Annual Report, Quarterly Earnings, etc.)")
    report_date: str = Field(..., description="Date of the report (YYYY-MM-DD)")
    section: str = Field(..., description="Section of the report (Revenue, Cash Flow, etc.)")
    content: str = Field(..., description="Content of the report section")
    api_key: str = Field(..., description="API key for authentication and rate limiting")

class QueryResponse(BaseModel):
    """Response schema for financial queries"""
    answer: str = Field(..., description="Answer to the financial question")
    source: str = Field(..., description="Source of the answer (cache or generated)")
    latency_seconds: float = Field(..., description="Time taken to generate the answer")
    
class MetricsResponse(BaseModel):
    """Response schema for system metrics"""
    query_count: int
    cache_hit_ratio: float
    concurrent_requests: int
    average_latency: float
    cache_size: Optional[int] = None 