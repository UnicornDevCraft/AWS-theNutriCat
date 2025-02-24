import functools
import random
import string
import sqlite3
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from app.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    """Register user"""

    # Forget any user_id
    session.clear()

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        conf_password = request.form.get('confirmation')
        terms = request.form.get('terms')
        db = get_db()
        error = None
        errorType = None

        if not email:
            error = 'Email is required.'
            errorType = 'error'
        elif not password:
            error = 'Password is required.'
            errorType = 'error'
        elif not conf_password:
            error = 'Passwords have to match.'
            errorType = 'error'
        elif not terms:
            error = 'Terms not accepted.'
            errorType = 'error'
        else:
            rows = None
            # Query database for email
            rows = db.execute(
                "SELECT email FROM users WHERE email = ?", (email,)
            ).fetchone()

            if rows:
                error = f"{email} is already registered."
                errorType = 'error'

        if error is None:
            try:
                db.execute(
                    "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                    (generate_random_username(), email, generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError:
                error = f"Sorry, {email} is already registered."
                errorType = 'error'
            else:
                error = 'The registration was successful.'
                errorType = 'success'
                flash(error, errorType)

        if errorType == 'success':
            # Query database for id
            user = db.execute(
                "SELECT * FROM users WHERE email = ?", (email,)
            ).fetchone()
            session['user_id'] = user['id']
            return redirect(url_for("index"))

        flash(error, errorType)

    return render_template('auth/register.html')
        
@bp.route('/login', methods=('GET', 'POST'))
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        db = get_db()
        error = None

        user = db.execute(
            'SELECT * FROM users WHERE email = ?', (email,)
        ).fetchone()

        if user is None:
            error = 'Incorrect email.'
            errorType = 'error'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'
            errorType = 'error'

        if error is None:
            session['user_id'] = user['id']
            error = 'You are successfuly logged in!'
            errorType = 'success'
            flash(error, errorType)
            return redirect(url_for('index'))

        flash(error, errorType)

    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM users WHERE id = ?', (user_id,)
        ).fetchone()

@bp.route('/logout')
def logout():
    session.clear()
    error = 'You are successfuly logged out!'
    errorType = 'success'
    flash(error, errorType)
    return redirect(url_for('index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view

def generate_random_username():
    db = get_db()
    username = "user" + "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
    while db.execute("SELECT 1 FROM users WHERE username = ?", (username,)).fetchone():
        username = "user" + "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return username
