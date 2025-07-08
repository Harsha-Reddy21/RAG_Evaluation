# RAG Pipeline with Intent Detection

A customer support system for a SaaS company that handles different query types (technical issues, billing questions, feature requests) with tailored processing strategies.

## Features

- Local LLM setup with Ollama and OpenAI fallback
- Intent detection system for three categories:
  - Technical Support: Routes to code examples and documentation
  - Billing/Account: Routes to pricing tables and policies
  - Feature Requests: Routes to roadmap and comparison data
- Evaluation framework with metrics:
  - Intent classification accuracy
  - Response relevance (cosine similarity)
  - Context utilization score
  - Response time
- React frontend with chat interface and evaluation dashboard
- FastAPI backend with streaming support

## Setup Instructions

### Prerequisites

- Python 3.8+
- Node.js 14+
- [Ollama](https://ollama.ai/) installed locally with the `llama3` model

### Backend Setup

1. Navigate to the backend directory:
   ```
   cd backend
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`

4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

5. Create a `.env` file from the example:
   ```
   cp .env.example .env
   ```

6. Edit the `.env` file and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your-openai-api-key
   ```

7. Run the backend:
   ```
   python run.py
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Start the development server:
   ```
   npm start
   ```

4. Open your browser and navigate to [http://localhost:3000](http://localhost:3000)

## Usage

### Chat Interface

1. Enter a query in the chat interface
2. Toggle between OpenAI and local Ollama model
3. Enable/disable streaming responses
4. View intent detection results and context used

### Evaluation Dashboard

1. Run tests with configurable number of samples
2. View metrics on intent accuracy, relevance, context utilization, and latency
3. Analyze intent distribution

## Sample Test Queries

### Technical Support

- "How do I reset my password?"
- "What are the API rate limits?"
- "How do I set up OAuth integration?"

### Billing

- "What are your pricing tiers?"
- "What happens if I miss a payment?"
- "How do I get a refund?"

### Feature Requests

- "When will you add two-factor authentication?"
- "Can you integrate with Slack?"
- "Will there be a mobile app?" 