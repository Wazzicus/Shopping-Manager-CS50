from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, EqualTo, Length

class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired("Must not be empty!"),Length(min=2,max=10)], render_kw={"autocomplete":"off"})
    username = StringField('Username', validators=[DataRequired("Must not be empty!"),Length(min=2,max=10)], render_kw={"autocomplete":"off"})
    password = PasswordField('Password', validators=[DataRequired("Must not be empty!"),Length(min=6,max=10)], render_kw={"autocomplete":"new-password"})
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired("Must not be empty!"), EqualTo('password'), Length(min=6,max=10)], render_kw={"autocomplete":"new-password"})
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired("Must not be empty!")])
    password = PasswordField('Password', validators=[DataRequired("Must not be empty!")])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')
