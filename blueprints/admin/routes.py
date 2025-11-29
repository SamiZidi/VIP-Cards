from flask import render_template, request, redirect, url_for, session
from functools import wraps
from . import admin_bp
from secrets import compare_digest
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import generate_csrf
import dotenv
import os

dotenv.load_dotenv()
USER_NAME = os.getenv("ADMIN_USERNAME")
PASSWORD = os.getenv("ADMIN_PASSWORD")

# Initialize rate limiter
limiter = Limiter(
    get_remote_address,
    storage_uri="memory://"
)

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'admin_logged_in' not in session:
            return redirect(url_for('admin_bp.admin_login'))
        return f(*args, **kwargs)
    return decorated

@admin_bp.route("/admin", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def admin_login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        
        # Use constant-time comparison to prevent timing attacks
        username_valid = compare_digest(username, USER_NAME)
        password_valid = compare_digest(password, PASSWORD)
        
        if username_valid and password_valid:
            session.permanent = True
            session['admin_logged_in'] = True
            return redirect(url_for('admin_bp.admin_dashboard'))
        else:
            # Redirect with error parameter
            return redirect(url_for('admin_bp.admin_login', error='invalid'))

    if 'admin_logged_in' in session:
        return redirect(url_for('admin_bp.admin_dashboard'))

    return render_template("admin/admin_login.html")


@admin_bp.route("/admin/dashboard")
@login_required
def admin_dashboard():
    return render_template("admin/admin.html")

@admin_bp.route("/logout")
def logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_bp.admin_login'))

@admin_bp.route("/admin/competitions")
@login_required
def admin_competitions():
    return render_template("admin/competitions.html")