from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField, RadioField, HiddenField, StringField
from wtforms.validators import Optional, DataRequired, Length,EqualTo
from flask_wtf.file import FileAllowed

class PasswordChangeForm(FlaskForm):
    current_password = StringField('Current Password', validators=[DataRequired("You must enter password"), Length(min=6)])
    new_password = StringField('New Password', validators=[DataRequired("You must enter password"), Length(min=6)])
    confirm_new_password = StringField('Confirm New Password', validators=[DataRequired("You must enter password"), Length(min=6), EqualTo('new_password', message='Passwords must match')])
    submit = SubmitField('Change Password')

class NameChangeForm(FlaskForm):
    current_name = StringField('Current Name', validators=[DataRequired("You must enter name"), Length(min=2)])
    new_name = StringField('New Name', validators=[DataRequired("You must enter name"), Length(min=2)])
    submit = SubmitField('Change Display Name')    


class AvatarForm(FlaskForm):
    dicebear_url = RadioField("Choose an Avatar", choices=[], validators=[Optional()])
    avatar_upload = FileField("Upload Profile Picture", validators=[
        FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')
    ])
    revert_avatar = HiddenField()  
    submit = SubmitField("Save Changes")
