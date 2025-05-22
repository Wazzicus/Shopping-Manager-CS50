"""
models.py

This module defines all database models for the Shopping Manager web app.

Models:
- User: Registered user with roles and avatar support
- Household: A shared group with members and shopping lists
- ShoppingList: A list of items belonging to a household
- ListItem: An individual item in a shopping list
- ActivityLog: Tracks user actions within a household
"""

from flask import url_for
from app.extensions import db
from flask_login import UserMixin
from datetime import datetime
from tzlocal import get_localzone
import secrets

tz = get_localzone()

class User(db.Model, UserMixin):
    """
    Represents a user account in the system.
    Users can be members or admins of a household and interact with lists/items.
    """
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='member')  # member or admin
    avatar_url = db.Column(db.String(256), nullable=True)  # DiceBear URL or uploaded file path

    # Relationships
    household_id = db.Column(db.Integer, db.ForeignKey('households.id'))
    household = db.relationship('Household', back_populates='members', foreign_keys=[household_id])
    administered_household = db.relationship('Household', back_populates='admin',
                                             foreign_keys='Household.admin_id', uselist=False)
    created_lists = db.relationship('ShoppingList', backref='creator', lazy=True)
    added_items = db.relationship('ListItem', backref='added_by', lazy=True)
    activities = db.relationship('ActivityLog', backref='user', lazy=True)

    def get_avatar_url(self):
        """
        Returns the appropriate avatar URL for the user.
        Prioritizes:
        1. Custom URL (external or local)
        2. Auto-generated DiceBear avatar (initials)
        """
        if not self.avatar_url:
            return f"https://api.dicebear.com/7.x/initials/svg?seed={self.username}"

        if self.avatar_url.startswith(('http://', 'https://')):
            return self.avatar_url

        return url_for('files_bp.uploaded_file', filename=self.avatar_url)

    def __repr__(self):
        return f'<User {self.username}>'


class Household(db.Model):
    """
    Represents a group of users (family, roommates, etc.) sharing shopping lists.
    Each household has one admin, many members, and multiple lists.
    """
    __tablename__ = 'households'

    id = db.Column(db.Integer, primary_key=True)
    join_code = db.Column(db.String(36), unique=True, nullable=False, default=lambda: secrets.token_hex(4).upper())
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(
    db.DateTime(timezone=True),
    default=lambda: datetime.now(tz)
    )

    admin_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    admin = db.relationship('User', back_populates='administered_household', foreign_keys=[admin_id])

    members = db.relationship('User', back_populates='household', lazy=True, foreign_keys='User.household_id')
    shopping_lists = db.relationship('ShoppingList', backref='household', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Household {self.name} ({self.join_code})>'


class ShoppingList(db.Model):
    """
    Represents a shopping list tied to a household.
    Each list has many items and is created by a user.
    """
    __tablename__ = 'shoppinglists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    household_id = db.Column(db.Integer, db.ForeignKey('households.id'), nullable=False)
    created_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(
    db.DateTime(timezone=True),
    default=lambda: datetime.now(tz)
    )

    items_count = db.Column(db.Integer, default=0)
    purchased_items_count = db.Column(db.Integer, default=0)

    items = db.relationship('ListItem', backref='shopping_list', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<ShoppingList {self.name}>'


class ListItem(db.Model):
    """
    Represents an individual item in a shopping list.
    Items are added by users and can be marked as purchased.
    """
    __tablename__ = 'listitems'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    measure = db.Column(db.String(10), nullable=True, default='')

    shoppinglist_id = db.Column(db.Integer, db.ForeignKey('shoppinglists.id'), nullable=False)
    added_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    added_at = db.Column(
    db.DateTime(timezone=True),
    default=lambda: datetime.now(tz)
    )
    purchased = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<ListItem {self.name}>'


class ActivityLog(db.Model):
    """
    Logs key user actions within a household for accountability and UX feedback.
    Example actions: item added, list updated, user joined household.
    """
    __tablename__ = 'activity_log'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    household_id = db.Column(db.Integer, db.ForeignKey('households.id'), nullable=False)
    action_type = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(
    db.DateTime(timezone=True),
    default=lambda: datetime.now(tz)
    )