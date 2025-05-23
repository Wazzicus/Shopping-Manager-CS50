"""
household/routes.py

Blueprint for household management functionality.

Routes include:
- Creating and joining households
- Viewing, renaming, deleting, and leaving households
- Admin-specific member management (remove, transfer, regenerate join code)
"""

from flask import Blueprint, render_template, url_for, flash, redirect, request,jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Household as HouseholdModel, User as UsersModel
from app.household.forms import HouseholdCreationForm, HouseholdJoinForm
from app.utils import log_activity
import secrets, logging
from tzlocal import get_localzone
from datetime import datetime

tz = get_localzone()

household_bp = Blueprint('household_bp', __name__)

@household_bp.route('/setup', methods=['GET', 'POST'])
@login_required
def setup():
    """
    Displays the setup page where users can either:
    - Create a new household (if not already in one)
    - Join an existing household using a join code

    Handles form validation, flash messaging, and logging.
    """

    create_form = HouseholdCreationForm(prefix='create')
    join_form = HouseholdJoinForm(prefix='join')

    if request.method == "POST":
        create_form = HouseholdCreationForm(request.form, prefix='create')
        join_form = HouseholdJoinForm(request.form, prefix='join')
        action = request.form.get("action")

        if action == "create" and create_form.validate():
            if current_user.household_id:
                flash("You already belong to a household.", "warning")
                return redirect(url_for("main.dashboard"))
            
            household = HouseholdModel(name=create_form.household_name.data, admin_id=current_user.id, join_code=secrets.token_hex(4).upper())
            db.session.add(household)
            db.session.flush()
            current_user.household_id = household.id
            current_user.role = 'admin'
            db.session.commit()

            log_successful = True
            try:
                log_activity(user_id=current_user.id, 
                             household_id=household.id, 
                             action_type="Household Creation", 
                             timestamp=datetime.now(tz))
            except Exception as e:
                logging.exception(f"Failed to log household creation activity: {e}")
                log_successful = False
            
            if log_successful:
                flash('Household created successfully!', 'success')
            else:
                flash('Household created, but logging the activity failed. Please contact support if issues persist.', 'warning')
            
            return redirect(url_for("main.dashboard"))

        elif action == "join" and join_form.validate():
            
            household_to_join = HouseholdModel.query.filter_by(join_code=join_form.join_code.data).first() 
            if household_to_join:
                current_user.household_id = household_to_join.id
                current_user.role = 'member'
                db.session.flush()
                db.session.commit()

                try:
                    log_activity(user_id=current_user.id, 
                                 household_id=household_to_join.id, 
                                 action_type="Household Joining", 
                                 timestamp=datetime.now(tz))
                except Exception as e:

                    logging.exception(f"Failed to log household joining activity: {e}")
                flash(f'Welcome to {household_to_join.name}!', 'success')

                return redirect(url_for('main.dashboard'))
            
            else:
                flash('Invalid join code.', 'danger')

        else: 
            if action == "create" and create_form.errors:
                flash(f"Could not create household. Please correct the errors: {', '.join([err for field_errors in create_form.errors.values() for err in field_errors])}", "danger")
            elif action == "join" and join_form.errors:
                flash(f"Could not join household. Please correct the errors: {', '.join([err for field_errors in join_form.errors.values() for err in field_errors])}", "danger")
            elif not action and request.form: 
                flash("Invalid form submission detected.", "danger")
    
    initial_active_tab = 'join' 
    post_action = request.form.get("action") if request.method == "POST" else None
    if post_action == "create":
        initial_active_tab = 'create'
    elif request.method == "GET" and request.args.get('tab') == 'create':
        initial_active_tab = 'create'
            
    return render_template('household/setup.html', join_form=join_form, create_form=create_form, initial_active_tab=initial_active_tab)
     
@household_bp.route('/manage/<int:household_id>')
@login_required
def manage_household(household_id):
    """
    Displays the admin-only management page for a household.

    Only accessible to the admin of the household.
    """

    if not household_id:
        flash("Access denied!", "danger")
        return redirect(url_for("main.index"))

    household = current_user.household
    if not household or not current_user.id == household.admin_id:
        flash("Access denied!", "danger")
        return redirect(url_for("main.index"))
    
    members =household.members 
    return render_template('household/manage.html', household=household, members=members)

@household_bp.route('/remove_member/<int:user_id_to_remove>', methods=["POST"]) 
@login_required
def remove_member(user_id_to_remove):
    """
    Allows the household admin to remove a member from the household.

    Returns:
        JSON response with success or error messages.
    """

    admin = current_user
    household = admin.household

    if not household:
        return jsonify({'success': False, 'error': "You are not in a household."}), 400
    
    if not admin.id == household.admin_id:
        return jsonify({'success': False, 'error': "Unauthorized: Only the household admin can remove members."}), 403

    member_to_remove = UsersModel.query.get(user_id_to_remove)

    if not member_to_remove:
        return jsonify({'success': False, 'error': "User to remove not found."}), 404
    
    if member_to_remove.household_id != household.id:
        return jsonify({'success': False, 'error': "This user is not a member of your current household."}), 400
    
    if member_to_remove.id == admin.id:
        return jsonify({'success': False, 'error': "You cannot remove yourself using this function. Use 'Leave Household' instead."}), 400

    removed_member_username = member_to_remove.username 
    household_id_for_log = household.id

    member_to_remove.household_id = None
    if hasattr(member_to_remove, 'role'):
        member_to_remove.role = None
    db.session.add(member_to_remove)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logging.exception(f"Error removing member {user_id_to_remove} from household {household_id_for_log}: {e}")
        return jsonify({'success': False, 'error': "A server error occurred while removing the member."}), 500

    try:
        log_activity(
            user_id=admin.id,
            household_id=household_id_for_log,
            action_type="Member Removal",
            timestamp=datetime.now(tz)
        )
    except Exception as e:
        logging.exception(f"Failed to log member removal activity: {e}")

    return jsonify({
        "success": True,
        "message": f"Member '{removed_member_username}' has been successfully removed from the household.",
        "removed_user_id": user_id_to_remove 
    }), 200

@household_bp.route('/rename/<int:household_id>', methods=["POST"])
@login_required
def rename(household_id):
    """
    Renames the household. Only accessible by the admin.

    Expects:
        JSON payload with key `new_name`.
    """

    if not household_id:
        return jsonify ({'error': "Unauthorised!"}), 403
    
    household = current_user.household
    data = request.get_json()

    if not household or not current_user.id == household.admin_id:
        return jsonify ({'error': "Unauthorised!"}), 403
    
    new_name = data.get('new_name')
    if new_name:
        household.name = new_name
        db.session.commit()
        try:
            log_activity(user_id=current_user.id,
                         household_id=current_user.household.admin_id,
                         action_type="Household Renaming",
                         timestamp=datetime.now(tz),
                         new_name=new_name)
        except Exception as e:

            logging.exception(f"Failed to log activity: {e}")

        return jsonify({ 'success': True, 'message': 'Household renamed successfully', 'new_name': new_name}), 200
    else:
        return jsonify ({'error': "New name is required!"}), 400

@household_bp.route('/delete/<int:household_id>', methods=["POST"])
@login_required
def delete(household_id):
    """
    Deletes a household along with detaching its members.

    Only the admin can perform this action.
    """

    household = current_user.household

    if not household:
        return jsonify({'error': "You are not part of any household to delete."}), 404 
    
    if not household_id:
        return jsonify({'error': "You are not part of any household to delete."}), 404 

    if not current_user.id == household.admin_id:
        return jsonify({'error': "Unauthorized. Only the household admin can delete the household."}), 403

    household_id_for_log = household.id

    members_to_remove = list(household.members)
    for member in members_to_remove:
        member.household_id = None
        member.role = None  
        db.session.add(member) 

    db.session.delete(household) 
    
    try:
        db.session.commit() 
    except Exception as e:

        db.session.rollback()
        logging.exception(f"Error committing household deletion for household ID {household_id_for_log}: {e}")
        return jsonify({'error': "A server error occurred while trying to delete the household."}), 500

    try:
        log_activity(
            user_id=current_user.id,
            household_id=household_id_for_log, 
            action_type="Household Deletion",
            timestamp=datetime.now(tz))
    except Exception as e:

        logging.exception(f"CRITICAL: Failed to log household deletion activity for household ID {household_id_for_log} (user: {current_user.id}), but household was deleted. Error: {e}")
        log_action_message += " Logging failed (see server logs)."

    return jsonify({
        "success": True,
        "message": log_action_message, 
        "redirect_url": url_for('household_bp.setup')
    }), 200


@household_bp.route('/regenerate_code', methods=["POST"])
@login_required
def regenerate_code():
    """
    Regenerates the household join code.

    Admin-only.
    """
  
    try:
        household = current_user.household
        if not household or not current_user.id == household.admin_id:
            return jsonify({'error': "Unauthorized!"}), 403
        
        household.join_code = secrets.token_hex(4).upper()
        db.session.commit()
        return jsonify({"success": True, "new_code": household.join_code}), 200
    
    except Exception as e:
        logging.exception(f"Error in regenerating join code: {e}")
        return jsonify({'error': "Server error occurred"}), 500


@household_bp.route('/leave', methods=["POST"])
@login_required
def leave():
    """
    Allows a user to leave a household.

    If the user is an admin, ownership is transferred to another member (if any).
    Otherwise, the user is removed from the household.
    Does not allow the last member to leave.
    """

    user_to_leave = current_user
    household_to_be_left = user_to_leave.household


    if not household_to_be_left:
        return jsonify({'success': False, 'error': "You are not in a household!"}), 400

    household_id_for_log = current_user.household_id
    household_name_for_log = household_to_be_left.name

    if household_to_be_left.admin_id == user_to_leave.id:  
        other_members = UsersModel.query.filter(
            UsersModel.household_id == household_id_for_log,
            UsersModel.id != user_to_leave.id
        ).order_by(UsersModel.id).all()

        if not other_members:
            flash("You are the only member in this household. To disband it, please use the 'Delete Household' option.")
            return redirect('main.dashboard')
        else:
            new_admin = other_members[0]
            household_to_be_left.admin_id = new_admin.id
            if hasattr(new_admin, 'role'): 
                new_admin.role = 'admin'
                db.session.add(new_admin)
            
            user_to_leave.household_id = None
            if hasattr(user_to_leave, 'role'):
                user_to_leave.role = None 
            
            db.session.add(user_to_leave)
            db.session.add(household_to_be_left) 

            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                logging.exception(f"Error during admin leave & transfer for household {household_id_for_log}: {e}")
                return jsonify({'success': False, 'error': "A server error occurred during the admin transfer process."}), 500

            try:
                log_activity(
                    user_id=user_to_leave.id,
                    household_id=household_id_for_log,
                    action_type= "Admin Leaving",
                    timestamp=datetime.now(tz),
                    new_name=new_admin.username
                )
            except Exception as e:
                logging.exception(f"Failed to log admin leave and transfer activity: {e}")

            return jsonify({
                "success": True,
                "message": f"You have left '{household_name_for_log}'. {new_admin.username} is now the administrator.",
                "redirect_url": url_for('household_bp.setup')
            }), 200
    else:
        # Regular member leaving
        user_to_leave.household_id = None
        if hasattr(user_to_leave, 'role'):
            user_to_leave.role = None
        db.session.add(user_to_leave)

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logging.exception(f"Error during member leave for household {household_id_for_log}: {e}")
            return jsonify({'success': False, 'error': "A server error occurred while leaving the household."}), 500
        
        try:
            log_activity(
                user_id=user_to_leave.id,
                household_id=household_id_for_log,
                action_type="Household Leaving",
                timestamp=datetime.now(tz)
            )
        except Exception as e:
            logging.exception(f"Failed to log member leave activity: {e}")

        return jsonify({
            "success": True,
            "message": f"You have successfully left '{household_name_for_log}'.",
            "redirect_url": url_for('household_bp.setup') 
        }), 200
    
@household_bp.route('/view/<int:household_id>', methods=["GET"])
@login_required
def view(household_id):
    """
    Displays household details based on user's role.

    Admin: Sees the manage page.
    Member: Sees the member view page.
    """

    if not current_user.household_id:
        flash('You must be in a household.')
        return redirect(url_for('household_bp.setup'))
    
    household =HouseholdModel.query.get_or_404(household_id)
    
    if not current_user.household_id == household_id:
        flash('Access Denied')
        return jsonify({"success": False, "message": "You do not belong to this household."}), 403
    
    members = household.members 
    
    if current_user.id == household.admin_id:
        return render_template('household/manage.html', members=members, household=household)
    else:
        return render_template('household/view.html', members=members, household=household)

    