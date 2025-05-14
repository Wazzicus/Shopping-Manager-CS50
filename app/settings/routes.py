# settings/routes.py
from flask import Blueprint, render_template, url_for, redirect, abort
from flask_login import login_required, current_user
from app.extensions import db
from app.settings.forms import PasswordChangeForm, NameChangeForm, ProfilePictureForm
from app.utils import log_activity
import logging

settings_bp = Blueprint('settings_bp', __name__)

@settings_bp.route('/')
@login_required
def account_settings():
    password_change_form = PasswordChangeForm()
    name_change_form = NameChangeForm()
    profile_picture_form = ProfilePictureForm()
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
        
        if profile_picture_form.validate_on_submit() and profile_picture_form.submit.data:
            current_user.profile_picture = profile_picture_form.picture.data
            db.session.commit()
            return redirect(url_for('main.dashboard'))
        else:
            return redirect(url_for('settings_bp.settings'))        
    return render_template('settings.html', password_change_form=password_change_form,
                           name_change_form=name_change_form,
                           profile_picture_form=profile_picture_form)