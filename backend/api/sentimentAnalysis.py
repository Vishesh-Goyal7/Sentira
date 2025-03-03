import torch
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
from textblob import TextBlob
from pymongo import MongoClient

model_name = "cardiffnlp/twitter-roberta-base-sentiment"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)
sentiment_pipeline = pipeline("text-classification", model=model, tokenizer=tokenizer)

LABEL_MAP = {
    "LABEL_0": "Negative",
    "LABEL_1": "Neutral",
    "LABEL_2": "Positive"
}

client = MongoClient("mongodb://localhost:27017/")
db = client["TwitterSentiment"]
collection = db["tweets"]

def get_sentiment(text):
    result = sentiment_pipeline(text)[0]  
    sentiment_label = LABEL_MAP[result["label"]]  
    confidence = result["score"]  
    return sentiment_label, confidence

tweets = collection.find({}, {"tweet_id": 1, "clean_text": 1})

for tweet in tweets:
    text = tweet["clean_text"]
    
    sentiment, confidence = get_sentiment(text)

    collection.update_one(
        {"tweet_id": tweet["tweet_id"]},
        {"$set": {
            "sentiment": sentiment,
            "confidence": confidence,
        }}
    )

print("Sentiment Analysis completed successfully!")
