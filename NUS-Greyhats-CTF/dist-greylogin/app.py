import secrets

from flask import Flask, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash


app = Flask(__name__)
app.config["SECRET_KEY"] = secrets.token_hex(32)

# Users are kept in memory to keep this example small.
users = {
    "admin": {
        "username": "admin",
        "password_hash": generate_password_hash(secrets.token_urlsafe(32)),
        "role": "admin",
    }
}


@app.get("/")
def index():
    user = session.get("user")
    if not user:
        return redirect(url_for("login"))

    flag = None
    if user.get("role", "user") == "admin":
        with open("flag.txt") as file:
            flag = file.read().strip()
    return render_template("dashboard.html", user=user, flag=flag)


@app.route("/register", methods=["GET", "POST"])
def register():
    if "user" in session:
        return redirect(url_for("index"))

    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        if not username.strip() or not password:
            flash("Please fill in every field.", "error")
        elif len(username) < 3:
            flash("Username must be at least 3 characters.", "error")
        elif len(password) < 8:
            flash("Password must be at least 8 characters.", "error")
        elif username in users:
            flash("That username is already registered.", "error")
        else:
            users[username] = {
                "username": username,
                "password_hash": generate_password_hash(password),
                "role": "user",
            }
            flash("Account created. You can now sign in.", "success")
            return redirect(url_for("login"))

    return render_template("auth.html", mode="register")


@app.route("/login", methods=["GET", "POST"])
def login():
    if "user" in session:
        return redirect(url_for("index"))

    if request.method == "POST":
        submitted_user = request.form.to_dict()
        username = submitted_user.get("username", "")
        password = submitted_user.get("password", "")
        user = users.get(username)

        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user"] = submitted_user
            return redirect(url_for("index"))

        flash("Invalid username or password.", "error")

    return render_template("auth.html", mode="login")


@app.post("/logout")
def logout():
    session.clear()
    flash("You have been signed out.", "success")
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
