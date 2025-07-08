import os
import json
from typing import Dict, List, Tuple, Optional
from pathlib import Path

# Mock knowledge base - in a real application, this would be a vector database
KNOWLEDGE_BASE = {
    "Technical Support": [
        "To reset your password, go to settings > security > reset password.",
        "API rate limits are set to 100 requests per minute for Basic tier.",
        "OAuth integration requires client_id and client_secret from the developer dashboard.",
        "Error code E1001 indicates a network timeout, please check your connection.",
        "You can enable debug mode by setting DEBUG=true in your .env file."
    ],
    "Billing": [
        "Our pricing tiers include Basic ($10/mo), Pro ($30/mo), and Enterprise (custom pricing).",
        "Missed payments result in account hold after 7 days and deactivation after 30 days.",
        "Refunds can be processed within 14 days of purchase through the billing portal.",
        "Invoices are generated on the 1st of each month and payment is due within 15 days.",
        "Enterprise plans include custom SLAs and dedicated support channels."
    ],
    "Feature Request": [
        "We are planning 2FA support in Q3 and AI summarization in Q4 per our roadmap.",
        "Integration with Slack and MS Teams is currently in beta testing.",
        "Mobile app development is scheduled for next year according to our roadmap.",
        "Custom dashboard widgets are planned for the Q2 release.",
        "API v2 with GraphQL support is currently in development."
    ]
}

def retrieve_context(intent: str, query: str, top_k: int = 2) -> List[str]:
    """
    Retrieve relevant context based on intent and query
    
    Args:
        intent: The detected intent
        query: The user query
        top_k: Number of context items to retrieve
        
    Returns:
        List of context strings
    """
    # In a real application, this would use semantic search
    # For this demo, we'll just return the first top_k items for the intent
    if intent in KNOWLEDGE_BASE:
        return KNOWLEDGE_BASE[intent][:top_k]
    return []

def build_prompt(intent: str, query: str, context: List[str]) -> str:
    """
    Build a prompt based on intent, query and context
    
    Args:
        intent: The detected intent
        query: The user query
        context: List of context strings
        
    Returns:
        Formatted prompt for the LLM
    """
    context_text = "\n".join(context)
    
    if intent == "Technical Support":
        return f"""You are a technical support assistant for a SaaS product.
Using ONLY the following documentation, answer the user's question:

DOCUMENTATION:
{context_text}

USER QUESTION:
{query}

If you cannot answer the question based on the provided documentation, politely say so and suggest contacting support for more assistance.
"""
    
    elif intent == "Billing":
        return f"""You are a billing support assistant for a SaaS product.
Based on the following billing policies, answer the customer's question:

BILLING POLICIES:
{context_text}

CUSTOMER QUESTION:
{query}

Only answer based on the information provided. If you don't have enough information, politely say so.
"""
    
    elif intent == "Feature Request":
        return f"""You are a product manager for a SaaS product.
Based on our current product roadmap, address this feature request:

PRODUCT ROADMAP:
{context_text}

FEATURE REQUEST:
{query}

Explain if the feature is already planned, when it might be available, or politely explain if it's not currently on the roadmap.
"""
    
    else:
        # Generic fallback prompt
        return f"""You are a helpful assistant for a SaaS product.
Using the following information, answer the user's question:

INFORMATION:
{context_text}

USER QUESTION:
{query}

Be concise and helpful.
"""

def save_query_data(query_data: Dict) -> None:
    """
    Save query data for evaluation purposes
    
    Args:
        query_data: Dictionary containing query information
    """
    data_dir = Path("./data")
    data_dir.mkdir(exist_ok=True)
    
    data_file = data_dir / "query_history.jsonl"
    
    with open(data_file, "a") as f:
        f.write(json.dumps(query_data) + "\n") 