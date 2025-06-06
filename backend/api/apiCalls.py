from flask import Flask, request, jsonify
from pymongo import MongoClient
import bcrypt
from flask_cors import CORS
import subprocess

app = Flask(__name__)
CORS(app)

client = MongoClient("mongodb://localhost:27017/")
db1 = client["test"]
users = db1["users"]
db2 = client["TwitterSentiment"]
tweets_collection = db2["tweets"]

@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password").encode("utf-8")  

    user = users.find_one({"email": email})
    if user:
        stored_password = user["password"]  
        if isinstance(stored_password, str):  
            stored_password = stored_password.encode("utf-8")

        if bcrypt.checkpw(password, stored_password):
            return jsonify({"success": True}), 200
    
    return jsonify({"success": False}), 401

@app.route("/api/signup", methods=["POST"])
def signup():
    data = request.json
    email = data.get("email")
    password = data.get("password").encode('utf-8')

    if users.find_one({"email": email}):
        return jsonify({"success": False, "message": "Email already exists"}), 400

    hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())

    users.insert_one({"email": email, "password": hashed_password})

    return jsonify({"success": True}), 201

@app.route("/api/sentiment/<keyword>", methods=["GET"])
def get_sentiment_data(keyword):
    try:
        sentiment_records = list(tweets_collection.find({"keyword": keyword}))

        positive_count = sum(1 for record in sentiment_records if record["sentiment"] == "Positive")
        negative_count = sum(1 for record in sentiment_records if record["sentiment"] == "Negative")
        neutral_count = sum(1 for record in sentiment_records if record["sentiment"] == "Neutral")
        return jsonify({
            "keyword": keyword.lower(),
            "positive_count": positive_count,
            "negative_count": negative_count,
            "neutral_count": neutral_count
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/previous-searches", methods=["GET"])
def get_previous_searches():
    try:
        keywords = tweets_collection.distinct("keyword")
        
        return jsonify({"keywords": keywords}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/analyze", methods=["POST"])
def analyze_keyword():
    data = request.get_json()
    keyword = data.get("keyword")
    
    if not keyword:
        return jsonify({"error": "Keyword is required"}), 400
    
    from brain import process_keyword
    result = process_keyword(keyword)

    return jsonify({"message": f"Analysis complete for {keyword}", "keyword": keyword, "result" : result})

if __name__ == "__main__":
    app.run(debug=True, port=5012)
