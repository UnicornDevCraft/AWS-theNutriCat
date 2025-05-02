"""Authentication routes for the application."""

# Standard library imports
import functools
import logging
import random
import string

# Related third-party imports
import requests
from flask import (
    Blueprint, current_app, flash, g, jsonify, redirect, render_template, request, session, url_for
)
from itsdangerous import URLSafeTimedSerializer

# Local application/library imports
from app.db import db
from app.models import User, Recipe, Tag, Favorite


# Create a blueprint for authentication routes
bp = Blueprint("auth", __name__, url_prefix="/auth")

# Set up logging
logger = logging.getLogger(__name__)


# --- Utility Functions ---

def generate_random_username():
    """Generate a random username"""
    username = "user" + "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
    while User.query.filter_by(username=username).first(): 
        username = "user" + "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return username

def generate_reset_token(user_email, expires_sec=3600):
    """Generate a password reset token"""
    s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    return s.dumps(user_email, salt="password-reset-salt")

def verify_reset_token(token, max_age=3600):
    """Verify the password reset token"""
    s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    try:
        return s.loads(token, salt="password-reset-salt", max_age=max_age)
    except Exception:
        return None

def verify_recaptcha(response_token):
    """Verify reCAPTCHA response with Google"""
    secret = current_app.config["RECAPTCHA_SECRET_KEY"]
    res = requests.post(
        "https://www.google.com/recaptcha/api/siteverify",
        data={"secret": secret, "response": response_token}
    )
    return res.json().get("success", False)

# --- Middleware ---

@bp.before_app_request
def load_logged_in_user():
    """Load the logged-in user from the session"""
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        g.user = User.query.get(user_id)

def login_required(view):
    """Decorator to ensure the user is logged in before accessing a view"""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            if request.accept_mimetypes["application/json"]:
                return jsonify({"success": False, "error": "Unauthorized"}), 401
            return redirect(url_for("auth.login"))
        return view(**kwargs)
    return wrapped_view

# --- Routes for authorization ---

@bp.route("/register", methods=("GET", "POST"))
def register():
    """Register user"""
    # Forget any user_id
    session.pop("user_id", None)

    # After registration form submission
    if request.method == "POST":

        # Get reCAPTCHA token from form
        recaptcha_response = request.form.get("g-recaptcha-response")
        if not recaptcha_response or not verify_recaptcha(recaptcha_response):
            flash("reCAPTCHA verification failed. Try again.", "error")
            return redirect(url_for("auth.register"))
    
        # Get form data
        email = request.form.get("email")
        password = request.form.get("password")
        conf_password = request.form.get("confirmation")
        terms = request.form.get("terms")

        # Validate form data
        if not email:
            flash("Email is required.", "error")
        elif not password:
            flash("Password is required.", "error")
        elif password != conf_password:
            flash("Passwords must match.", "error")
        elif not terms:
            flash("Terms not accepted.", "error")
        elif User.query.filter_by(email=email).first():
            flash(f"{email} is already registered.", "error")
        else:
            user = User(username=generate_random_username(), email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            
            flash("Registration successful.", "success")
            session["user_id"] = user.id
            return redirect(url_for("recipes.index"))

    return render_template("auth/register.html", recaptcha_site_key=current_app.config["RECAPTCHA_SITE_KEY"])


@bp.route("/login", methods=("GET", "POST"))
def login():
    """Log user in"""
    # Forget any user_id
    session.clear()

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()

        if user is None or not user.check_password(password):
            flash("Incorrect email or password.", "error")
        else:
            session["user_id"] = user.id
            flash("You are successfully logged in!", "success")
            return redirect(url_for("recipes.index"))

    return render_template("auth/login.html")


@bp.route("/logout")
def logout():
    """Log user out"""
    session.clear()
    flash("You are successfuly logged out!", "success")
    return redirect(url_for("recipes.index"))


# --- Profile & Account Management ---

@bp.route("/profile")
def profile():
    """Display user profile"""
    user = User.query.filter_by(id=session.get("user_id")).first()

    if user is None:
        flash("Please log in to view your profile.", "error")
        return redirect(url_for("auth.login"))

    recipe_count = (
        db.session.query(Recipe)
        .join(Recipe.tags)
        .filter(Tag.type == "my_recipe")
        .count()
    )
    favorite_count = Favorite.query.filter_by(user_id=user.id).count()
    
    return render_template("auth/profile.html", user=user, user_recipe_count=recipe_count, favorite_count=favorite_count)  


@bp.route("/change-username", methods=["POST"])
@login_required
def change_username():
    """Change the username of the logged-in user"""
    new_username = request.form.get("new_username").strip()

    if not new_username:
        flash("Invalid username.", "error")
    elif User.query.filter_by(username=new_username).first():
        flash("Username already taken.", "error")
    else:
        g.user.username = new_username
        db.session.commit()
        flash("Username updated successfully!", "success") 
    
    return redirect(url_for("auth.profile"))


@bp.route("/change-password", methods=["POST"])
@login_required
def change_password():
    """Change the password of the logged-in user"""
    current_password = request.form.get("current_password")
    new_password = request.form.get("new_password")

    if not g.user.check_password(current_password):
        flash("Current password is incorrect.", "error")
    elif current_password == new_password:
        flash("New password must be different from the current one.", "error")
    else:
        g.user.set_password(new_password)
        db.session.commit()
        flash("Your password has been updated successfully!", "success")
    
    return redirect(url_for("auth.profile"))

# --- Password Reset ---

@bp.route("/forgot-password", methods=("GET", "POST"))
def forgot_password():
    """Send password reset email"""
    if request.method == "POST":
        # Get reCAPTCHA token from form
        recaptcha_response = request.form.get("g-recaptcha-response")
        email = request.form.get("email")
        
        if not verify_recaptcha(recaptcha_response):
            flash("reCAPTCHA verification failed. Try again.", "error")
            # Keep the email entered by the user
            email = request.form["email"]
            return redirect(url_for("auth.forgot_password"))
        
        user = User.query.filter_by(email=email).first()
        if user:
            token = generate_reset_token(user.email)
            reset_url = url_for("auth.reset_password", token=token, _external=True)
            print(f"Password reset link: {reset_url}")  # Only for debugging, remove in production
            flash("Password reset instructions have been sent to your email.", "success")
        else:
            flash("Email not found.", "error")

    return render_template("auth/forgot_password.html", recaptcha_site_key=current_app.config["RECAPTCHA_SITE_KEY"])


@bp.route("/reset-password/<token>", methods=("GET", "POST"))
def reset_password(token):
    """Reset password using token"""
    # Check if the token is valid
    email = verify_reset_token(token)
    if not email:
        flash("The password reset link is invalid or has expired.", "error")
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()
        if user:
            user.set_password(password)
            db.session.commit()
            flash("Your password has been updated.", "success")
            return redirect(url_for("auth.login"))

    return render_template("auth/reset_password.html")


@bp.route("/check-email")
def check_email():
    """Check if an email is already registered"""
    email = request.args.get("email", "").strip()

    if not email:
        return jsonify({"exists": False, "error": "No email provided"}), 400

    exists = db.session.execute(
        db.select(User).filter_by(email=email)
    ).scalar_one_or_none() is not None

    return jsonify({"exists": exists})