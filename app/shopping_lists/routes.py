# shopping_lists/routes.py
from flask import Blueprint, render_template, url_for, flash, redirect, abort, jsonify, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models import ShoppingList as ShoppingListModel, ListItem as ListItemModel
from app.shopping_lists.forms import AddItemForm, EditShoppingListForm, EditItemForm, ShoppingListForm
import logging
from app.utils import log_activity

shoppinglist_bp = Blueprint('shoppinglist_bp', __name__)

@shoppinglist_bp.route('/create_list', methods=['POST'])
@login_required
def create_list():
    """Handle creation of new shopping lists via both AJAX and form submissions."""
    if not current_user.household_id:
        if request.is_json:
            return jsonify({
                "success": False,
                "message": "You must belong to a household to create a list."
            }), 403
        flash('You must belong to a household to create a list.', 'error')
        return redirect(url_for('main.dashboard'))

    # Handle both AJAX and form submissions
    if request.method == 'POST':
        is_ajax = request.is_json
        list_name = None

        # Get list name based on request type
        if is_ajax:
            data = request.get_json()
            list_name = data.get('name', '').strip()
        else:
            list_name = request.form.get('name', '').strip()

        # Validate list name
        if not list_name:
            if is_ajax:
                return jsonify({
                    "success": False,
                    "message": "List name cannot be empty."
                }), 400
            flash('List name cannot be empty.', 'error')
            return redirect(url_for('main.dashboard'))

        if len(list_name) > 50:
            if is_ajax:
                return jsonify({
                    "success": False,
                    "message": "List name cannot exceed 50 characters."
                }), 400
            flash('List name cannot exceed 50 characters.', 'error')
            return redirect(url_for('main.dashboard'))

        # Check for duplicate list names
        existing_list = ShoppingListModel.query.filter(
            db.func.lower(ShoppingListModel.name) == db.func.lower(list_name),
            ShoppingListModel.household_id == current_user.household_id,
        ).first()

        if existing_list:
            if is_ajax:
                return jsonify({
                    "success": False,
                    "message": f"A list named '{list_name}' already exists."
                }), 400
            flash(f"A list named '{list_name}' already exists.", 'error')
            return redirect(url_for('main.dashboard'))

        # Create new list
        try:
            new_list = ShoppingListModel(
                name=list_name,
                created_by_user_id=current_user.id,
                household_id=current_user.household_id
            )
            db.session.add(new_list)
            db.session.commit()

            # Log activity
            try:
                log_activity(
                    user_id=current_user.id,
                    household_id=current_user.household_id,
                    action_type="List Creation",
                    list_name=new_list.name  
                )
            except Exception as e:
                logging.error(f"Failed to log activity: {e}")

            # Return appropriate response
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

            # For form submission, redirect to the new list
            return redirect(url_for('shoppinglist_bp.view_list', list_id=new_list.id))

        except Exception as e:
            db.session.rollback()
            logging.error(f"Error creating list: {e}")
            if is_ajax:
                return jsonify({
                    "success": False,
                    "message": "An error occurred while creating the list."
                }), 500
            flash('An error occurred while creating the list.', 'error')
            return redirect(url_for('main.dashboard'))

    # GET request - show the form
    new_list_form = ShoppingListForm()
    return render_template('dashboard.html',
                         title="Dashboard",
                         new_list_form=new_list_form)
    


@shoppinglist_bp.route('/list/<int:list_id>', methods=['GET', 'POST'])
@login_required
def view_list(list_id):
    shopping_list = ShoppingListModel.query.get_or_404(list_id)

    if not current_user.household or shopping_list.household_id != current_user.household_id:
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
             return jsonify({"success": False, "message": "Forbidden"}), 403
        abort(403)

    item_form = AddItemForm()

    if request.method == 'POST':
        is_ajax = request.is_json 

        if is_ajax:
            # --- AJAX / JSON Handling ---
            data = request.get_json()
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
                try:
                    log_activity(user_id=current_user.id,
                                 household_id=current_user.household_id,
                                 action_type="Item Addition",
                                 item_name=new_item)
                except Exception as e:
                    logging.error(f"Failed to log activity: {e}")
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

        else:
            # --- Standard Form Submission Handling ---
            if item_form.validate_on_submit():
                try:
                    new_item = ListItemModel(name=item_form.name.data,
                                        shoppinglist_id=list_id,
                                        quantity=item_form.quantity.data, 
                                        measure=item_form.measure.data,  
                                        added_by_user_id=current_user.id)
                    db.session.add(new_item)
                    db.session.commit()
                    try:
                        log_activity(user_id=current_user.id,
                                     household_id=current_user.household_id,
                                     action_type="Item Addition",
                                     item_name=new_item.name)
                    except Exception as e:
                        logging.error(f"Failed to log activity: {e}")
                    return redirect(url_for('shoppinglist_bp.view_list', list_id=list_id))
                except Exception as e:
                     db.session.rollback()
                     flash('Error adding item to database.', 'danger')
                     logging.error(f"Error adding item via Standard Form Submission: {e}")

    # --- GET Request  ---
    items = ListItemModel.query.filter_by(shoppinglist_id=list_id).order_by(ListItemModel.added_at.asc()).all()
    total_items = len(items)
    purchased_items = sum(1 for item in items if item.purchased)
    completion_percentage = (purchased_items / total_items) * 100 if total_items > 0 else 0

    return render_template('shopping/view_list.html',
                        title=shopping_list.name,
                        shopping_list=shopping_list,
                        items=items,
                        item_form=item_form,
                        completion_percentage=completion_percentage)

@shoppinglist_bp.route('/list/<int:list_id>/edit', methods=['GET','POST'])
@login_required
def edit_list(list_id):
    shopping_list = ShoppingListModel.query.get_or_404(list_id)
    if not current_user.household or shopping_list.household_id != current_user.household_id:
        abort(403)
    form = EditShoppingListForm(obj=shopping_list)
    if form.validate_on_submit():
        shopping_list.name=form.name.data
        db.session.commit()
        flash(f'List "{shopping_list.name}" updated.', 'success')
        try:
            log_activity(user_id=current_user.id, 
                         household_id=current_user.household_id,
                         action_type="List Renaming",
                         new_name=form.name.data)
        except Exception as e:
            logging.error(f"Failed to log activity: {e}")
        return redirect(url_for('shoppinglist_bp.view_list',list_id=list_id))

    return render_template('shopping/edit_list.html', title=f'Edit List: {shopping_list.name}', form=form, shopping_list=shopping_list)

@shoppinglist_bp.route('/list/<int:list_id>/delete', methods=['GET','POST'])
@login_required
def delete_list(list_id):
    shopping_list = ShoppingListModel.query.get_or_404(list_id)
    if not current_user.household or shopping_list.household_id != current_user.household_id:
      return jsonify({"success": False, "message": "Forbidden"}), 403

    try:
        list_name = shopping_list.name 
        db.session.delete(shopping_list)
        db.session.commit()
        try:
            log_activity(user_id=current_user.id,
                         household_id=current_user.household_id,
                         action_type="List Deletion",
                         list_name=list_name)
        except Exception as e:
            logging.error(f"Failed to log activity: {e}")

        return jsonify({
            "success": True,
            "message": f'"{list_name}" deleted.'
        })
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error deleting list: {e}")
        return jsonify({"success": False, "message": "Error deleting list."}), 500


# --- List Item Routes --- 
@shoppinglist_bp.route('/list/item/<int:item_id>/edit', methods=['GET','POST'])
@login_required
def edit_item(item_id):
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
        try:
            log_activity(user_id=current_user.id,
                        household_id=current_user.household_id, 
                        action_type="Item Editing",
                        new_name=form.name.data
                        )
        except Exception as e:
            logging.error(f"Failed to log activity: {e}")
        return redirect(url_for('shoppinglist_bp.view_list',list_id=item.shoppinglist_id))
    return render_template('shopping/edit_item.html', form=form, item=item)

@shoppinglist_bp.route('/list/item/<int:item_id>/delete', methods=['POST', 'GET'])
@login_required
def delete_item(item_id):
    item = ListItemModel.query.get_or_404(item_id)

    if item.shopping_list.household_id != current_user.household_id:
        return jsonify({"success": False, "message": "Forbidden"}), 403

    item_name = item.name  
    try:
        db.session.delete(item)
        db.session.commit()

        try:
            log_activity(
                user_id=current_user.id,
                household_id=current_user.household_id,
                action_type="Item Deletion",
                item_name=item_name
            )
        except Exception as e:
            logging.error(f"Failed to log activity: {e}")

        return jsonify({"success": True, "message": f'"{item_name}" deleted. Refresh to see changes'})

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error deleting item '{item_name}': {e}")
        return jsonify({"success": False, "message": "Error deleting item."}), 500



@shoppinglist_bp.route('/list/item/<int:item_id>/toggle_purchase', methods=['POST'])
@login_required
def toggle_purchase(item_id):
    item = ListItemModel.query.get_or_404(item_id)
    if item.shopping_list.household_id != current_user.household_id:
        return jsonify({"success": False,
                        "message": "Forbidden"}), 403
    try:
        item.purchased = not item.purchased
        db.session.commit()
        try:
            log_activity(user_id=current_user.id, household_id=current_user.household_id, action_type="Mark as Purchased")
        except Exception as e:
            logging.error(f"Failed to log activity: {e}")
        return jsonify({"success": True,
                        "item_id": item.id,
                        "purchased_status": item.purchased,
                        "message":f'Item "{item.name}" marked as {"purchased" if item.purchased else "not purchased"}.'
                          }), 200
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error toggling purchase status for item {item.name}: {e}")

    return jsonify({"success": False,
                        "message": "Error updating item status."}), 500

@shoppinglist_bp.route('/list/item/<int:item_id>/update_name', methods=['POST'])
@login_required
def update_item_name(item_id):
    item = ListItemModel.query.get_or_404(item_id)

    if not current_user.household or item.shopping_list.household_id != current_user.household_id:
        return jsonify({"success": False, "message": "Forbidden"}), 403
    
    if not request.is_json:
        return jsonify({"success": False, "message": "Invalid request: Content-Type must be application/json"}), 415 # Unsupported Media Type

    data = request.get_json()
    new_name = data.get('new_name', '').strip()

    if not new_name:
        return jsonify({"success": False, "message": "New item name cannot be empty."}), 400 
    if len(new_name) > 100: 
        return jsonify({"success": False, "message": "New item name is too long."}), 400
    try:
        item.name = new_name
        db.session.commit()
        try:
            log_activity(user_id=current_user.id,
                         household_id=current_user.household_id,
                         action_type="Item Renaming",
                         new_name=new_name)
        except Exception as e:
            logging.error(f"Failed to log activity: {e}")
        return jsonify({
            "success": True,
            "new_name": item.name,
            "message": "Item name updated successfully."
        })
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error updating item name for item {item_id}: {e}") 
        return jsonify({"success": False, "message": "Database error updating item name."}), 500
