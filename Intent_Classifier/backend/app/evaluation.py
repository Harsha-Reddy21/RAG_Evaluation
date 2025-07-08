import json
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from pathlib import Path
from sentence_transformers import SentenceTransformer, util

# Initialize the sentence transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

def relevance_score(response: str, ideal: str) -> float:
    """
    Calculate relevance score using cosine similarity
    
    Args:
        response: The generated response
        ideal: The ideal or expected response
        
    Returns:
        Cosine similarity score between 0 and 1
    """
    try:
        # Encode the texts
        response_embedding = model.encode(response, convert_to_tensor=True)
        ideal_embedding = model.encode(ideal, convert_to_tensor=True)
        
        # Calculate cosine similarity
        cos_sim = util.cos_sim(response_embedding, ideal_embedding)
        return float(cos_sim[0][0])
    except Exception as e:
        print(f"Error calculating relevance score: {e}")
        return 0.0

def context_utilization_score(response: str, context: List[str]) -> float:
    """
    Calculate context utilization score based on word overlap
    
    Args:
        response: The generated response
        context: List of context strings used for generation
        
    Returns:
        Context utilization score between 0 and 1
    """
    try:
        # Join all context items
        context_text = " ".join(context)
        
        # Convert to lowercase and split into words
        context_words = set(context_text.lower().split())
        response_words = set(response.lower().split())
        
        # Calculate overlap
        if len(context_words) == 0:
            return 0.0
            
        overlap = len(context_words.intersection(response_words))
        return overlap / len(context_words)
    except Exception as e:
        print(f"Error calculating context utilization score: {e}")
        return 0.0

def load_query_history() -> pd.DataFrame:
    """
    Load query history from file
    
    Returns:
        DataFrame containing query history
    """
    data_file = Path("./data/query_history.jsonl")
    
    if not data_file.exists():
        return pd.DataFrame()
    
    data = []
    with open(data_file, "r") as f:
        for line in f:
            try:
                data.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    
    return pd.DataFrame(data)

def calculate_metrics() -> Dict:
    """
    Calculate evaluation metrics from query history
    
    Returns:
        Dictionary containing evaluation metrics
    """
    df = load_query_history()
    
    if df.empty:
        return {
            "intent_accuracy": 0.0,
            "avg_relevance": 0.0,
            "avg_context_utilization": 0.0,
            "avg_latency": 0.0,
            "samples_per_intent": {},
            "total_samples": 0
        }
    
    # Calculate intent accuracy
    df["intent_accuracy"] = df["true_intent"] == df["predicted_intent"]
    intent_accuracy = df["intent_accuracy"].mean()
    
    # Calculate average metrics
    avg_relevance = df["relevance"].mean()
    avg_context_utilization = df["context_utilization"].mean()
    avg_latency = df["latency"].mean()
    
    # Count samples per intent
    intent_counts = df["predicted_intent"].value_counts().to_dict()
    
    return {
        "intent_accuracy": float(intent_accuracy),
        "avg_relevance": float(avg_relevance),
        "avg_context_utilization": float(avg_context_utilization),
        "avg_latency": float(avg_latency),
        "samples_per_intent": intent_counts,
        "total_samples": len(df)
    }

def generate_test_set() -> List[Dict]:
    """
    Generate a test set of queries for evaluation
    
    Returns:
        List of dictionaries containing test queries
    """
    return [
        # Technical Support queries
        {"query": "How do I reset my password?", "true_intent": "Technical Support", 
         "ideal_answer": "To reset your password, go to settings > security > reset password."},
        {"query": "What are the API rate limits?", "true_intent": "Technical Support", 
         "ideal_answer": "API rate limits are set to 100 requests per minute for Basic tier."},
        {"query": "How do I set up OAuth integration?", "true_intent": "Technical Support", 
         "ideal_answer": "OAuth integration requires client_id and client_secret from the developer dashboard."},
        {"query": "I'm getting error code E1001, what does it mean?", "true_intent": "Technical Support", 
         "ideal_answer": "Error code E1001 indicates a network timeout, please check your connection."},
        {"query": "How can I enable debug mode?", "true_intent": "Technical Support", 
         "ideal_answer": "You can enable debug mode by setting DEBUG=true in your .env file."},
        
        # Billing queries
        {"query": "What are your pricing tiers?", "true_intent": "Billing", 
         "ideal_answer": "Our pricing tiers include Basic ($10/mo), Pro ($30/mo), and Enterprise (custom pricing)."},
        {"query": "What happens if I miss a payment?", "true_intent": "Billing", 
         "ideal_answer": "Missed payments result in account hold after 7 days and deactivation after 30 days."},
        {"query": "How do I get a refund?", "true_intent": "Billing", 
         "ideal_answer": "Refunds can be processed within 14 days of purchase through the billing portal."},
        {"query": "When are invoices generated?", "true_intent": "Billing", 
         "ideal_answer": "Invoices are generated on the 1st of each month and payment is due within 15 days."},
        {"query": "What's included in the Enterprise plan?", "true_intent": "Billing", 
         "ideal_answer": "Enterprise plans include custom SLAs and dedicated support channels."},
        
        # Feature Request queries
        {"query": "When will you add two-factor authentication?", "true_intent": "Feature Request", 
         "ideal_answer": "We are planning 2FA support in Q3 per our roadmap."},
        {"query": "Can you integrate with Slack?", "true_intent": "Feature Request", 
         "ideal_answer": "Integration with Slack is currently in beta testing."},
        {"query": "Will there be a mobile app?", "true_intent": "Feature Request", 
         "ideal_answer": "Mobile app development is scheduled for next year according to our roadmap."},
        {"query": "I need custom dashboard widgets", "true_intent": "Feature Request", 
         "ideal_answer": "Custom dashboard widgets are planned for the Q2 release."},
        {"query": "When will you support GraphQL?", "true_intent": "Feature Request", 
         "ideal_answer": "API v2 with GraphQL support is currently in development."}
    ] 