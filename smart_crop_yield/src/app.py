from flask import Flask, render_template, request, redirect, session, url_for, flash
from flask_mail import Mail, Message
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import pickle
import numpy as np

app = Flask(__name__)
app.secret_key = "smart_crop_secret_key"

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client["smart_crop_yield"]
users_collection = db["users"]

# Flask-Mail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'jblessedwasike@gmail.com'
app.config['MAIL_PASSWORD'] = 'ebis xdru nuyr qqie'
app.config['MAIL_DEFAULT_SENDER'] = 'jblessedwasike@gmail.com'

mail = Mail(app)

# Dictionary of crop details
crop_details = {
    "rice": {
        "name": "Rice",
        "description": "Rice thrives in warm, humid conditions and requires flooding during early growth stages.",
        "requirements": {"Temperature": "20-35°C", "Rainfall": "150-300 cm", "Soil": "Clay or loamy"}
    },
    "wheat": {
        "name": "Wheat",
        "description": "Wheat is best grown in well-drained soils with good organic matter in cooler climates.",
        "requirements": {"Temperature": "10-24°C", "Rainfall": "50-100 cm", "Soil": "Loamy or sandy loam"}
    },
    "maize": {
        "name": "Maize",
        "description": "Maize grows well in warm climates with good sunlight and regular weeding.",
        "requirements": {"Temperature": "18-30°C", "Rainfall": "50-100 cm", "Soil": "Well-drained loam"}
    },
    "cotton": {
        "name": "Cotton",
        "description": "Cotton needs warm temperatures, adequate irrigation, and pest control.",
        "requirements": {"Temperature": "20-30°C", "Rainfall": "50-100 cm", "Soil": "Deep, well-drained loam"}
    },
    "potato": {
        "name": "Potato",
        "description": "Potatoes grow best in cool weather and require well-drained, loose soils.",
        "requirements": {"Temperature": "15-20°C", "Rainfall": "50-75 cm", "Soil": "Sandy loam"}
    },
    "sugarcane": {
        "name": "Sugarcane",
        "description": "Sugarcane requires a long, warm growing season and lots of water.",
        "requirements": {"Temperature": "20-30°C", "Rainfall": "100-150 cm", "Soil": "Loamy or sandy loam"}
    },
    "soybean": {
        "name": "Soybean",
        "description": "Soybeans thrive in warm, moist conditions and benefit from nitrogen-fixing bacteria.",
        "requirements": {"Temperature": "20-30°C", "Rainfall": "50-125 cm", "Soil": "Loamy or clay"}
    },
    "kidneybeans": {
        "name": "Kidney Beans",
        "description": "Kidney beans grow well in warm climates with moderate watering.",
        "requirements": {"Temperature": "15-25°C", "Rainfall": "60-100 cm", "Soil": "Loamy"}
    }
}

@app.route("/")
def home():
    if "user" in session:
        return render_template("index.html", name=session["user"]["name"])
    return redirect(url_for("login"))

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        if users_collection.find_one({"email": email}):
            return render_template("signup.html", error="Email already registered.")

        hashed_password = generate_password_hash(password)
        users_collection.insert_one({
            "name": name,
            "email": email,
            "password": hashed_password
        })
        session["user"] = {"name": name, "email": email}
        return redirect(url_for("home"))

    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = users_collection.find_one({"email": email})
        if user and check_password_hash(user["password"], password):
            session["user"] = {"name": user["name"], "email": user["email"]}
            return redirect(url_for("home"))
        else:
            return render_template("login.html", error="Invalid email or password.")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        user_name = request.form['name']
        user_email = request.form['email']
        user_message = request.form['message']

        msg = Message(subject=f"New Contact Message from {user_name}",
                      sender=app.config['MAIL_USERNAME'],
                      recipients=["jblessedwasike@gmail.com"])
        msg.body = f"""
        Name: {user_name}
        Email: {user_email}
        Message:
        {user_message}
        """
        try:
            mail.send(msg)
            flash("Your message has been sent successfully!", "success")
        except Exception as e:
            print("Mail send failed:", e)
            flash("An error occurred while sending your message.", "danger")
        return redirect(url_for("contact"))

    return render_template("contact.html")

@app.route("/guide")
def guide():
    return render_template("guide.html")

@app.route("/about")
def about():
    return render_template("about.html")

import requests

@app.route("/predict", methods=["GET", "POST"])
def predict():
    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        try:
            model = pickle.load(open("crop_model.pkl", "rb"))
            features = [ float(request.form[f]) for f in ["nitrogen","phosphorus","potassium","temperature","humidity","ph","rainfall"] ]
            normalized = [min(1, f/m) for f, m in zip(features, [120,60,100,35,90,7.0,300])]
            predicted = model.predict(np.array([normalized]))[0]
            crop_key = predicted.lower()

            # Fetch live info from Wikipedia
            wiki_resp = requests.get(
                f"https://en.wikipedia.org/api/rest_v1/page/summary/{crop_key}"
            )
            if wiki_resp.ok:
                data = wiki_resp.json()
                live_desc = data.get("extract")
                crop_name = data.get("title", crop_details[crop_key]["name"])
            else:
                live_desc = crop_details[crop_key]["description"]
                crop_name = crop_details[crop_key]["name"]

            crop = {
                "name": crop_name,
                "requirements": crop_details[crop_key]["requirements"],
                "description": live_desc
            }
            timestamp = datetime.now().strftime("%I:%M %p EAT on %B %d, %Y")
            return render_template("result.html", crop=crop, timestamp=timestamp)

        except Exception as e:
            return render_template("error.html", error=str(e))
    return render_template("predict.html")

@app.errorhandler(404)
def page_not_found(e):
    return render_template("error.html", error="Page not found."), 404

if __name__ == "__main__":
    app.run(debug=True)
