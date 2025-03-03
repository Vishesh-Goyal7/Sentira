import tweepy
from pymongo import MongoClient
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import torch
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
from textblob import TextBlob

model_name = "cardiffnlp/twitter-roberta-base-sentiment"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)
sentiment_pipeline = pipeline("text-classification", model=model, tokenizer=tokenizer)

LABEL_MAP = {
    "LABEL_0": "Negative",
    "LABEL_1": "Neutral",
    "LABEL_2": "Positive"
}

BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAACqhzgEAAAAAE3W4YdNOKzYvnR%2FluNMLu8VPny8%3DdBQSHinUXxFqbWhTGpCunW7UJYWXrf9JwJ9VXwlsfeoaCTDIrT"  # Required for v2 API

nltk.download("stopwords")
nltk.download("punkt")
nltk.download("wordnet")

client = MongoClient("mongodb://localhost:27017/")
db = client["TwitterSentiment"]
collection = db["tweets"]

twitter_client = tweepy.Client(bearer_token=BEARER_TOKEN)
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words("english"))

def fetchTweets(query):
    tweets = twitter_client.search_recent_tweets(query=query, max_results=10)

    if tweets.data:
        for tweet in tweets.data:
            collection.insert_one({
                "keyword": query.lower(),
                "tweet_id": str(tweet.id),
                "text": tweet.text,
                "created_at": tweet.created_at,
                "author_id": tweet.author_id
            })
        print("Tweets stored successfully!")
    else:
        print("No tweets found.")

def clean_text(text):
    text = text.lower()  # Convert to lowercase
    text = re.sub(r"http\S+|www\S+|https\S+", "", text)  # Remove URLs
    text = re.sub(r"@\w+|#\w+", "", text)  # Remove mentions & hashtags
    text = re.sub(r"[^a-zA-Z\s]", "", text)  # Remove special characters
    words = word_tokenize(text)  # Tokenization
    words = [lemmatizer.lemmatize(word) for word in words if word not in stop_words]  # Lemmatization & Stopword Removal
    return " ".join(words)

def get_sentiment(text):
    result = sentiment_pipeline(text)[0]  # Get sentiment result
    sentiment_label = LABEL_MAP[result["label"]]  # Convert label (e.g., LABEL_0) to human-readable
    confidence = result["score"]  # Confidence score
    return sentiment_label, confidence

def preprocessTweets():
    tweets = collection.find({}, {"tweet_id": 1, "text": 1})
    for tweet in tweets:
        cleaned_text = clean_text(tweet["text"])
        collection.update_one(
            {"tweet_id": tweet["tweet_id"]},  
            {"$set": {"clean_text": cleaned_text}}
        )
    print("Tweets cleaned and updated successfully!")

def analyse():
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

def process_keyword(keyword):
    fetchTweets(keyword)
    preprocessTweets()
    analyse()
    print(f"Processing completed for keyword: {keyword}")
    
if __name__ == "__main__":
    process_keyword(keyword)