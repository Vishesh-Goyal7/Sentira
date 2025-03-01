import re
import pymongo
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

# Download NLTK resources
nltk.download("stopwords")
nltk.download("punkt")
nltk.download("wordnet")

# Connect to MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["TwitterSentiment"]
collection = db["tweets"]

# Initialize Lemmatizer
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words("english"))

# Function to clean tweet text
def clean_text(text):
    text = text.lower()  # Convert to lowercase
    text = re.sub(r"http\S+|www\S+|https\S+", "", text)  # Remove URLs
    text = re.sub(r"@\w+|#\w+", "", text)  # Remove mentions & hashtags
    text = re.sub(r"[^a-zA-Z\s]", "", text)  # Remove special characters
    words = word_tokenize(text)  # Tokenization
    words = [lemmatizer.lemmatize(word) for word in words if word not in stop_words]  # Lemmatization & Stopword Removal
    return " ".join(words)

# Fetch tweets from MongoDB
tweets = collection.find({}, {"tweet_id": 1, "text": 1})

# Process each tweet
for tweet in tweets:
    cleaned_text = clean_text(tweet["text"])
    
    # Update the cleaned text in MongoDB
    collection.update_one(
        {"tweet_id": tweet["tweet_id"]},  # Match existing tweet
        {"$set": {"clean_text": cleaned_text}}
    )

print("Tweets cleaned and updated successfully!")
