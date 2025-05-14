# routes.py
from flask import Blueprint, render_template, url_for, flash, redirect,request, jsonify
from flask_login import login_required, current_user
from app.models import Household as HouseholdModel, ShoppingList as ShoppingListModel, ActivityLog, ListItem as ListItemModel
from app.utils import format_action
from app.shopping_lists.forms import ShoppingListForm

main = Blueprint('main', __name__, template_folder="templates")

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/dashboard')
@login_required
def dashboard():
    new_list_form = ShoppingListForm() 
    household_id = current_user.household_id
    if not household_id:
        flash("You must join or create a household first.", "warning")
        return redirect(url_for('household_bp.setup')) 

    household = HouseholdModel.query.get(household_id) 
    if not household:
        flash("Household not found.", "danger")
        return redirect(url_for('main.dashboard')) 
    
    is_admin = (current_user.id == household.admin_id)

    
    all_household_lists = ShoppingListModel.query.filter_by(household_id=household_id)\
                                               .order_by(ShoppingListModel.created_at.desc())\
                                               .all()


    recent_activity = ActivityLog.query.filter_by(household_id=household_id)\
                                     .order_by(ActivityLog.timestamp.desc())\
                                     .limit(5)\
                                     .all()

    return render_template('dashboard.html',
                           title=f"Dashboard - {household.name}",
                           household=household, 
                           lists=all_household_lists, 
                           is_admin=is_admin,
                           recent_activity=recent_activity,
                           format_action=format_action ,
                           new_list_form=new_list_form
                           )

@main.route('/search_lists', methods=['GET'])
@login_required
def search_lists():
    query = request.args.get('q', '').strip()
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if not current_user.is_authenticated:
        return jsonify({'error': 'Unauthorized'}), 403

    # Adjust field name to match your actual model
    lists = ShoppingListModel.query.filter(
        ShoppingListModel.created_by_user_id == current_user.id,
        ShoppingListModel.name.ilike(f'%{query}%')
    ).all()

    if is_ajax:
        html = render_template('shopping/search_results.html', lists=lists)
        return jsonify({'html': html})

    # If it's a full GET (form submit), show them inside dashboard
    return render_template('dashboard.html', lists=lists, search_query=query)
