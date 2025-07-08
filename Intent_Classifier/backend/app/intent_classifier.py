from transformers import pipeline
import os
from pathlib import Path

# Initialize the classifier
def init_classifier():
    # Check if model is already downloaded to avoid redownloading
    cache_dir = Path.home() / ".cache" / "huggingface"
    model_name = "bhadresh-savani/distilbert-base-uncased-emotion"
    
    try:
        intent_classifier = pipeline(
            "text-classification", 
            model=model_name,
            device=-1  # Use CPU
        )
        print("Intent classifier initialized successfully")
        return intent_classifier
    except Exception as e:
        print(f"Error initializing intent classifier: {e}")
        return None

# Map emotion labels to intent categories
def map_intent(label):
    """
    Maps emotion labels to customer support intents:
    - joy/love -> Feature Request (positive emotions)
    - anger/fear/sadness -> Billing (negative emotions)
    - surprise/others -> Technical Support (default)
    """
    if label in ["joy", "love"]:
        return "Feature Request"
    elif label in ["anger", "fear", "sadness"]:
        return "Billing"
    else:
        return "Technical Support"

# Detect intent from query
def detect_intent(query, classifier):
    """
    Detect intent from user query using emotion classifier
    """
    try:
        result = classifier(query)
        label = result[0]["label"]
        confidence = result[0]["score"]
        intent = map_intent(label)
        return intent, confidence
    except Exception as e:
        print(f"Error detecting intent: {e}")
        return "Technical Support", 0.0  # Default fallback 