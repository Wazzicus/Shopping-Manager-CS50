# utils.py
from app.extensions import db
from app.models import ActivityLog

def log_activity(user_id, household_id, action_type):
    activity = ActivityLog(
        user_id=user_id,
        household_id = household_id,
        action_type =action_type
    )
    db.session.add(activity)
    db.session.commit()

def format_action(action_type):
    if action_type == "Item Addition":
        return "Added an item"
    elif action_type == "Item Deletion":
        return "Deleted an item"
    elif action_type == "Item Renaming":
        return "Renamed an item"
    elif action_type == "Household Creation":
        return "Created the household" 
    elif action_type == "Household Renaming":
        return "Renamed the household"
    elif action_type == "Household Joining":
        return "Joined the household"
    elif action_type == "Household Leaving":
        return "Left the household"
    elif action_type == "Member Removal":
        return "Was Removed"
    elif action_type == "List Creation":
        return "Created a new list"
    elif action_type == "List Deletion":
        return "Deleted the list: "
    elif action_type == "List Renaming":
        return "Renamed the list:"
    elif action_type == "Mark as Purchased":
        return "Marked an item as purchased"
    else:
        return f"Performed the action: {action_type}"