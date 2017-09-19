"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask_debugtoolbar import DebugToolbarExtension

from flask import (Flask, render_template, redirect, request, flash,
                   session, jsonify)

from model import User, Rating, Movie, connect_to_db, db



app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""
    a = jsonify([1, 3])
    return render_template('homepage.html')


@app.route("/users")
def user_list():
    """Show list of users."""

    users = User.query.all()
    return render_template("all_users.html", users=users)


@app.route("/register")
def reg_form():
    """Show registration form"""

    return render_template("registration_form.html")


@app.route("/register", methods=["POST"])
def confirm_registration():
    """Confirms registration"""

    email = request.form.get("email")
    password = request.form.get("password")

    duplicates = db.session.query(User).filter_by(email=email).all()

    if duplicates:
        flash("This email is already registered. Please try again with a different email.")
    else:
        new_user = User(email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash("You have been registered! Yay!")

    return redirect("/")


@app.route("/login", methods=["POST"])
def log_in():
    """Logs a user in"""

    email = request.form.get("email")
    password = request.form.get("password")

    duplicates = db.session.query(User).filter_by(email=email).first()

    if duplicates:
        if password == duplicates.password:
            session[email] = password
            flash("You have been logged in!")
            return redirect("/")
        else:
            flash("Wrong password. Please try again.")
            return redirect("/")
    else:
        flash("Not a valid user. Please create an account.")
        return render_template("registration_form.html")

@app.route("/logout")
def log_out():
    """Logs the user out"""

    for key in session.keys():
     session.pop[]


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    app.jinja_env.auto_reload = app.debug  # make sure templates, etc. are not cached in debug mode

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
