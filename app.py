
import os
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY")

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ---------------- DATABASE ----------------
# ---------------- DATABASE ----------------

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password = db.Column(db.String(200), nullable=False)
    profile_picture = db.Column(db.String(200), default="default.png")
    posts = db.relationship("Post", backref="user", lazy=True)

    comments = db.relationship(
        "Comment",
        backref="user",
        lazy=True
    )

    likes = db.relationship(
        "Like",
        backref="user",
        lazy=True
    )

class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(200), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    comments = db.relationship(
        "Comment",
        backref="post",
        lazy=True,
        cascade="all, delete-orphan"
    )

    likes = db.relationship(
        "Like",
        backref="post",
        lazy=True,
        cascade="all, delete-orphan"
    )

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    is_read = db.Column(db.Boolean, default=False)

class Follow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    following_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)


class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

@app.route("/follow/<int:user_id>", methods=["POST"])
def follow(user_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    follower_id = session["user_id"]

    if follower_id == user_id:
        return redirect(url_for("users"))

    existing_follows = Follow.query.filter_by(
        follower_id=follower_id,
        following_id=user_id
    ).all()

    if existing_follows:
        for follow_record in existing_follows:
            db.session.delete(follow_record)
    else:
        new_follow = Follow(
            follower_id=follower_id,
            following_id=user_id
        )
        db.session.add(new_follow)

        notification = Notification(
            user_id=user_id,
            message="Someone started following you."
        )
        db.session.add(notification)

    db.session.commit()

    return redirect(url_for("users"))


@app.route("/")
def home():
    posts = Post.query.all()
    user = User.query.get(session["user_id"]) if "user_id" in session else None

    unread_notifications = 0
    if "user_id" in session:
        unread_notifications = Notification.query.filter_by(
            user_id=session["user_id"],
            is_read=False
        ).count()

    return render_template(
        "home.html",
        posts=posts,
        user=user,
        unread_notifications=unread_notifications
    )
# ---------------- REGISTER ----------------

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        new_user = User(
            username=username,
            email=email,
            password=generate_password_hash(password)
        )

        db.session.add(new_user)
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
            session["user_id"] = user.id
            return redirect(url_for("dashboard"))

        return "Invalid username or password"

    return render_template("login.html")
# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))

    user = User.query.filter_by(username=session["user"]).first()

    if user is None:
        session.clear()
        return redirect(url_for("login"))

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
    print("=== UPLOAD ROUTE REACHED ===")

    if "user" not in session:
        return redirect(url_for("login"))
    print(request.files)

    if "photo" not in request.files:
        return "No file selected"

    photo = request.files["photo"]
    filename = photo.filename

    upload_folder = os.path.join(app.static_folder, "uploads")
    os.makedirs(upload_folder, exist_ok=True)

    photo.save(os.path.join(upload_folder, filename))

    user = User.query.filter_by(username=session["user"]).first()
    user.profile_picture = filename
    db.session.commit()
    print("Saved picture:", user.profile_picture)
    return redirect(url_for("dashboard"))

# ---------------- PROFILE ----------------

@app.route("/profile")
def profile():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user = User.query.get(session["user_id"])

    if user is None:
        session.clear()
        return redirect(url_for("login"))

    return render_template(
        "profile.html",
        user=user,
        picture=user.profile_picture
    )
@app.route("/posts", methods=["GET", "POST"])
def posts():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        content = request.form["content"]
        image = request.files.get("image")

        filename = None

        if image and image.filename:
            filename = secure_filename(image.filename)
            image.save(
                os.path.join(app.static_folder, "uploads", filename)
            )

        user = User.query.get(session["user_id"])

        if user:
            new_post = Post(
                content=content,
                image=filename,
                user_id=user.id
            )

            db.session.add(new_post)
            db.session.commit()

        return redirect(url_for("posts"))

    all_posts = Post.query.order_by(Post.id.desc()).all()

    return render_template("posts.html", posts=all_posts)


@app.route("/comment/<int:post_id>", methods=["POST"])
def comment(post_id):
    if "user" not in session:
        return redirect(url_for("login"))

    content = request.form["comment"]
    user = User.query.filter_by(username=session["user"]).first()

    new_comment = Comment(
        content=content,
        post_id=post_id,
        user_id=user.id
    )

    db.session.add(new_comment)
    db.session.commit()

    return redirect(url_for("posts"))
@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
def edit_post(post_id):
    if "user" not in session:
        return redirect(url_for("login"))

    post = Post.query.get_or_404(post_id)
    user = User.query.filter_by(username=session["user"]).first()

    if post.user_id != user.id:
        return redirect(url_for("posts"))

    if request.method == "POST":
        post.content = request.form["content"]
        print("POST CONTENT:", content)
        db.session.commit()
        return redirect(url_for("posts"))

    return render_template("edit_post.html", post=post)
@app.route("/delete-post/<int:post_id>", methods=["POST"])
def delete_post(post_id):
    if "user" not in session:
        return redirect(url_for("login"))

    post = Post.query.get_or_404(post_id)
    user = User.query.filter_by(username=session["user"]).first()

    if post.user_id == user.id:
        db.session.delete(post)
        db.session.commit()

    return redirect(url_for("posts"))

@app.route("/like/<int:post_id>", methods=["POST"])
def like_post(post_id):
    if "user" not in session:
        return redirect(url_for("login"))

    user = User.query.filter_by(username=session["user"]).first()

    existing_like = Like.query.filter_by(
        post_id=post_id,
        user_id=user.id
    ).first()

    if not existing_like:
        new_like = Like(
            post_id=post_id,
            user_id=user.id
        )
        db.session.add(new_like)
        db.session.commit()

    return redirect(url_for("posts"))
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
@app.route("/messages/<int:user_id>", methods=["GET", "POST"])
def private_messages(user_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    current_user_id = session["user_id"]
    other_user = User.query.get_or_404(user_id)

    if request.method == "POST":
        content = request.form.get("content", "").strip()
        if content:
            new_message = Message(
                sender_id=current_user_id,
                receiver_id=user_id,
                content=content
            )
            db.session.add(new_message)
            db.session.commit()
        return redirect(url_for("private_messages", user_id=user_id))

    messages = Message.query.filter(
        ((Message.sender_id == current_user_id) & (Message.receiver_id == user_id)) |
        ((Message.sender_id == user_id) & (Message.receiver_id == current_user_id))
    ).order_by(Message.id.asc()).all()

    return render_template(
        "messages.html",
        messages=messages,
        other_user=other_user
    )

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

    Comment.query.filter_by(user_id=user.id).delete(synchronize_session=False)
    Like.query.filter_by(user_id=user.id).delete(synchronize_session=False)
    Follow.query.filter(
        (Follow.follower_id == user.id) |
        (Follow.following_id == user.id)
    ).delete(synchronize_session=False)
    Message.query.filter(
        (Message.sender_id == user.id) |
        (Message.receiver_id == user.id)
    ).delete(synchronize_session=False)
    Notification.query.filter_by(user_id=user.id).delete(
        synchronize_session=False
    )

    Post.query.filter_by(user_id=user.id).delete(
        synchronize_session=False
    )

    db.session.delete(user)
    db.session.commit()

    return redirect(url_for("users"))


@app.route("/users")
def users():
    if "user_id" not in session:
        return redirect(url_for("login"))

    search = request.args.get("search", "")

    if search:
        all_users = User.query.filter(
            User.username.contains(search)
        ).all()
    else:
        all_users = User.query.all()

    following_ids = {
        follow.following_id
        for follow in Follow.query.filter_by(
            follower_id=session["user_id"]
        ).all()
    }

    return render_template(
        "users.html",
        users=all_users,
        search=search,
        following_ids=following_ids
    )


@app.route("/delete-account", methods=["POST"])
def delete_account():
    if "user" not in session:
        return redirect(url_for("login"))

    user = User.query.filter_by(username=session["user"]).first()

    if user:
        db.session.delete(user)
        db.session.commit()

    session.clear()

    return redirect(url_for("home"))
@app.route("/search")
def search():
    if "user_id" not in session:
        return redirect(url_for("login"))

    q = request.args.get("q", "").strip()

    if q:
        users = User.query.filter(User.username.ilike(f"%{q}%")).all()
    else:
        users = []

    return render_template("search.html", users=users, query=q)
@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form["email"]

        user = User.query.filter_by(email=email).first()

        if user:
            flash("Password reset feature will be available soon.", "success")
        else:
            flash("No account found with that email.", "danger")

        return redirect(url_for("login"))

    return render_template("forgot_password.html")
@app.route("/notifications")
def notifications():
    if "user_id" not in session:
        return redirect(url_for("login"))

    notifications = Notification.query.filter_by(
        user_id=session["user_id"]
    ).order_by(Notification.id.desc()).all()

    return render_template(
        "notifications.html",
        notifications=notifications
    )


if __name__ == "__main__":
    app.run(debug=True)

