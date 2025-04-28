from flask import Flask, request, jsonify
from flask_cors import CORS
from db import (
    register_user,
    login_user,
    submit_slider_mood,
    submit_questionnaire_mood,
    get_analytics,
    send_friend_request,
    get_pending_requests,
    respond_to_request
)
import psycopg2
from db import add_friend 
from datetime import datetime
from db import get_friends  # Add this to the top

app = Flask(__name__)
CORS(app)

# -- PostgreSQL Railway Connection for community posts --
conn = psycopg2.connect(
    dbname="railway",
    user="postgres",
    password="OzmMvQTBFLDzOFfyjbscpsEIFzSJzucV",
    host="gondola.proxy.rlwy.net",
    port="18005"
)
cursor = conn.cursor()

# ----------- Authentication & Mood Endpoints ------------

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not all([name, email, password]):
        return jsonify({"success": False, "message": "Missing fields"}), 400

    success = register_user(name, email, password)
    if success:
        return jsonify({"success": True, "message": "User registered"})
    else:
        return jsonify({"success": False, "message": "Email already exists"}), 409

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    user = login_user(email, password)
    if user:
        return jsonify({"success": True, "user": user})
    else:
        return jsonify({"success": False, "message": "Invalid credentials"}), 401

@app.route("/submit_mood", methods=["POST"])
def submit_mood():
    data = request.get_json()
    user_id = data.get("user_id")
    mood_type = data.get("mood_type")  # Either an int or a dict

    if isinstance(mood_type, int):
        submit_slider_mood(user_id, mood_type)
        return jsonify({"success": True, "message": "Mood submitted (slider)"})
    elif isinstance(mood_type, dict):
        mood = submit_questionnaire_mood(
            user_id,
            mood_type.get("q1", 0),
            mood_type.get("q2", 0),
            mood_type.get("q3", 0),
            mood_type.get("q4", 0),
            mood_type.get("q5", 0),
        )
        return jsonify({"success": True, "message": f"Mood submitted (questionnaire): {mood}"})
    
    return jsonify({"success": False, "message": "Invalid mood format"}), 400

@app.route("/analytics/<int:user_id>", methods=["GET"])
def analytics(user_id):
    data = get_analytics(user_id)
    return jsonify(data)

# ----------- Community Routes ------------

@app.route("/add_post", methods=["POST"])
def add_post():
    data = request.get_json()
    user_id = data['user_id']
    content = data['content']

    cursor.execute("INSERT INTO posts (user_id, content) VALUES (%s, %s)", (user_id, content))
    conn.commit()
    return jsonify({'message': 'Post added successfully'}), 201

@app.route("/get_posts", methods=["GET"])
def get_posts():
    cursor.execute("""
        SELECT posts.content, posts.created_at, users.name
        FROM posts
        JOIN users ON posts.user_id = users.id
        ORDER BY posts.created_at DESC
    """)
    posts = cursor.fetchall()
    result = []
    for content, created_at, name in posts:
        result.append({
            'name': name,
            'content': content,
            'created_at': created_at.strftime('%Y-%m-%d %H:%M')
        })
    return jsonify(result)

@app.route("/send_friend_request", methods=["POST"])
def send_friend():
    data = request.get_json()
    user_id = data.get("user_id")
    friend_email = data.get("friend_email")

    success, message = send_friend_request(user_id, friend_email)
    return jsonify({"success": success, "message": message})


@app.route("/pending_requests/<int:user_id>", methods=["GET"])
def pending_requests(user_id):
    requests = get_pending_requests(user_id)
    return jsonify({"success": True, "requests": requests})


@app.route("/respond_to_request", methods=["POST"])
def respond_request():
    data = request.get_json()
    request_id = data.get("request_id")
    accept = data.get("accept", True)

    respond_to_request(request_id, accept)
    return jsonify({"success": True, "message": "Request handled"})
 

@app.route("/add_friend", methods=["POST"])
def add_friend_route():
    data = request.get_json()
    user_id = data.get("user_id")
    friend_email = data.get("friend_email")

    if not all([user_id, friend_email]):
        return jsonify({"success": False, "message": "Missing fields"}), 400

    result = add_friend(user_id, friend_email)
    status_code = 200 if result["success"] else 409
    return jsonify(result), status_code



@app.route("/friends/<int:user_id>", methods=["GET"])
def get_friends_route(user_id):
    friends = get_friends(user_id)
    return jsonify({"success": True, "friends": friends})

from db import post_mood_update, get_friend_posts  # Add at the top

@app.route("/post", methods=["POST"])
def create_post():
    data = request.get_json()
    user_id = data.get("user_id")
    content = data.get("content")
    
    if not content:
        return jsonify({"success": False, "message": "Post content required"}), 400
    
    post_mood_update(user_id, content)
    return jsonify({"success": True, "message": "Post created!"})

@app.route("/feed/<int:user_id>", methods=["GET"])
def get_feed(user_id):
    posts = get_friend_posts(user_id)
    return jsonify({"success": True, "posts": posts})



# ----------- Start Server ------------
if __name__ == "__main__":
    app.run(debug=True)
