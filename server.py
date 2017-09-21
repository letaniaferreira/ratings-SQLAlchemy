"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask_debugtoolbar import DebugToolbarExtension

from flask import (Flask, render_template, redirect, request, flash,
                   session)

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

    return render_template('homepage.html')


@app.route("/users")
def user_list():
    """Show list of users."""

    users = User.query.all()
    return render_template("all_users.html", users=users)


@app.route("/movies")
def movie_list():
    """Show list of movies."""

    movies = Movie.query.order_by('title').all()
    return render_template("all_movies.html", movies=movies)


@app.route("/movies/<some_id>")
def movie_details(some_id):
    """Shows movie details."""

    movie = Movie.query.get(some_id)

    return render_template("movie_page.html", movie=movie)


@app.route("/users/<some_id>")
def user_details(some_id):
    """Shows user details."""

    user = User.query.get(some_id)

    return render_template("user_page.html", user=user)


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
        flash("You have been registered and logged in! Yay!")
        session['email'] = email

    return redirect("/")


@app.route("/login", methods=["POST"])
def log_in():
    """Logs a user in"""

    email = request.form.get("email")
    password = request.form.get("password")

    user = db.session.query(User).filter_by(email=email).first()

    try:
        user.user_id

        if user and password == user.password:
            session['email'] = email
            flash("You have been logged in!")
            return render_template("user_page.html", user=user)
        else:
            flash("Login failed. Email or password was not correct.")
            return redirect("/")

    except AttributeError:
        flash("Login failed. Email or password was not correct.")
        return redirect("/")


@app.route("/rate", methods=["POST"])
def rate_movie():
    """Passes rating for movie"""

    movie_id = request.form.get("movie")
    score = request.form.get("score")
    movie = Movie.query.get(movie_id)

    try:
        email = session['email']

        user = User.query.filter_by(email=email).first()
        user_id = user.user_id
        rating = Rating.query.filter(Rating.user_id == user_id, Rating.movie_id == movie_id).first()
        if rating:
            rating.score = score
            db.session.commit()
            flash("You have updated your rating for " + movie.title + " to a " + score + ".")
            return redirect("/movies/" + movie_id)
        else:
            new_rating = Rating(movie_id=movie_id, user_id=user_id, score=score)
            db.session.add(new_rating)
            db.session.commit()
            flash("You have rated " + movie.title + " as a " + score + ".")
            return redirect("/movies/" + movie_id)

    except KeyError:
        flash("Not a valid user logged in!")
        return redirect("/")


@app.route("/logout")
def log_out():
    """Logs the user out"""

    del session['email']
    flash("You are logged out!")

    return redirect("/")

if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    app.jinja_env.auto_reload = app.debug  # make sure templates, etc. are not cached in debug mode

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
