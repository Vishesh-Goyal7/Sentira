import pymongo
from textblob import TextBlob

# Connect to MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["TwitterSentiment"]
collection = db["tweets"]

# Fetch cleaned tweets
tweets = collection.find({}, {"tweet_id": 1, "clean_text": 1})

# Function to extract aspects
def extract_aspects(text):
    blob = TextBlob(text)
    aspects = {}
    
    for sentence in blob.sentences:
        sentiment = sentence.sentiment.polarity
        words = sentence.words
        
        for word in words:
            if word.lower() not in ["the", "is", "of", "but", "this"]:  # Ignore common words
                aspects[word.lower()] = sentiment  # Store aspect and its sentiment score

    return aspects

# Process each tweet
for tweet in tweets:
    aspects_sentiment = extract_aspects(tweet["clean_text"])  # Extract aspects

    # Update MongoDB with aspect-based sentiment analysis
    collection.update_one(
        {"tweet_id": tweet["tweet_id"]},
        {"$set": {"aspect_sentiment": aspects_sentiment}}
    )

print("ABSA complete! Aspect-based sentiments stored in MongoDB.")
