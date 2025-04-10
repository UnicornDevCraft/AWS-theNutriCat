import functools
import random
import string
from flask import (
    Blueprint, flash, g, jsonify, redirect, render_template, request, session, url_for
)
from app.models import User
from app.db import db

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

        if not email:
            flash('Email is required.', 'error')
        elif not password:
            flash('Password is required.', 'error')
        elif password != conf_password:
            flash('Passwords must match.', 'error')
        elif not terms:
            flash('Terms not accepted.', 'error')
        else:
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                flash(f"{email} is already registered.", 'error')
            else:
                user = User(username=generate_random_username(), email=email)
                user.set_password(password)
                db.session.add(user)
                db.session.commit()
                
                flash('Registration successful.', 'success')
                session['user_id'] = user.id
                return redirect(url_for("recipes.index"))

    return render_template('auth/register.html')
        
@bp.route('/login', methods=('GET', 'POST'))
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()

        if user is None or not user.check_password(password):
            flash('Incorrect email or password.', 'error')
        else:
            session['user_id'] = user.id
            flash('You are successfully logged in!', 'success')
            return redirect(url_for('recipes.index'))

    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = User.query.get(user_id)

@bp.route('/logout')
def logout():
    session.clear()
    flash('You are successfuly logged out!', 'success')
    return redirect(url_for('recipes.index'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            if request.accept_mimetypes["application/json"]:
                return jsonify({"success": False, "error": "Unauthorized"}), 401
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view

@bp.route('/profile')
@login_required
def profile():
    user = User.query.filter_by(id=session.get('user_id')).first()
    
    return render_template('auth/profile.html', user=user)

def generate_random_username():
    username = "user" + "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
    while User.query.filter_by(username=username).first(): 
        username = "user" + "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return username


