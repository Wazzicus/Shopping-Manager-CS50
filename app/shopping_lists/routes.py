"""
shopping_lists/routes.py

This blueprint handles all routes related to managing shopping lists and their items.
Includes:
- Creating, editing, deleting, viewing lists
- Adding, editing, deleting, renaming, toggling items
- AJAX and HTML form compatibility
"""

from flask import Blueprint, render_template, url_for, flash, redirect, abort, jsonify, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models import ShoppingList as ShoppingListModel, ListItem as ListItemModel
from app.shopping_lists.forms import AddItemForm, EditShoppingListForm, EditItemForm
from app.utils import log_activity
import logging
from datetime import datetime
from tzlocal import get_localzone

tz = get_localzone()

shoppinglist_bp = Blueprint('shoppinglist_bp', __name__)


@shoppinglist_bp.route('/create_list', methods=['POST'])
@login_required
def create_list():
    """
    Create a new shopping list for the current user's household.
    Handles both standard form submissions and AJAX requests.
    """
    if not current_user.household_id:
        msg = "You must belong to a household to create a list."
        if request.is_json:
            return jsonify({"success": False, "message": msg}), 403
        flash(msg, 'error')
        return redirect(url_for('main.dashboard'))

    is_ajax = request.is_json
    list_name = request.get_json().get('name', '').strip() if is_ajax else request.form.get('name', '').strip()

    if not list_name:
        msg = "List name cannot be empty."
        return jsonify({"success": False, "message": msg}), 400 if is_ajax else flash(msg, 'error')

    if len(list_name) > 50:
        msg = "List name cannot exceed 50 characters."
        return jsonify({"success": False, "message": msg}), 400 if is_ajax else flash(msg, 'error')

    # Check for duplicate names
    existing_list = ShoppingListModel.query.filter(
        db.func.lower(ShoppingListModel.name) == list_name.lower(),
        ShoppingListModel.household_id == current_user.household_id
    ).first()

    if existing_list:
        msg = f"A list named '{list_name}' already exists."
        return jsonify({"success": False, "message": msg}), 400 if is_ajax else flash(msg, 'error')

    try:
        new_list = ShoppingListModel(
            name=list_name,
            created_by_user_id=current_user.id,
            household_id=current_user.household_id
        )
        db.session.add(new_list)
        db.session.commit()
        log_activity(user_id=current_user.id, household_id=current_user.household_id, action_type="List Creation", timestamp=datetime.now(tz), list_name=new_list.name)

        if is_ajax:
            return jsonify({
                "success": True,
                "message": f'List "{new_list.name}" created successfully!',
                "list": {
                    "id": new_list.id,
                    "name": new_list.name,
                    "created_at": new_list.created_at.isoformat(),
                    "items_count": 0
                }
            }), 201
        return redirect(url_for('shoppinglist_bp.view_list', list_id=new_list.id))

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error creating list: {e}")
        msg = "An error occurred while creating the list."
        return jsonify({"success": False, "message": msg}), 500 if is_ajax else flash(msg, 'error')


@shoppinglist_bp.route('/list/<int:list_id>', methods=['GET', 'POST'])
@login_required
def view_list(list_id):
    """
    View a specific shopping list and its items.
    Allows adding items via form or AJAX.
    """
    shopping_list = ShoppingListModel.query.get_or_404(list_id)
    if not current_user.household or shopping_list.household_id != current_user.household_id:
        return jsonify({"success": False, "message": "Forbidden"}), 403 if request.is_json else abort(403)

    item_form = AddItemForm()

    if request.method == 'POST':
        is_ajax = request.is_json
        data = request.get_json() if is_ajax else None

        # --- Handle AJAX Submission ---
        if is_ajax:
            item_name = data.get('name', '').strip()
            quantity = data.get('quantity', 1)
            measure = data.get('measure', '')

            if not item_name:
                return jsonify({"success": False, "message": "Item name cannot be empty."}), 400

            try:
                new_item = ListItemModel(
                    name=item_name,
                    shoppinglist_id=list_id,
                    added_by_user_id=current_user.id,
                    quantity=quantity,
                    measure=measure
                )
                db.session.add(new_item)
                db.session.commit()
                log_activity(user_id=current_user.id, household_id=current_user.household_id, action_type="Item Addition", timestamp=datetime.now(tz) ,item_name=new_item.name)

                return jsonify({
                    "success": True,
                    "message": f'Item "{new_item.name}" added!',
                    "item": {
                        "id": new_item.id,
                        "name": new_item.name,
                        "purchased": new_item.purchased,
                        "added_by": {
                            "id": current_user.id,
                            "name": current_user.name,
                            "avatar_url": current_user.avatar_url
                        },
                        "quantity": new_item.quantity,
                        "measure": new_item.measure
                    }
                }), 201

            except Exception as e:
                db.session.rollback()
                logging.error(f"Error adding item via AJAX: {e}")
                return jsonify({"success": False, "message": "Error adding item to database."}), 500

        # --- Handle Standard Form Submission ---
        elif item_form.validate_on_submit():
            try:
                new_item = ListItemModel(
                    name=item_form.name.data,
                    shoppinglist_id=list_id,
                    quantity=item_form.quantity.data,
                    measure=item_form.measure.data,
                    added_by_user_id=current_user.id
                )
                db.session.add(new_item)
                db.session.commit()
                
                log_activity(user_id=current_user.id, household_id=current_user.household_id, action_type="Item Addition",timestamp= datetime.now(tz) ,item_name=new_item.name)
                return redirect(url_for('shoppinglist_bp.view_list', list_id=list_id))
            except Exception as e:
                db.session.rollback()
                flash("Error adding item to database.", "danger")
                logging.error(f"Error adding item via form: {e}")

    # --- GET Request: Render List View ---
    items = ListItemModel.query.filter_by(shoppinglist_id=list_id).order_by(ListItemModel.added_at.asc()).all()
    total_items = len(items)
    purchased_items = sum(1 for item in items if item.purchased)
    completion_percentage = (purchased_items / total_items) * 100 if total_items else 0

    return render_template(
        'shopping/view_list.html',
        title=shopping_list.name,
        shopping_list=shopping_list,
        items=items,
        item_form=item_form,
        completion_percentage=completion_percentage
    )


@shoppinglist_bp.route('/list/<int:list_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_list(list_id):
    """
    Rename a shopping list.
    """
    shopping_list = ShoppingListModel.query.get_or_404(list_id)
    if not current_user.household or shopping_list.household_id != current_user.household_id:
        abort(403)

    form = EditShoppingListForm(obj=shopping_list)
    if form.validate_on_submit():
        try:

            shopping_list.name = form.name.data
            db.session.commit()
            flash(f'List "{shopping_list.name}" updated.', 'success')
            log_activity(user_id=current_user.id, household_id=current_user.household_id, action_type="List Renaming", timestamp=datetime.now(tz), new_name=form.name.data)
            return redirect(url_for('shoppinglist_bp.view_list', list_id=list_id))
        
        except Exception as e:
            db.session.rollback()
            flash("Error adding item to database.", "danger")
            logging.error(f"Error adding item via form: {e}")


    return render_template('shopping/edit_list.html', title=f'Edit List: {shopping_list.name}', form=form, shopping_list=shopping_list)


@shoppinglist_bp.route('/list/<int:list_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_list(list_id):
    """
    Delete a shopping list.
    Supports JSON and HTML responses.
    """
    shopping_list = ShoppingListModel.query.get_or_404(list_id)
    if not current_user.household or shopping_list.household_id != current_user.household_id:
        return jsonify({"success": False, "message": "Forbidden"}), 403

    try:
        list_name = shopping_list.name
        db.session.delete(shopping_list)
        db.session.commit()

        log_activity(user_id=current_user.id, household_id=current_user.household_id, action_type="List Deletion", timestamp=datetime.now(tz), list_name=list_name)
        return jsonify({"success": True, "message": f'"{list_name}" deleted.'})
    except Exception as e:

        db.session.rollback()
        logging.error(f"Error deleting list: {e}")
        return jsonify({"success": False, "message": "Error deleting list."}), 500


@shoppinglist_bp.route('/list/item/<int:item_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_item(item_id):
    """
    Edit a list item's details.
    """
    item = ListItemModel.query.get_or_404(item_id)
    if item.shopping_list.household_id != current_user.household_id:
        abort(403)

    form = EditItemForm(obj=item)
    if form.validate_on_submit():
        item.name = form.name.data
        item.quantity = form.quantity.data
        item.measure = form.measure.data
        db.session.commit()

        flash(f'Item "{item.name}" updated.', 'success')
        log_activity(user_id=current_user.id, household_id=current_user.household_id, action_type="Item Editing", timestamp=datetime.now(tz), new_name=form.name.data)
        return redirect(url_for('shoppinglist_bp.view_list', list_id=item.shoppinglist_id))

    return render_template('shopping/edit_item.html', form=form, item=item)


@shoppinglist_bp.route('/list/item/<int:item_id>/delete', methods=['POST', 'GET'])
@login_required
def delete_item(item_id):
    """
    Delete a shopping list item.
    """
    item = ListItemModel.query.get_or_404(item_id)
    if item.shopping_list.household_id != current_user.household_id:
        return jsonify({"success": False, "message": "Forbidden"}), 403

    try:
        item_name = item.name
        db.session.delete(item)
        db.session.commit()

        log_activity(user_id=current_user.id, household_id=current_user.household_id, action_type="Item Deletion", timestamp=datetime.now(tz), item_name=item_name)
        return jsonify({"success": True, "message": f'"{item_name}" deleted. Refresh to see changes'})
    except Exception as e:

        db.session.rollback()
        logging.error(f"Error deleting item '{item_name}': {e}")
        return jsonify({"success": False, "message": "Error deleting item."}), 500


@shoppinglist_bp.route('/list/item/<int:item_id>/toggle_purchase', methods=['POST'])
@login_required
def toggle_purchase(item_id):
    """
    Toggle the 'purchased' status of a list item.
    """
    item = ListItemModel.query.get_or_404(item_id)
    if item.shopping_list.household_id != current_user.household_id:
        return jsonify({"success": False, "message": "Forbidden"}), 403

    try:
        item.purchased = not item.purchased
        db.session.commit()
        log_activity(user_id=current_user.id, household_id=current_user.household_id, action_type="Mark as Purchased", timestamp=datetime.now(tz))
        return jsonify({
            "success": True,
            "item_id": item.id,
            "purchased_status": item.purchased,
            "message": f'Item "{item.name}" marked as {"purchased" if item.purchased else "not purchased"}.'
        }), 200
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error toggling purchase status for item {item.name}: {e}")
        return jsonify({"success": False, "message": "Error updating item status."}), 500


@shoppinglist_bp.route('/list/item/<int:item_id>/update_name', methods=['POST'])
@login_required
def update_item_name(item_id):
    """
    Inline rename of a shopping list item (AJAX).
    """
    item = ListItemModel.query.get_or_404(item_id)
    if not current_user.household or item.shopping_list.household_id != current_user.household_id:
        return jsonify({"success": False, "message": "Forbidden"}), 403

    if not request.is_json:
        return jsonify({"success": False, "message": "Invalid request: Content-Type must be application/json"}), 415

    data = request.get_json()
    new_name = data.get('new_name', '').strip()

    if not new_name:
        return jsonify({"success": False, "message": "New item name cannot be empty."}), 400
    if len(new_name) > 100:
        return jsonify({"success": False, "message": "New item name is too long."}), 400

    try:
        item.name = new_name
        db.session.commit()
        log_activity(user_id=current_user.id, household_id=current_user.household_id, action_type="Item Renaming",timestamp=datetime.now(tz), new_name=new_name)
        return jsonify({"success": True, "new_name": item.name, "message": "Item name updated successfully."})
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error updating item name for item {item_id}: {e}")
        return jsonify({"success": False, "message": "Database error updating item name."}), 500
