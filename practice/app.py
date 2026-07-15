
import os
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "secret123"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ---------------- DATABASE ----------------

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    profile_picture = db.Column(db.String(200), default="default.png")

with app.app_context():
    db.create_all()

# ---------------- HOME ----------------

@app.route("/")
def home():
    return render_template("index.html")

# ---------------- REGISTER ----------------

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])

        existing = User.query.filter_by(username=username).first()
        if existing:
            return "User already exists"

        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("register.html")

# ---------------- LOGIN ----------------

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session["user"] = user.username
            return redirect(url_for("dashboard"))

        return "Invalid username or password"

    return render_template("login.html")
# ---------------- DASHBOARD ----------------

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))

    user = User.query.filter_by(username=session["user"]).first()

    return render_template(
        "dashboard.html",
        user=user.username,
        picture=user.profile_picture
    )

# ---------------- UPDATE PICTURE ----------------

@app.route("/update-picture")
def update_picture():
    if "user" not in session:
        return redirect(url_for("login"))

    return render_template("update_picture.html")

@app.route("/upload", methods=["POST"])
def upload():
    if "user" not in session:
        return redirect(url_for("login"))

    if "photo" not in request.files:
        return "No file selected"

    photo = request.files["photo"]

    if photo.filename == "":
        return "No file selected"

    filename = photo.filename

    upload_folder = os.path.join(app.static_folder, "uploads")
    os.makedirs(upload_folder, exist_ok=True)

    photo.save(os.path.join(upload_folder, filename))

    user = User.query.filter_by(username=session["user"]).first()
    user.profile_picture = filename
    db.session.commit()

    return redirect(url_for("dashboard"))

# ---------------- PROFILE ----------------

@app.route("/profile")
def profile():
    if "user" not in session:
        return redirect(url_for("login"))

    user = User.query.filter_by(username=session["user"]).first()
    return render_template("profile.html", user=user)

# ---------------- OTHER PAGES ----------------

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

# ---------------- RUN ----------------
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))
if __name__ == "__main__":
    app.run(debug=True)
