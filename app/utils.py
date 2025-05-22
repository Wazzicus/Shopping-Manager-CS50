"""
utils.py

This module contains utility functions for the Shopping Manager app:
- Logging user activities to the database
- Formatting human-readable descriptions for those activities
"""

from app.extensions import db
from app.models import ActivityLog


def log_activity(user_id, household_id, action_type, timestamp, item_name=None, list_name=None, new_name=None, old_name=None):
    """
    Logs an action performed by a user into the ActivityLog table.

    """
    activity = ActivityLog(
        user_id=user_id,
        household_id=household_id,
        action_type=action_type,
        timestamp = timestamp
    )
    db.session.add(activity)
    db.session.commit()


def format_action(action_type, item_name=None, list_name=None, new_name=None, old_name=None):
    """
    Generates a human-readable string that describes a logged activity.

    Args:
        action_type (str): Type of action performed.
        item_name (str, optional): Name of the item involved.
        list_name (str, optional): Name of the list involved.
        new_name (str, optional): New name used in renaming.
        old_name (str, optional): Old name used in renaming.

    Returns:
        str: A formatted message describing the action.
    """
    if action_type == "Item Addition":
        return f"Added '{item_name}' to the list." if item_name else "Added an item."

    elif action_type == "Item Deletion":
        return f"Deleted '{item_name}' from {list_name}." if item_name else "Deleted an item."

    elif action_type == "Item Renaming":
        if old_name and new_name:
            return f"Renamed '{old_name}' to '{new_name}'."
        elif new_name:
            return f"Renamed an item to '{new_name}'."
        else:
            return "Renamed an item."

    elif action_type == "Household Creation":
        return "Created the household."

    elif action_type == "Household Renaming":
        if old_name and new_name:
            return f"Renamed the household from '{old_name}' to '{new_name}'."
        elif new_name:
            return f"Renamed the household to '{new_name}'."
        else:
            return "Renamed the household."

    elif action_type == "Household Joining":
        return "Joined the household."

    elif action_type == "Household Leaving":
        return "Left the household."

    elif action_type == "Member Removal":
        return "Was removed from the household."

    elif action_type == "List Creation":
        return f"Created a new list: '{list_name}'." if list_name else "Created a new list."

    elif action_type == "List Deletion":
        return f"Deleted the list: '{list_name}'." if list_name else "Deleted a list."

    elif action_type == "List Renaming":
        if old_name and new_name:
            return f"Renamed the list from '{old_name}' to '{new_name}'."
        elif new_name:
            return f"Renamed the list to '{new_name}'."
        else:
            return "Renamed the list."

    elif action_type == "Mark as Purchased":
        return f"Marked '{item_name}' as purchased." if item_name else "Marked an item as purchased."

    elif action_type == "Admin Leaving":
        return f"(Admin) left the household, transferred to {new_name}"
    
    elif action_type == "Name Change":
        if old_name and new_name:
            return f"Changed their name from '{old_name}' to '{new_name}'."
        elif new_name:
            return f"Changed their name to '{new_name}'."
        else:
            return "Changed their name."
        
    else:
        return f"Performed the action: {action_type}"
