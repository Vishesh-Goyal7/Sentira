import re
import pymongo
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

nltk.download("stopwords")
nltk.download("punkt")
nltk.download("wordnet")

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["TwitterSentiment"]
collection = db["tweets"]

lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words("english"))

def clean_text(text):
    text = text.lower()  
    text = re.sub(r"http\S+|www\S+|https\S+", "", text)
    text = re.sub(r"@\w+|#\w+", "", text)  
    text = re.sub(r"[^a-zA-Z\s]", "", text)
    words = word_tokenize(text)  
    words = [lemmatizer.lemmatize(word) for word in words if word not in stop_words]  
    return " ".join(words)

tweets = collection.find({}, {"tweet_id": 1, "text": 1})

for tweet in tweets:
    cleaned_text = clean_text(tweet["text"])
    
    collection.update_one(
        {"tweet_id": tweet["tweet_id"]},  
        {"$set": {"clean_text": cleaned_text}}
    )

print("Tweets cleaned and updated successfully!")
