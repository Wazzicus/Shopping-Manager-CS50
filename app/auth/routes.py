"""
auth/routes.py

This blueprint handles user authentication:
- Login and registration (combined on one page with a tab-switcher)
- Logout functionality

Forms:
- LoginForm
- RegistrationForm
"""

from flask import Blueprint, render_template, url_for, flash, redirect, request
from app.extensions import db
from flask_login import login_user, current_user, logout_user
from app.auth.forms import RegistrationForm, LoginForm
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User

# Define the authentication blueprint
auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/auth', methods=["GET", "POST"])
def auth():
    """
    Combined login and registration route.

    Handles:
    - Redirecting logged-in users to the dashboard
    - Logging in users if valid credentials are submitted
    - Registering new users if the registration form is valid
    - Rendering the auth.html template with both forms

    Returns:
        - Redirect to dashboard/setup on success
        - Renders form with flash messages on failure
    """
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    login_form = LoginForm()
    register_form = RegistrationForm()
    action = request.form.get("action")  # Determines whether login or register was submitted

    # Handle login submission
    if action == "login" and login_form.validate_on_submit():
        user = User.query.filter_by(username=login_form.username.data).first()
        if user and check_password_hash(user.password, login_form.password.data):
            login_user(user, remember=True)
            flash("You have been logged in!", "success")
            return redirect(url_for("main.dashboard"))
        else:
            flash("Login failed. Check username and/or password!", "danger")

    # Handle registration submission
    elif action == "register" and register_form.validate_on_submit():
        existing_user = User.query.filter_by(username=register_form.username.data).first()
        if existing_user:
            flash("Username already exists. Please choose a different one.", "danger")
        else:
            hashed_password = generate_password_hash(register_form.password.data)
            user = User(
                username=register_form.username.data,
                name=register_form.name.data,
                password=hashed_password,
            )
            db.session.add(user)
            db.session.commit()

            # Set DiceBear avatar as default
            user.avatar_url = f'https://api.dicebear.com/7.x/initials/svg?seed={user.name}'
            db.session.commit()

            login_user(user)
            flash("Your account has been created successfully!", "success")
            return redirect(url_for("household_bp.setup"))

    else:
        # Display warnings if form validation failed
        if action == "login" and login_form.errors:
            flash("Please correct the errors in the login form.", "warning")
        elif action == "register" and register_form.errors:
            flash("Please correct the errors in the registration form.", "warning")

    # Set initial tab based on request method or query
    initial_active_tab = 'login'
    if request.method == "POST" and action == "register":
        initial_active_tab = 'register'
    if request.method == "GET" and request.args.get('tab') == 'register':
        initial_active_tab = 'register'

    return render_template(
        "auth.html",
        title="Get Started",
        login_form=login_form,
        register_form=register_form,
        initial_active_tab=initial_active_tab
    )


@auth_bp.route("/logout", methods=["POST"])
def logout():
    """
    Logs out the current user.

    Returns:
        Redirect to login/registration page with a flash message.
    """
    logout_user()
    flash("You have been logged out!", "info")
    return redirect(url_for("auth.auth"))
