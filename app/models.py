# models.py
from flask import url_for
from app.extensions import db
from flask_login import UserMixin
from datetime import datetime, timezone
import secrets


class User(db.Model, UserMixin):
    __tablename__ = 'users' 
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='member')
    avatar_url = db.Column(db.String(256), nullable=True)  # Can be DiceBear URL or local path
    def get_avatar_url(self):
        if self.avatar_url:
            # Assuming you're storing uploads in 'static/uploads/avatars/<filename>'
            return url_for('static', filename=f'uploads/avatars/{self.avatar_url}')
        else:
            # Return a DiceBear avatar URL (you can customize this style)
            return f"https://api.dicebear.com/7.x/initials/svg?seed={self.username}"

    household_id = db.Column(db.Integer, db.ForeignKey('households.id'))
    household = db.relationship('Household', back_populates='members', foreign_keys=[household_id])
    administered_household = db.relationship('Household', back_populates='admin',foreign_keys='Household.admin_id', uselist=False)
    created_lists = db.relationship('ShoppingList', backref='creator', lazy=True)
    added_items = db.relationship('ListItem', backref='added_by', lazy=True)
    activities = db.relationship('ActivityLog', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'

class Household(db.Model):
    __tablename__ = 'households'
    id = db.Column(db.Integer, primary_key=True)
    join_code = db.Column(db.String(36), unique=True, nullable=False, default=lambda: secrets.token_hex(4).upper())
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    admin_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    admin = db.relationship('User', back_populates='administered_household', foreign_keys=[admin_id])
    members = db.relationship('User', back_populates='household', lazy=True, foreign_keys='User.household_id')
    shopping_lists = db.relationship('ShoppingList', backref='household', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Household {self.name} ({self.join_code})>'

class ShoppingList(db.Model):
    __tablename__ = 'shoppinglists'  # Explicitly set table name
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    household_id = db.Column(db.Integer, db.ForeignKey('households.id'), nullable=False)
    created_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    items_count = db.Column(db.Integer, default=0)
    purchased_items_count = db.Column(db.Integer, default=0)
    items = db.relationship('ListItem', backref='shopping_list', lazy=True, cascade="all, delete-orphan")
    

    def __repr__(self):
        return f'<ShoppingList {self.name}>'

class ListItem(db.Model):
    __tablename__ = 'listitems'  # Explicitly set table name
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    measure = db.Column(db.String(10), nullable=True, default='')
    shoppinglist_id = db.Column(db.Integer, db.ForeignKey('shoppinglists.id'), nullable=False)
    added_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    purchased = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<ListItem {self.name}>'
    
class ActivityLog(db.Model):
    __tablename__ = 'activity_log'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    household_id = db.Column(db.Integer, db.ForeignKey('households.id'), nullable=False)
    action_type = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now(timezone.utc))
