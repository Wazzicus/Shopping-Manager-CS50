# settings/routes.py
from flask import Blueprint, render_template, url_for, redirect, abort, flash, current_app, request
from flask_login import login_required, current_user
from app.extensions import db
from app.settings.forms import PasswordChangeForm, NameChangeForm, AvatarForm
from app.utils import log_activity
from werkzeug.utils import secure_filename
import os
import logging

settings_bp = Blueprint('settings_bp', __name__)


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@settings_bp.route('/', methods=["POST", "GET"])
@login_required
def account_settings():
    form = AvatarForm()
    password_change_form = PasswordChangeForm()
    name_change_form = NameChangeForm()
    if password_change_form.validate_on_submit() and password_change_form.submit.data:
        if current_user.check_password(password_change_form.current_password.data):
            current_user.set_password(password_change_form.new_password.data)
            db.session.commit()
            return redirect(url_for('main.dashboard'))
        else:
            abort(403)
        if name_change_form.validate_on_submit() and name_change_form.submit.data:
            current_user.name =name_change_form.new_name.data
            db.session.commit()
            try:
                log_activity(user_id=current_user.id, household_id=current_user.household_id, action_type="Name Change")
            except Exception as e:
                logging.error(f"Failed to log activity: {e}")
            return redirect(url_for('main.dashboard'))
        else:
            return redirect(url_for('settings_bp.settings'))
               
    return render_template('settings.html', password_change_form=password_change_form,
                           name_change_form=name_change_form,
                           seeds = ['lion', 'tiger', 'dragon', 'phoenix', 'storm', 'warrior'],
                            form=form
                          )

@settings_bp.route("/account/change_avatar", methods=["GET", "POST"])
@login_required
def change_avatar():
    form = AvatarForm()
    password_change_form = PasswordChangeForm()
    name_change_form = NameChangeForm()
    

    if form.validate_on_submit():
        # If DiceBear selected
        if form.dicebear_url.data:
            current_user.avatar_url = form.dicebear_url.data


        if form.avatar_upload.data and allowed_file(form.avatar_upload.data.filename):
            # Uploaded avatar takes priority
            filename = secure_filename(form.avatar_upload.data.filename)
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            form.avatar_upload.data.save(file_path)
            relative_path = os.path.join('uploads/avatars', filename)
            current_user.avatar_url = relative_path
        elif form.dicebear_url.data:
            current_user.avatar_url = form.dicebear_url.data


        if form.avatar_upload.data and form.dicebear_url.data:
            flash("Choose either DiceBear avatar or upload your own, not both.", "warning")
            return redirect(url_for('settings.account_settings'))
    

        db.session.commit()
        flash("Profile picture updated!", "success")
        return redirect(url_for('settings.account_settings'))

    return render_template('settings.html', form=form, password_change_form=password_change_form, name_change_form=name_change_form)