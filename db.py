import psycopg2
import os
import hashlib
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def get_connection():
    return psycopg2.connect(DATABASE_URL)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(name, email, password):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE email = %s", (email,))
    if cur.fetchone():
        conn.close()
        return False
    hashed_pw = hash_password(password)
    cur.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (name, email, hashed_pw))
    conn.commit()
    conn.close()
    return True

def login_user(email, password):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, password FROM users WHERE email = %s", (email,))
    result = cur.fetchone()
    conn.close()
    if result:
        user_id, name, hashed_pw = result
        if hash_password(password) == hashed_pw:
            return {"id": user_id, "name": name}
    return None

def submit_slider_mood(user_id, mood_value):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO moods (user_id, mood_type) VALUES (%s, %s)", (user_id, mood_value))
    conn.commit()
    conn.close()

def submit_questionnaire_mood(user_id, q1, q2, q3, q4, q5):
    total = q1 + q2 + q3 + q4 + q5
    if total <= 7:
        mood = "Stressed"
    elif total <= 12:
        mood = "Sad"
    elif total <= 17:
        mood = "Neutral"
    elif total <= 22:
        mood = "Good"
    else:
        mood = "Jolly"
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO moods (user_id, mood_type) VALUES (%s, %s)", (user_id, mood))
    conn.commit()
    conn.close()
    return mood

def get_analytics(user_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT mood_type, COUNT(*) FROM moods WHERE user_id = %s GROUP BY mood_type", (user_id,))
    results = cur.fetchall()

    mood_counts = {
        "Stressed": 0,
        "Sad": 0,
        "Neutral": 0,
        "Good": 0,
        "Jolly": 0
    }
    for mood, count in results:
        mood_counts[mood] = count

    # Daily analytics (last 7 days)
    cur.execute("""
        SELECT DATE(created_at), mood_type, COUNT(*) 
        FROM moods 
        WHERE user_id = %s AND created_at >= CURRENT_DATE - INTERVAL '6 days'
        GROUP BY DATE(created_at), mood_type 
        ORDER BY DATE(created_at)
    """, (user_id,))
    daily = cur.fetchall()

    # Weekly analytics (last 4 weeks)
    cur.execute("""
        SELECT DATE_TRUNC('week', created_at) AS week, mood_type, COUNT(*) 
        FROM moods 
        WHERE user_id = %s AND created_at >= CURRENT_DATE - INTERVAL '28 days'
        GROUP BY week, mood_type
        ORDER BY week
    """, (user_id,))
    weekly = cur.fetchall()

    # Monthly analytics (last 3 months)
    cur.execute("""
        SELECT DATE_TRUNC('month', created_at) AS month, mood_type, COUNT(*) 
        FROM moods 
        WHERE user_id = %s AND created_at >= CURRENT_DATE - INTERVAL '3 months'
        GROUP BY month, mood_type
        ORDER BY month
    """, (user_id,))
    monthly = cur.fetchall()

    conn.close()

    return {
        "total_counts": mood_counts,
        "daily": daily,
        "weekly": weekly,
        "monthly": monthly
    }


def send_friend_request(user_id, friend_email):
    conn = get_connection()
    cur = conn.cursor()

    # Find friend's user ID
    cur.execute("SELECT id FROM users WHERE email = %s", (friend_email,))
    friend = cur.fetchone()
    if not friend:
        conn.close()
        return False, "User not found"

    friend_id = friend[0]

    # Check if request already exists or they are already friends
    cur.execute("""
        SELECT * FROM friends 
        WHERE (user_id = %s AND friend_id = %s) OR (user_id = %s AND friend_id = %s)
    """, (user_id, friend_id, friend_id, user_id))
    if cur.fetchone():
        conn.close()
        return False, "Already requested or already friends"

    # Insert pending friend request
    cur.execute("""
        INSERT INTO friends (user_id, friend_id, status)
        VALUES (%s, %s, 'pending')
    """, (user_id, friend_id))
    
    conn.commit()
    conn.close()
    return True, "Friend request sent"
def get_pending_requests(user_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT f.id, u.name, u.email
        FROM friends f
        JOIN users u ON f.user_id = u.id
        WHERE f.friend_id = %s AND f.status = 'pending'
    """, (user_id,))

    requests = cur.fetchall()
    conn.close()

    return [{"request_id": r[0], "name": r[1], "email": r[2]} for r in requests]


def respond_to_request(request_id, accept=True):
    conn = get_connection()
    cur = conn.cursor()

    if accept:
        cur.execute("UPDATE friends SET status = 'accepted' WHERE id = %s", (request_id,))
    else:
        cur.execute("DELETE FROM friends WHERE id = %s", (request_id,))

    conn.commit()
    conn.close()
    return True

def add_friend(user_id, friend_email):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id FROM users WHERE email = %s", (friend_email,))
    result = cur.fetchone()

    if not result:
        conn.close()
        return {"success": False, "message": "User not found"}

    friend_id = result[0]

    # Prevent adding self or duplicates
    if friend_id == user_id:
        conn.close()
        return {"success": False, "message": "You cannot add yourself as a friend"}

    try:
        cur.execute("INSERT INTO friends (user_id, friend_id) VALUES (%s, %s)", (user_id, friend_id))
        conn.commit()
        conn.close()
        return {"success": True, "message": "Friend added"}
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        conn.close()
        return {"success": False, "message": "Already friends"}

def get_friends(user_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT u.id, u.name, u.email 
        FROM users u
        JOIN friends f ON u.id = f.friend_id
        WHERE f.user_id = %s
    """, (user_id,))
    friends = cur.fetchall()
    conn.close()

    return [{"id": fid, "name": name, "email": email} for fid, name, email in friends]

def post_mood_update(user_id, content):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO posts (user_id, content) VALUES (%s, %s)",
        (user_id, content)
    )
    conn.commit()
    conn.close()

def get_friend_posts(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT p.id, u.name, p.content, p.created_at
        FROM posts p
        JOIN users u ON p.user_id = u.id
        WHERE p.user_id = %s OR p.user_id IN (
            SELECT friend_id FROM friends WHERE user_id = %s
        )
        ORDER BY p.created_at DESC
    """, (user_id, user_id))
    posts = cur.fetchall()
    conn.close()
    return [{"id": pid, "name": name, "content": content, "created_at": str(ts)} for pid, name, content, ts in posts]
