from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired,Length, EqualTo

class PasswordChangeForm(FlaskForm):
    current_password = StringField('Current Password', validators=[DataRequired("You must enter password"), Length(min=6)])
    new_password = StringField('New Password', validators=[DataRequired("You must enter password"), Length(min=6)])
    confirm_new_password = StringField('Confirm New Password', validators=[DataRequired("You must enter password"), Length(min=6), EqualTo('new_password', message='Passwords must match')])
    submit = SubmitField('Change Password')

class NameChangeForm(FlaskForm):
    current_name = StringField('Current Name', validators=[DataRequired("You must enter name"), Length(min=2)])
    new_name = StringField('New Name', validators=[DataRequired("You must enter name"), Length(min=2)])
    submit = SubmitField('Change Display Name')    

class ProfilePictureForm(FlaskForm):
    picture = SelectField('Choose a Profile Picture', choices=[
        ('default.png', 'Default'),
        ('1.png', '1'),
        ('2.png', '2'),
        ('3.png', '3'),
        ('4.png', '4'),
        ('5.png', '5'),
    ])
    new_name = StringField('New Name', validators=[DataRequired("You must enter name"), Length(min=2)])
    submit = SubmitField('Change Profile Picture')    