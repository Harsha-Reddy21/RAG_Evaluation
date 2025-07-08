# RAG Pipeline with Intent Detection - Implementation Summary

## Architecture Overview

This project implements a complete RAG (Retrieval-Augmented Generation) pipeline with intent detection for a customer support system. The system is designed to handle different types of customer queries by first detecting the intent, then retrieving relevant context, and finally generating appropriate responses.

### Backend (FastAPI)

The backend is built with FastAPI and consists of several key components:

1. **Intent Classification System**
   - Uses a pre-trained emotion classifier (DistilBERT) to categorize queries
   - Maps emotions to three intent categories: Technical Support, Billing, and Feature Requests

2. **LLM Router**
   - Manages communication with both local Ollama and OpenAI models
   - Implements automatic fallback from local to cloud model if needed
   - Supports both standard and streaming responses
   - Handles concurrent requests through a queue system

3. **RAG Engine**
   - Retrieves context based on detected intent
   - Builds specialized prompts for each intent type
   - Maintains a simple knowledge base (can be extended to vector DB)

4. **Evaluation Framework**
   - Measures intent classification accuracy
   - Calculates response relevance using semantic similarity
   - Tracks context utilization through word overlap
   - Monitors response latency
   - Provides comprehensive metrics for system performance

### Frontend (React)

The frontend is built with React and Material-UI, providing a clean and intuitive interface:

1. **Chat Interface**
   - Real-time conversation with the RAG system
   - Displays intent detection results and context used
   - Supports streaming responses
   - Toggle between OpenAI and local models

2. **Evaluation Dashboard**
   - Visualizes performance metrics
   - Allows running tests with configurable parameters
   - Shows intent distribution and accuracy

## Key Features

- **Intent-based Routing**: Different query types are handled with specialized prompts and context
- **Local-First Processing**: Uses Ollama for local inference with OpenAI fallback
- **Streaming Support**: Real-time response generation for better UX
- **Comprehensive Evaluation**: Multiple metrics to assess system performance
- **A/B Testing**: Compare local vs. cloud model performance

## Technical Highlights

1. **Modular Design**: Clean separation of concerns between components
2. **Async Processing**: Efficient handling of concurrent requests
3. **Error Handling**: Robust error recovery with fallback mechanisms
4. **Streaming Implementation**: Server-sent events for real-time responses
5. **Metrics Collection**: Detailed performance tracking for system evaluation

## Future Improvements

1. **Vector Database Integration**: Replace mock knowledge base with proper vector DB (e.g., Chroma, FAISS)
2. **Fine-tuning Intent Classifier**: Train a specialized intent classifier instead of using emotion mapping
3. **Enhanced Context Retrieval**: Implement semantic search for more relevant context
4. **User Feedback Loop**: Collect user feedback to improve responses over time
5. **Authentication & Multi-tenancy**: Add user accounts and organization-specific knowledge bases 