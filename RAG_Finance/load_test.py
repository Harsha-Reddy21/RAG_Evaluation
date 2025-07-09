import asyncio
import time
import aiohttp
import random
import statistics
from tqdm import tqdm
import argparse
import json
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

# Test configuration defaults
DEFAULT_BASE_URL = "http://localhost:8000"
DEFAULT_API_KEY = "test_api_key_12345"
DEFAULT_CONCURRENT_USERS = 200
DEFAULT_TEST_DURATION_SECONDS = 600  # 10 minutes
DEFAULT_RAMP_UP_TIME = 60  # 60 seconds to ramp up to full load

# Test data
COMPANIES = ["Apple", "Microsoft", "Google", "Amazon", "Tesla", "Facebook", "Netflix", "IBM", "Intel", "Oracle"]

QUESTIONS = [
    "What was the revenue trend over the last 3 years?",
    "What is the current profit margin?",
    "How has the cash flow changed since last quarter?",
    "What were the major expenses in the latest annual report?",
    "What is the debt-to-equity ratio?",
    "How does the company's performance compare to industry averages?",
    "What are the key risk factors mentioned in recent reports?",
    "What is the projected growth for next year?",
    "How much did R&D spending increase year-over-year?",
    "What is the dividend payout ratio?",
    "What was mentioned about sustainability initiatives in recent reports?",
    "How has the company's market share changed?",
    "What acquisitions did the company make recently?",
    "How much cash reserves does the company have?",
    "What is the company's strategy for international expansion?"
]

class LoadTest:
    """Load testing class for Financial RAG API"""
    
    def __init__(self, base_url, api_key, concurrent_users, duration_seconds, ramp_up_time):
        self.base_url = base_url
        self.api_key = api_key
        self.concurrent_users = concurrent_users
        self.duration_seconds = duration_seconds
        self.ramp_up_time = ramp_up_time
        
        # Results storage
        self.results = []
        self.start_time = None
        self.end_time = None
        
        # Progress bar
        self.progress_bar = None
    
    async def send_query(self, session, user_id):
        """Send a query to the API"""
        company = random.choice(COMPANIES)
        question = random.choice(QUESTIONS)
        
        start_time = time.time()
        try:
            async with session.post(
                f"{self.base_url}/query",
                json={
                    "company": company,
                    "question": question,
                    "api_key": f"{self.api_key}_{user_id}"
                },
                timeout=30
            ) as response:
                result = await response.json()
                latency = time.time() - start_time
                return {
                    "success": response.status == 200,
                    "latency": latency,
                    "status": response.status,
                    "company": company,
                    "question": question,
                    "timestamp": time.time(),
                    "cache_hit": result.get("source") == "cache"
                }
        except Exception as e:
            return {
                "success": False,
                "latency": time.time() - start_time,
                "error": str(e),
                "company": company,
                "question": question,
                "timestamp": time.time(),
                "cache_hit": False
            }
    
    async def user_behavior(self, user_id):
        """Simulate user behavior"""
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            queries = 0
            
            # Calculate delay for ramp-up
            if self.ramp_up_time > 0:
                delay = (user_id / self.concurrent_users) * self.ramp_up_time
                await asyncio.sleep(delay)
            
            while time.time() - start_time < self.duration_seconds:
                result = await self.send_query(session, user_id)
                self.results.append(result)
                queries += 1
                
                # Update progress bar
                if self.progress_bar:
                    self.progress_bar.update(1)
                
                # Random think time between queries (0.5-3 seconds)
                await asyncio.sleep(random.uniform(0.5, 3))
    
    async def run_test(self):
        """Run the load test"""
        print(f"Starting load test with {self.concurrent_users} concurrent users for {self.duration_seconds} seconds")
        print(f"Base URL: {self.base_url}")
        
        # Check if API is available
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/health") as response:
                    if response.status != 200:
                        print(f"API health check failed with status {response.status}")
                        return
                    print("API health check successful")
        except Exception as e:
            print(f"API health check failed: {str(e)}")
            return
        
        # Estimate total queries
        total_estimated_queries = int(self.concurrent_users * self.duration_seconds / 2)
        
        self.start_time = time.time()
        
        # Create progress bar
        with tqdm(total=total_estimated_queries, desc="Queries") as self.progress_bar:
            # Create tasks for each user
            tasks = [self.user_behavior(i) for i in range(self.concurrent_users)]
            await asyncio.gather(*tasks)
        
        self.end_time = time.time()
        
        # Analyze and report results
        self.analyze_results()
    
    def analyze_results(self):
        """Analyze test results"""
        if not self.results:
            print("No results to analyze")
            return
        
        total_duration = self.end_time - self.start_time
        total_queries = len(self.results)
        queries_per_second = total_queries / total_duration
        
        successful = [r for r in self.results if r.get("success")]
        failed = [r for r in self.results if not r.get("success")]
        
        cache_hits = [r for r in self.results if r.get("cache_hit")]
        cache_misses = [r for r in self.results if not r.get("cache_hit") and r.get("success")]
        
        latencies = [r["latency"] for r in successful]
        
        # Print summary
        print("\n" + "="*50)
        print("LOAD TEST RESULTS")
        print("="*50)
        print(f"Test duration: {total_duration:.2f} seconds")
        print(f"Total queries: {total_queries}")
        print(f"Queries per second: {queries_per_second:.2f}")
        print(f"Successful: {len(successful)} ({len(successful)/total_queries*100:.2f}%)")
        print(f"Failed: {len(failed)} ({len(failed)/total_queries*100:.2f}%)")
        
        if cache_hits or cache_misses:
            cache_hit_ratio = len(cache_hits) / (len(cache_hits) + len(cache_misses)) if (len(cache_hits) + len(cache_misses)) > 0 else 0
            print(f"Cache hits: {len(cache_hits)} ({cache_hit_ratio*100:.2f}%)")
        
        if latencies:
            print("\nLatency (seconds):")
            print(f"  Min: {min(latencies):.3f}")
            print(f"  Max: {max(latencies):.3f}")
            print(f"  Avg: {statistics.mean(latencies):.3f}")
            print(f"  Median: {statistics.median(latencies):.3f}")
            print(f"  95th percentile: {sorted(latencies)[int(len(latencies)*0.95)]:.3f}")
            
            # Check if meeting SLA
            under_2s = sum(1 for l in latencies if l < 2.0)
            print(f"Queries under 2s: {under_2s} ({under_2s/len(latencies)*100:.2f}%)")
        
        # Get final metrics from API
        asyncio.run(self.get_final_metrics())
        
        # Save results to file
        self.save_results()
        
        # Generate charts
        self.generate_charts()
    
    async def get_final_metrics(self):
        """Get final metrics from API"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/metrics") as response:
                    if response.status == 200:
                        metrics = await response.json()
                        print("\nSystem Metrics:")
                        for key, value in metrics.items():
                            print(f"  {key}: {value}")
        except Exception as e:
            print(f"Failed to get system metrics: {str(e)}")
    
    def save_results(self):
        """Save test results to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"load_test_results_{timestamp}.json"
        
        # Prepare results summary
        summary = {
            "test_config": {
                "base_url": self.base_url,
                "concurrent_users": self.concurrent_users,
                "duration_seconds": self.duration_seconds,
                "ramp_up_time": self.ramp_up_time
            },
            "results": {
                "total_queries": len(self.results),
                "successful_queries": sum(1 for r in self.results if r.get("success")),
                "failed_queries": sum(1 for r in self.results if not r.get("success")),
                "cache_hits": sum(1 for r in self.results if r.get("cache_hit")),
                "start_time": self.start_time,
                "end_time": self.end_time,
                "total_duration": self.end_time - self.start_time
            },
            "latency_stats": {},
            "detailed_results": self.results
        }
        
        # Add latency statistics
        latencies = [r["latency"] for r in self.results if r.get("success")]
        if latencies:
            summary["latency_stats"] = {
                "min": min(latencies),
                "max": max(latencies),
                "mean": statistics.mean(latencies),
                "median": statistics.median(latencies),
                "p95": sorted(latencies)[int(len(latencies)*0.95)],
                "p99": sorted(latencies)[int(len(latencies)*0.99)],
                "under_2s_percentage": sum(1 for l in latencies if l < 2.0) / len(latencies)
            }
        
        # Save to file
        with open(filename, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\nResults saved to {filename}")
    
    def generate_charts(self):
        """Generate charts from test results"""
        if not self.results:
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Filter successful requests
        successful = [r for r in self.results if r.get("success")]
        if not successful:
            print("No successful requests to plot")
            return
        
        # Extract timestamps and latencies
        timestamps = [r["timestamp"] - self.start_time for r in successful]
        latencies = [r["latency"] for r in successful]
        cache_hits = [r.get("cache_hit", False) for r in successful]
        
        # Create figure with subplots
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 15))
        
        # Plot 1: Latency over time
        ax1.scatter(timestamps, latencies, alpha=0.5, c=['green' if hit else 'blue' for hit in cache_hits])
        ax1.set_title('Latency over Time')
        ax1.set_xlabel('Time (seconds)')
        ax1.set_ylabel('Latency (seconds)')
        ax1.grid(True)
        
        # Add horizontal line at 2s for SLA
        ax1.axhline(y=2.0, color='r', linestyle='-', label='2s SLA')
        ax1.legend()
        
        # Plot 2: Latency histogram
        ax2.hist(latencies, bins=50, alpha=0.75)
        ax2.set_title('Latency Distribution')
        ax2.set_xlabel('Latency (seconds)')
        ax2.set_ylabel('Count')
        ax2.grid(True)
        
        # Plot 3: Cache hit ratio over time
        # Group by time buckets (10 second intervals)
        bucket_size = 10  # seconds
        buckets = {}
        
        for i, ts in enumerate(timestamps):
            bucket = int(ts / bucket_size) * bucket_size
            if bucket not in buckets:
                buckets[bucket] = {"hits": 0, "total": 0}
            
            buckets[bucket]["total"] += 1
            if cache_hits[i]:
                buckets[bucket]["hits"] += 1
        
        bucket_times = sorted(buckets.keys())
        hit_ratios = [buckets[t]["hits"] / buckets[t]["total"] if buckets[t]["total"] > 0 else 0 for t in bucket_times]
        
        ax3.plot(bucket_times, hit_ratios, marker='o')
        ax3.set_title('Cache Hit Ratio over Time')
        ax3.set_xlabel('Time (seconds)')
        ax3.set_ylabel('Cache Hit Ratio')
        ax3.set_ylim(0, 1)
        ax3.grid(True)
        
        # Adjust layout and save
        plt.tight_layout()
        chart_filename = f"load_test_charts_{timestamp}.png"
        plt.savefig(chart_filename)
        print(f"Charts saved to {chart_filename}")

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Load test for Financial RAG API')
    
    parser.add_argument('--url', type=str, default=DEFAULT_BASE_URL,
                        help=f'Base URL of the API (default: {DEFAULT_BASE_URL})')
    
    parser.add_argument('--api-key', type=str, default=DEFAULT_API_KEY,
                        help=f'API key prefix (default: {DEFAULT_API_KEY})')
    
    parser.add_argument('--users', type=int, default=DEFAULT_CONCURRENT_USERS,
                        help=f'Number of concurrent users (default: {DEFAULT_CONCURRENT_USERS})')
    
    parser.add_argument('--duration', type=int, default=DEFAULT_TEST_DURATION_SECONDS,
                        help=f'Test duration in seconds (default: {DEFAULT_TEST_DURATION_SECONDS})')
    
    parser.add_argument('--ramp-up', type=int, default=DEFAULT_RAMP_UP_TIME,
                        help=f'Ramp-up time in seconds (default: {DEFAULT_RAMP_UP_TIME})')
    
    return parser.parse_args()

async def main():
    """Main function"""
    args = parse_args()
    
    # Create and run load test
    load_test = LoadTest(
        base_url=args.url,
        api_key=args.api_key,
        concurrent_users=args.users,
        duration_seconds=args.duration,
        ramp_up_time=args.ramp_up
    )
    
    await load_test.run_test()

if __name__ == "__main__":
    asyncio.run(main()) 