import torch
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import spacy
from textblob import TextBlob
from pymongo import MongoClient

# Load SpaCy for aspect extraction
nlp = spacy.load("en_core_web_sm")

# Load sentiment analysis model (RoBERTa)
model_name = "cardiffnlp/twitter-roberta-base-sentiment"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)
sentiment_pipeline = pipeline("text-classification", model=model, tokenizer=tokenizer)

# Sentiment label mapping
LABEL_MAP = {
    "LABEL_0": "Negative",
    "LABEL_1": "Neutral",
    "LABEL_2": "Positive"
}

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["TwitterSentiment"]
collection = db["tweets"]

# Function to perform sentiment analysis
def get_sentiment(text):
    result = sentiment_pipeline(text)[0]  # Get sentiment result
    sentiment_label = LABEL_MAP[result["label"]]  # Convert label (e.g., LABEL_0) to human-readable
    confidence = result["score"]  # Confidence score
    return sentiment_label, confidence

# Process tweets from MongoDB
tweets = collection.find({}, {"tweet_id": 1, "clean_text": 1})

for tweet in tweets:
    text = tweet["clean_text"]
    
    # Get overall sentiment
    sentiment, confidence = get_sentiment(text)

    # Update MongoDB with results
    collection.update_one(
        {"tweet_id": tweet["tweet_id"]},
        {"$set": {
            "sentiment": sentiment,
            "confidence": confidence,
        }}
    )

print("Sentiment Analysis completed successfully!")
