
import os
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
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
class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
with app.app_context():
    db.create_all()

# ---------------- HOME ----------------

@app.route("/")
def home():
    return render_template("home.html")

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

    total_users = User.query.count()
    total_messages = ContactMessage.query.count()
    current_time = datetime.now().strftime("%d %B %Y, %I:%M %p")

    return render_template(
        "dashboard.html",
        user=user.username,
        picture=user.profile_picture,
        total_users=total_users,
        total_messages=total_messages,
        current_time=current_time
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
    print("Uploaded file:", photo.filename)

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
    return render_template("profile.html", user=user.username, picture=user.profile_picture)

# ---------------- OTHER PAGES ----------------
# ---------------- EDIT PROFILE ----------------

@app.route("/edit-profile", methods=["GET", "POST"])
def edit_profile():
    if "user" not in session:
        return redirect(url_for("login"))

    user = User.query.filter_by(username=session["user"]).first()

    if request.method == "POST":
        new_username = request.form["username"]

        existing = User.query.filter_by(username=new_username).first()

        if existing and existing.id != user.id:
            return "Username already taken"

        user.username = new_username
        db.session.commit()

        session["user"] = new_username

        return redirect(url_for("profile"))

    return render_template("edit_profile.html", user=user)
# ---------------- CHANGE PASSWORD ----------------

@app.route("/change-password", methods=["GET", "POST"])
def change_password():
    if "user" not in session:
        return redirect(url_for("login"))

    user = User.query.filter_by(username=session["user"]).first()

    if request.method == "POST":
        old_password = request.form["old_password"]
        new_password = request.form["new_password"]

        if not check_password_hash(user.password, old_password):
            return "Current password is incorrect"

        user.password = generate_password_hash(new_password)
        db.session.commit()

        return redirect(url_for("profile"))

    return render_template("change_password.html")
@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        message = request.form["message"]

        new_message = ContactMessage(
            name=name,
            email=email,
            message=message
        )

        db.session.add(new_message)
        db.session.commit()

        return "Message sent successfully!"

    return render_template("contact.html")

# ---------------- RUN ----------------
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))
@app.route("/messages")
def messages():
    if "user" not in session:
        return redirect(url_for("login"))

    all_messages = ContactMessage.query.all()
    return render_template("messages.html", messages=all_messages)
@app.route("/delete-message/<int:id>")
def delete_message(id):
    message = ContactMessage.query.get_or_404(id)
    db.session.delete(message)
    db.session.commit()
    return redirect(url_for("messages"))
@app.route("/delete-user/<int:id>")
def delete_user(id):
    if "user" not in session:
        return redirect(url_for("login"))

    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()

    return redirect(url_for("users"))


@app.route("/users")
def users():
    if "user" not in session:
        return redirect(url_for("login"))

    search = request.args.get("search", "")

    if search:
        all_users = User.query.filter(
            User.username.contains(search)
        ).all()
    else:
        all_users = User.query.all()

    return render_template("users.html", users=all_users, search=search)


if __name__ == "__main__":
    app.run(debug=True)
