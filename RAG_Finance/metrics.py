import logging
import time
from typing import Dict, Any
from prometheus_client import Counter, Histogram, Gauge, start_http_server

# Configure logging
logger = logging.getLogger(__name__)

class MetricsManager:
    """Metrics manager for the financial RAG system"""
    
    def __init__(self):
        # Initialize Prometheus metrics
        self.query_counter = Counter(
            'financial_rag_queries_total', 
            'Total number of financial queries',
            ['company', 'cache_hit']
        )
        
        self.query_latency = Histogram(
            'financial_rag_query_latency_seconds',
            'Query latency in seconds',
            ['company', 'cache_hit'],
            buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0)
        )
        
        self.concurrent_requests = Gauge(
            'financial_rag_concurrent_requests',
            'Number of concurrent requests'
        )
        
        self.cache_size = Gauge(
            'financial_rag_cache_size',
            'Number of items in cache'
        )
        
        # Internal metrics tracking
        self.total_queries = 0
        self.cache_hits = 0
        self.cache_misses = 0
        self.start_time = time.time()
        
        logger.info("Metrics manager initialized")
    
    def start_metrics_server(self, port: int = 9090):
        """Start Prometheus metrics server"""
        try:
            start_http_server(port)
            logger.info(f"Metrics server started on port {port}")
        except Exception as e:
            logger.error(f"Failed to start metrics server: {str(e)}")
    
    def record_query(self, company: str, latency: float, cache_hit: bool):
        """
        Record a query in metrics
        
        Args:
            company: Company being queried
            latency: Query latency in seconds
            cache_hit: Whether the query was served from cache
        """
        # Update Prometheus metrics
        self.query_counter.labels(
            company=company,
            cache_hit=str(cache_hit)
        ).inc()
        
        self.query_latency.labels(
            company=company,
            cache_hit=str(cache_hit)
        ).observe(latency)
        
        # Update internal metrics
        self.total_queries += 1
        if cache_hit:
            self.cache_hits += 1
        else:
            self.cache_misses += 1
    
    def increment_concurrent(self):
        """Increment concurrent requests counter"""
        self.concurrent_requests.inc()
    
    def decrement_concurrent(self):
        """Decrement concurrent requests counter"""
        self.concurrent_requests.dec()
    
    def update_cache_size(self, size: int):
        """Update cache size gauge"""
        self.cache_size.set(size)
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """
        Get summary of metrics
        
        Returns:
            Dictionary with metrics summary
        """
        uptime = time.time() - self.start_time
        cache_hit_ratio = self.cache_hits / max(1, self.total_queries)
        
        return {
            "total_queries": self.total_queries,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "cache_hit_ratio": cache_hit_ratio,
            "uptime_seconds": uptime,
            "queries_per_second": self.total_queries / max(1, uptime)
        }

# Create a metrics manager instance
metrics = MetricsManager() 