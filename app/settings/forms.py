from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField, RadioField, HiddenField, StringField, PasswordField
from wtforms.validators import Optional, DataRequired, Length,EqualTo
from flask_wtf.file import FileAllowed

class PasswordChangeForm(FlaskForm):
    old_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(),
        EqualTo('new_password', message='Passwords must match')
    ])
    submit = SubmitField('Change Password')

class NameChangeForm(FlaskForm):
    current_name = StringField('Current Name', validators=[DataRequired("You must enter name"), Length(min=2)])
    new_name = StringField('New Name', validators=[DataRequired("You must enter name"), Length(min=2)])
    submit = SubmitField('Change Display Name')    


class AvatarForm(FlaskForm):
    dicebear_url = RadioField("Choose an Avatar", choices=[], validators=[Optional()])
    avatar_upload = FileField("Upload Profile Picture", validators=[
        FileAllowed(['jpg', 'jpeg', 'png'], 'File format not supported!')
    ])
    revert_avatar = HiddenField()  
    submit = SubmitField("Save Changes")
