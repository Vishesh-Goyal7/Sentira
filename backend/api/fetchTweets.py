import tweepy
from pymongo import MongoClient

BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAHpdzgEAAAAAUbHcVIzFUWgdaK0xSslrny1qaXk%3D0ZDNf9XlsvsUdyQwyFL9NIGTcv9RTQPzpmvWgyVsYzzvCir5pp"  # Required for v2 API

client = MongoClient("mongodb://localhost:27017/")
db = client["TwitterSentiment"]
collection = db["tweets"]

twitter_client = tweepy.Client(bearer_token=BEARER_TOKEN)

query = "BJP"
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