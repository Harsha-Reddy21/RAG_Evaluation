# Financial RAG System

A production-scale Financial Intelligence RAG (Retrieval-Augmented Generation) System for handling concurrent queries on corporate financial reports and earnings data with Redis caching and OpenAI API integration.

## 🚀 Features

- **RAG Pipeline**: Document ingestion → Vector DB → Retrieval → OpenAI generation
- **Concurrent Processing**: Handle 100+ concurrent requests with <2s response time
- **Smart Caching**: Redis-based caching with different TTLs for real-time vs historical data
- **Rate Limiting**: Per-API key rate limiting
- **Monitoring**: Real-time metrics with Prometheus and Grafana
- **Scalable Architecture**: Modular design with async support and connection pooling

## 📋 Prerequisites

- Python 3.10+ (or Python 3.12 with updated dependencies)
- Docker and Docker Compose (recommended)
- OpenAI API key
- Pinecone API key
- PostgreSQL database
- Redis server

## 🛠️ Installation

### Option 1: Docker (Recommended)

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd financial-rag-system
   ```

2. **Set up environment variables**:
   Create a `.env` file in the root directory:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   PINECONE_API_KEY=your_pinecone_api_key_here
   ```

3. **Start the services**:
   ```bash
   docker-compose up -d
   ```

   This will start:
   - Financial RAG API on port 8000
   - PostgreSQL database
   - Redis cache
   - Prometheus metrics on port 9090
   - Grafana dashboards on port 3000

### Option 2: Local Development

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables**:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   PINECONE_API_KEY=your_pinecone_api_key_here
   DATABASE_URL=postgresql://postgres:password@localhost:5432/finance_db
   REDIS_HOST=localhost
   REDIS_PORT=6379
   ```

3. **Start PostgreSQL and Redis**:
   ```bash
   # Using Docker
   docker run -d --name postgres -p 5432:5432 -e POSTGRES_PASSWORD=password -e POSTGRES_DB=finance_db postgres:14
   docker run -d --name redis -p 6379:6379 redis:7
   ```

4. **Run the application**:
   ```bash
   python main.py
   ```

## 📚 API Endpoints

### Health Check
```http
GET /health
```

### Query Financial Data
```http
POST /query
Content-Type: application/json

{
  "company": "Apple",
  "question": "What was the revenue trend over the last 3 years?",
  "api_key": "your_api_key"
}
```

### Ingest Document
```http
POST /ingest
Content-Type: application/json

{
  "company": "Apple",
  "report_type": "Annual Report",
  "report_date": "2023-12-31",
  "section": "Revenue",
  "content": "Apple's revenue for FY2023 was $394.3 billion...",
  "api_key": "your_api_key"
}
```

### Batch Document Ingestion
```http
POST /ingest/batch
Content-Type: application/json

[
  {
    "company": "Apple",
    "report_type": "Annual Report",
    "report_date": "2023-12-31",
    "section": "Revenue",
    "content": "Apple's revenue for FY2023 was $394.3 billion...",
    "api_key": "your_api_key"
  }
]
```

### Get Metrics
```http
GET /metrics
```

### Rate Limit Status
```http
GET /rate-limit?api_key=your_api_key
```

## 🧪 Load Testing

Run load tests to validate system performance:

```bash
# Basic load test
python load_test.py

# Custom load test
python load_test.py --users 200 --duration 600 --url http://localhost:8000
```

### Load Test Parameters:
- `--users`: Number of concurrent users (default: 200)
- `--duration`: Test duration in seconds (default: 600)
- `--url`: API base URL (default: http://localhost:8000)
- `--api-key`: API key prefix (default: test_api_key_12345)

## 📊 Monitoring

### Prometheus Metrics
- Access metrics at: http://localhost:9090
- Key metrics:
  - `financial_rag_queries_total`: Total number of queries
  - `financial_rag_query_latency_seconds`: Query latency
  - `financial_rag_cache_hit_ratio`: Cache hit ratio
  - `financial_rag_concurrent_requests`: Concurrent requests

### Grafana Dashboards
- Access at: http://localhost:3000
- Default credentials: admin/admin
- Pre-configured dashboards for:
  - Query performance
  - Cache efficiency
  - System health

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI App   │    │   Redis Cache   │    │  PostgreSQL DB  │
│                 │    │                 │    │                 │
│ - Query Endpoint│◄──►│ - Smart TTL     │    │ - Financial     │
│ - Rate Limiting │    │ - Hit Tracking  │    │   Reports       │
│ - Background    │    │ - LRU Eviction  │    │ - Query Metrics │
│   Tasks         │    └─────────────────┘    └─────────────────┘
└─────────────────┘
         │
         ▼
┌─────────────────┐    ┌─────────────────┐
│  Pinecone       │    │   OpenAI        │
│  Vector Store   │    │                 │
│                 │    │ - Embeddings    │
│ - Document      │◄──►│ - Completions   │
│   Storage       │    │ - Rate Limiting │
│ - Similarity    │    └─────────────────┘
│   Search        │
└─────────────────┘
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | Required |
| `PINECONE_API_KEY` | Pinecone API key | Required |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://postgres:12345678@localhost:5432/finance_db` |
| `REDIS_HOST` | Redis host | `localhost` |
| `REDIS_PORT` | Redis port | `6379` |
| `API_HOST` | API host | `0.0.0.0` |
| `API_PORT` | API port | `8000` |
| `API_WORKERS` | Number of workers | `4` |

### Cache Configuration

- **Real-time data**: 1 hour TTL
- **Historical data**: 24 hours TTL
- **Cache hit ratio target**: >70%

### Rate Limiting

- **Default**: 100 requests per minute per API key
- **Configurable** via environment variables

## 📁 Project Structure

```
financial-rag-system/
├── api.py                 # FastAPI application
├── config.py              # Configuration management
├── models.py              # Database models and schemas
├── database.py            # Database connection management
├── cache.py               # Redis cache management
├── vector_store.py        # Pinecone vector store
├── llm.py                 # OpenAI client
├── rate_limiter.py        # Rate limiting logic
├── metrics.py             # Prometheus metrics
├── rag_pipeline.py        # Core RAG pipeline
├── document_processor.py  # Document ingestion
├── load_test.py           # Load testing script
├── main.py                # Application entry point
├── requirements.txt       # Python dependencies
├── docker-compose.yml     # Docker services
├── Dockerfile             # Application container
├── prometheus.yml         # Prometheus configuration
└── README.md              # This file
```

## 🚀 Performance Targets

- **Concurrent Requests**: 100+ users
- **Response Time**: <2 seconds
- **Cache Hit Ratio**: >70%
- **Uptime**: 99.9%

## 🔍 Troubleshooting

### Common Issues

1. **Import Errors**: Make sure all dependencies are installed
   ```bash
   pip install -r requirements.txt
   ```

2. **Connection Errors**: Check if PostgreSQL and Redis are running
   ```bash
   docker ps
   ```

3. **API Key Errors**: Verify your OpenAI and Pinecone API keys in `.env`

4. **Rate Limiting**: Check your API usage limits

### Logs

Check application logs:
```bash
# Docker
docker-compose logs api

# Local
tail -f logs/app.log
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review the API documentation at http://localhost:8000/docs

## 🔄 Updates

To update the system:
```bash
# Docker
docker-compose pull
docker-compose up -d

# Local
pip install -r requirements.txt --upgrade
``` 