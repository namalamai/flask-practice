

app = Flask(__name__)
app.secret_key = "secret"

# ---------------- ROUTES ----------------

@app.route('/')
def home():
    return "Hello Flask"

@app.route('/login')
def login():
    return "Login Page"

@app.route('/update-picture', methods=['GET', 'POST'])
def update_picture():
    return "Update Picture Page"

# ---------------- RUN ----------------

if __name__ == "__main__":
    app.run(debug=True)


    return render_template('update_picture.html', user=user)
app = Flask(__name__)
app.secret_key = "secret123"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# DATABASE MODEL
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    profile_picture = db.Column(db.String(200), default="default.png")

with app.app_context():
    db.create_all()



def home():
    return render_template("home.html")


# REGISTER
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        existing = User.query.filter_by(username=username).first()
        if existing:
            return "User already exists"

        hashed = generate_password_hash(password)
        new_user = User(username=username, password=hashed)

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("register.html")


# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session["user"] = username
            return redirect(url_for("dashboard"))
        else:
            return "Invalid username or password"

    return render_template("login.html")


# DASHBOARD
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))

    return render_template("dashboard.html", user=session["user"])


# LOGOUT
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))
@app.route("/upload", methods=["POST"])
def upload():
    return "Upload feature connected successfully!"
 

@app.route("/upload", methods=["POST"])
def upload():
    if "photo" not in request.files:
        return "No file selected"

    photo = request.files["photo"]

    if photo.filename == "":
        return "No file selected"

    filename = photo.filename
    photo.save(os.path.join("static", "uploads", filename))

    return "Picture uploaded successfully!"

