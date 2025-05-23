"""
settings/routes.py

Blueprint for managing user account settings:
- Password change
- Name change (via AJAX)
- Avatar change (upload or DiceBear)

Forms used:
- AvatarForm
- PasswordChangeForm
- NameChangeForm
"""

from flask import Blueprint, render_template, url_for, redirect, flash, current_app, request, jsonify
from flask_login import login_required, current_user, logout_user
from app.extensions import db
from app.settings.forms import PasswordChangeForm, NameChangeForm, AvatarForm
from app.utils import log_activity
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import os
import logging
from datetime import datetime
from tzlocal import get_localzone

tz = get_localzone()

settings_bp = Blueprint('settings_bp', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    """
    Check if a filename has an allowed image extension.

    Args:
        filename (str): The uploaded file's name

    Returns:
        bool: True if file extension is allowed
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@settings_bp.route('/account', methods=['GET'])
@login_required
def account_settings():
    """
    Render the main settings page.

    Returns:
        Rendered settings.html template with all forms.
    """
    form = AvatarForm()
    password_change_form = PasswordChangeForm()
    name_change_form = NameChangeForm()

    return render_template(
        'settings.html',
        form=form,
        password_change_form=password_change_form,
        name_change_form=name_change_form,
        seeds=['lion', 'tiger', 'dragon', 'phoenix', 'storm', 'warrior']
    )


@settings_bp.route('/settings/change-password', methods=['POST'])
@login_required
def change_password():
    """
    Password change route
    """
    form = AvatarForm()
    password_change_form = PasswordChangeForm()
    name_change_form = NameChangeForm()

    if password_change_form.validate_on_submit():
        if not check_password_hash(current_user.password, password_change_form.old_password.data):
            form.old_password.errors.append('Incorrect current password')
            return render_template(
                'settings.html',
                form=form,
                password_change_form=password_change_form,
                name_change_form=name_change_form,
                seeds=['lion', 'tiger', 'dragon', 'phoenix', 'storm', 'warrior']
            )
        current_user.password = generate_password_hash(password_change_form.new_password.data)
        db.session.commit()

        logout_user()
        flash('Password changed successfully. Please log in again.', 'success')
        return redirect(url_for('auth.login'))

    return render_template(
        'settings.html',
        form=form,
        password_change_form=password_change_form,
        name_change_form=name_change_form,
        seeds=['lion', 'tiger', 'dragon', 'phoenix', 'storm', 'warrior']
    )


@settings_bp.route('/change-name', methods=['POST'])
@login_required
def change_name():
    """
    Handles AJAX name change request.

    Returns:
        JSON response with success or error message.
    """
    old_name = current_user.name
    data = request.get_json()
    new_name = data.get('new_name', '').strip()

    if not new_name:
        return jsonify({'error': 'Name cannot be empty'}), 400
    
    try:
        current_user.name = new_name
        db.session.commit()

        log_activity(user_id=current_user.id, household_id=current_user.household_id, action_type="Name Change", timestamp=datetime.now(tz), old_name=old_name, new_name=new_name)
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error creating list: {e}")

    return jsonify({'message': 'Name updated successfully'})


@settings_bp.route("/account/change_avatar", methods=["POST"])
@login_required
def change_avatar():
    """
    Handles avatar change via file upload or DiceBear URL.
    Enforces mutual exclusivity (can't submit both at once).

    Returns:
        Redirect to settings with success or warning.
    """
    form = AvatarForm()
    password_change_form = PasswordChangeForm()
    name_change_form = NameChangeForm()

    if form.validate_on_submit():
        # Prevent submitting both fields
        if form.avatar_upload.data and form.dicebear_url.data:
            flash("Choose either DiceBear avatar or upload your own, not both.", "warning")
            return redirect(url_for('settings_bp.account_settings'))

        # File upload path handling
        if form.avatar_upload.data and allowed_file(form.avatar_upload.data.filename):
            filename = f"{current_user.id}_{secure_filename(form.avatar_upload.data.filename)}"
            file_path = os.path.join(current_app.config['AVATAR_FOLDER'], filename)

            # Save file
            form.avatar_upload.data.save(file_path)

            # Store relative path used by files_bp
            db_path = f"avatars/{filename}"
            current_user.avatar_url = url_for('files_bp.uploaded_file', filename=db_path)

        # DiceBear URL handling
        elif form.dicebear_url.data:
            current_user.avatar_url = form.dicebear_url.data

        else:
            flash("Please provide either a DiceBear avatar or upload an image.", "warning")
            return redirect(url_for('settings_bp.account_settings'))

        db.session.commit()
        flash("Profile picture updated!", "success")
        return redirect(url_for('settings_bp.account_settings'))

    return render_template(
        'settings.html',
        form=form,
        password_change_form=password_change_form,
        name_change_form=name_change_form,
        seeds=['lion', 'tiger', 'dragon', 'phoenix', 'storm', 'warrior']
    )
