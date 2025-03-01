from flask import Flask, request, jsonify
from pymongo import MongoClient
import bcrypt
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# MongoDB Connection
client = MongoClient("mongodb://localhost:27017/")
db1 = client["test"]
users = db1["users"]
db2 = client["TwitterSentiment"]
tweets_collection = db2["tweets"]

@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password").encode("utf-8")  # Convert input password to bytes

    user = users.find_one({"email": email})
    if user:
        stored_password = user["password"]  # Password from DB (string)
        if isinstance(stored_password, str):  
            stored_password = stored_password.encode("utf-8")  # Convert stored password to bytes

        if bcrypt.checkpw(password, stored_password):
            return jsonify({"success": True}), 200
    
    return jsonify({"success": False}), 401

@app.route("/api/signup", methods=["POST"])
def signup():
    data = request.json
    email = data.get("email")
    password = data.get("password").encode('utf-8')

    # Check if the user already exists
    if users.find_one({"email": email}):
        return jsonify({"success": False, "message": "Email already exists"}), 400

    # Hash the password
    hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())

    # Store the user in MongoDB
    users.insert_one({"email": email, "password": hashed_password})

    return jsonify({"success": True}), 201

@app.route("/api/sentiment", methods=["GET"])
def get_sentiment():
     
    keyword_doc = tweets_collection.find_one({}, {"keyword": 1, "sentiment": 1, "clean_text": 1})

    if not keyword_doc:
        return jsonify({"error": "No data found"}), 404

    positive_count = tweets_collection.count_documents({"sentiment": "Positive"})
    negative_count = tweets_collection.count_documents({"sentiment": "Negative"})
    neutral_count = tweets_collection.count_documents({"sentiment": "Neutral"})

    return jsonify({
        "keyword": keyword_doc["keyword"],
        "positive_count": positive_count,
        "negative_count": negative_count,
        "neutral_count": neutral_count
    })

if __name__ == "__main__":
    app.run(debug=True, port=5012)
