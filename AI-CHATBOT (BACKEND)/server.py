from flask import Flask, request, jsonify, Response
import google.generativeai as genai
from flask_cors import CORS
import mysql.connector
import json

app = Flask(__name__)
CORS(app, supports_credentials=True)  


conn = mysql.connector.connect(host="localhost", user="root", password="ROOT", database="AuthForm")
cursor = conn.cursor(dictionary=True)  


genai.configure(api_key="YOUR-API-KEY")


USERS_FILE = "users.json"
CHAT_HISTORY_FILE = "chat_history.json"



@app.post("/logout")
def logout():
    response = jsonify({"success": True, "message": "Logged out successfully"})
    response.delete_cookie("token")  
    return response



def load_users():
    try:
        with open(USERS_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []



def save_users(users):
    with open(USERS_FILE, "w") as file:
        json.dump(users, file, indent=4)



def load_chat_history():
    try:
        with open(CHAT_HISTORY_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []



def save_chat_history(user_message, bot_response):
    chat_history = load_chat_history()
    chat_history.append({"user": user_message, "bot": bot_response})

    with open(CHAT_HISTORY_FILE, "w") as file:
        json.dump(chat_history, file, indent=4)



def get_gemini_response(user_message):
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(user_message)
        return response.text
    except Exception as e:
        return "Error generating response."



@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "")

    if not user_message:
        return jsonify({"reply": "Please enter a message."})

    bot_response = get_gemini_response(user_message)
    save_chat_history(user_message, bot_response)

    return jsonify({"reply": bot_response})



@app.route("/history", methods=["GET"])
def history():
    return jsonify(load_chat_history())



@app.route("/clear_history", methods=["DELETE"])
def clear_history():
    with open(CHAT_HISTORY_FILE, "w") as file:
        json.dump([], file)
    return jsonify({"message": "Chat history cleared successfully."})



@app.route("/signup", methods=["POST"])
def signup():
    data = request.json
    cursor.execute("SELECT * FROM users WHERE email=%s", (data["email"],))
    existing_user = cursor.fetchone()

    if existing_user:
        return jsonify({"success": False, "message": "User already exists"}), 400

    cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
                   (data["name"], data["email"], data["password"]))
    conn.commit()
    return jsonify({"success": True, "message": "Signup successful"}), 201



@app.route("/login", methods=["POST"])
def login():
    data = request.json
    cursor.execute("SELECT * FROM users WHERE email=%s AND password=%s", (data["email"], data["password"]))
    user = cursor.fetchone()

    if user:
        return jsonify({"success": True, "message": "Login successful"}), 200
    return jsonify({"success": False, "message": "Invalid credentials"}), 401





@app.route("/")
def home():
    return "Flask server is running!"



if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)
