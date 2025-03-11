from flask import Flask, request, jsonify
import google.generativeai as genai
from flask_cors import CORS
import mysql.connector
import json

app = Flask(__name__)
CORS(app, supports_credentials=True)  

# Configure Gemini API client
genai.configure(api_key="API-KEY")  # Replace with your actual API key
genai_client = genai.GenerativeModel("gemini-1.5-flash")  # Use correct model name

# Database connection function
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="ROOT",
        database="AuthForm"
    )

USERS_FILE = "users.json"
CHAT_HISTORY_FILE = "chat_history.json"

# Function to generate AI response
def get_gemini_response(user_message):
    try:
        response = genai_client.generate_content(user_message)
        return response.text
    except Exception as e:
        return f"Error generating response: {str(e)}"

# Save chat history
def save_chat_history(user_message, bot_response):
    chat_history = load_chat_history()
    chat_history.append({"user": user_message, "bot": bot_response})

    with open(CHAT_HISTORY_FILE, "w") as file:
        json.dump(chat_history, file, indent=4)

# Load chat history
@app.route("/history", methods=["GET"])
def load_chat_history():
    try:
        with open(CHAT_HISTORY_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# Clear chat history
@app.route("/clear_history", methods=["DELETE"])
def clear_history():
    with open(CHAT_HISTORY_FILE, "w") as file:
        json.dump([], file)
    return jsonify({"message": "Chat history cleared successfully."})

# Chat endpoint
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "")

    if not user_message:
        return jsonify({"reply": "Please enter a message."})

    bot_response = get_gemini_response(user_message)
    save_chat_history(user_message, bot_response)

    return jsonify({"reply": bot_response})

# User Signup
@app.route("/signup", methods=["POST"])
def signup():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM users WHERE email=%s", (data["email"],))
    existing_user = cursor.fetchone()

    if existing_user:
        return jsonify({"success": False, "message": "User already exists"}), 400

    cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
                   (data["name"], data["email"], data["password"]))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "Signup successful"}), 201

# User Login
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM users WHERE email=%s AND password=%s", (data["email"], data["password"]))
    user = cursor.fetchone()

    conn.close()
    if user:
        return jsonify({"success": True, "message": "Login successful"}), 200
    return jsonify({"success": False, "message": "Invalid credentials"}), 401

# User Logout
@app.post("/logout")
def logout():
    response = jsonify({"success": True, "message": "Logged out successfully"})
    response.delete_cookie("token")  
    return response

@app.route("/")
def home():
    return "Flask server is running!"

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)
