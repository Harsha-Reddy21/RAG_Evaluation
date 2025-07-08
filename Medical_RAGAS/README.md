# Medical Knowledge Assistant RAG System

A production-ready Medical Knowledge Assistant RAG (Retrieval-Augmented Generation) pipeline for healthcare professionals to query medical literature, drug interactions, and clinical guidelines using OpenAI API with a comprehensive RAGAS evaluation framework.

## Features

- **RAG Pipeline**: Medical document ingestion → Vector DB → Retrieval → OpenAI generation
- **RAGAS Evaluation**: Context Precision, Context Recall, Faithfulness, Answer Relevancy
- **Safety System**: RAGAS-validated response filtering (Faithfulness >0.90, Context Precision >0.85)
- **Monitoring Dashboard**: Real-time RAGAS metrics tracking
- **Performance**: Response latency p95 < 3 seconds

## Tech Stack

- **Backend**: FastAPI
- **Frontend**: React with Material-UI
- **Vector Database**: FAISS
- **LLM**: OpenAI GPT-4
- **Embeddings**: OpenAI text-embedding-3-small
- **Evaluation**: RAGAS metrics
- **Deployment**: Docker and Docker Compose

## Getting Started

### Prerequisites

- Docker and Docker Compose
- OpenAI API key

### Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/medical-knowledge-assistant.git
   cd medical-knowledge-assistant
   ```

2. Create a `.env` file with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

3. Build and run the application with Docker Compose:
   ```
   docker-compose up --build
   ```

4. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Manual Setup (without Docker)

#### Backend

1. Create a virtual environment and install dependencies:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Run the FastAPI server:
   ```
   uvicorn app:app --reload
   ```

#### Frontend

1. Navigate to the frontend directory and install dependencies:
   ```
   cd frontend
   npm install
   ```

2. Run the React development server:
   ```
   npm start
   ```

## Usage

1. **Upload Medical Documents**: Use the upload section to add medical PDFs to the knowledge base.

2. **Ask Medical Questions**: Enter your medical query in the search box and get AI-generated answers with source references.

3. **View RAGAS Metrics**: Each answer is evaluated with RAGAS metrics to ensure accuracy and relevance.

4. **Monitor Performance**: Use the metrics dashboard to track system performance over time.

## RAGAS Evaluation

The system uses the following RAGAS metrics:

- **Context Precision**: Measures how much of the retrieved context is actually relevant to the question.
- **Context Recall**: Measures how much of the relevant information is retrieved.
- **Faithfulness**: Measures how accurately the generated answer reflects the retrieved context.
- **Answer Relevancy**: Measures how relevant the answer is to the question.

## Safety Thresholds

The system enforces the following quality thresholds:

- Faithfulness > 0.90
- Context Precision > 0.85

If an answer doesn't meet these thresholds, the system will not provide the answer and will indicate that it cannot provide a reliable response.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 