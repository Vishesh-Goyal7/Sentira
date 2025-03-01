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

# Function to extract aspects (noun phrases)
def extract_aspects(text):
    doc = nlp(text)
    aspects = [chunk.text for chunk in doc.noun_chunks]  # Extract noun phrases
    return aspects

# Function to perform sentiment analysis
def get_sentiment(text):
    result = sentiment_pipeline(text)[0]  # Get sentiment result
    sentiment_label = LABEL_MAP[result["label"]]  # Convert label (e.g., LABEL_0) to human-readable
    confidence = result["score"]  # Confidence score
    return sentiment_label, confidence

# Function to analyze aspect-based sentiment
def aspect_based_sentiment(text):
    aspects = extract_aspects(text)
    aspect_sentiments = {}

    sentences = text.split(". ")  # Split text into sentences for better aspect analysis

    for aspect in aspects:
        # Find sentence containing aspect
        relevant_sentence = next((s for s in sentences if aspect in s), text)
        
        # Get sentiment of sentence containing aspect
        polarity = TextBlob(relevant_sentence).sentiment.polarity  
        
        # Map polarity to sentiment labels
        if polarity > 0.1:
            aspect_sentiments[aspect] = "Positive"
        elif polarity < -0.1:
            aspect_sentiments[aspect] = "Negative"
        else:
            aspect_sentiments[aspect] = "Neutral"

    return aspect_sentiments

# Process tweets from MongoDB
tweets = collection.find({}, {"tweet_id": 1, "clean_text": 1})

for tweet in tweets:
    text = tweet["clean_text"]
    
    # Get overall sentiment
    sentiment, confidence = get_sentiment(text)

    # Get aspect-based sentiment
    aspect_sentiments = aspect_based_sentiment(text)

    # Update MongoDB with results
    collection.update_one(
        {"tweet_id": tweet["tweet_id"]},
        {"$set": {
            "sentiment": sentiment,
            "confidence": confidence,
            "aspect_sentiment": aspect_sentiments
        }}
    )

print("Sentiment Analysis + ABSA fixed and completed successfully!")
