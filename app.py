import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime
from chat_request import send_openai_request

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or "a secret key"
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
db.init_app(app)

with app.app_context():
    import models
    db.create_all()

@app.route("/")
def index():
    if "username" not in session:
        return redirect(url_for("login"))
    return redirect(url_for("chat"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        if username:
            session["username"] = username
            return redirect(url_for("chat"))
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))

@app.route("/chat")
def chat():
    if "username" not in session:
        return redirect(url_for("login"))
    messages = models.Message.query.order_by(models.Message.timestamp).all()
    return render_template("chat.html", username=session["username"], messages=messages)

@app.route("/send_message", methods=["POST"])
def send_message():
    if "username" not in session:
        return jsonify({"error": "Not authenticated"}), 401
    
    content = request.json.get("message")
    if not content:
        return jsonify({"error": "No message provided"}), 400

    # Save user message
    user_message = models.Message(
        content=content,
        username=session["username"],
        is_ai=False,
        timestamp=datetime.utcnow()
    )
    db.session.add(user_message)
    
    try:
        # Get AI response
        ai_response = send_openai_request(content)
        ai_message = models.Message(
            content=ai_response,
            username="AI Assistant",
            is_ai=True,
            timestamp=datetime.utcnow()
        )
        db.session.add(ai_message)
        db.session.commit()
        
        return jsonify({
            "user_message": {
                "content": user_message.content,
                "username": user_message.username,
                "timestamp": user_message.timestamp.isoformat()
            },
            "ai_message": {
                "content": ai_message.content,
                "username": ai_message.username,
                "timestamp": ai_message.timestamp.isoformat()
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
