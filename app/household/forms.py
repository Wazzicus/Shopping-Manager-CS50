from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length

class HouseholdCreationForm(FlaskForm):
    household_name = StringField('Household Name', validators=[DataRequired("You must choose a name"), Length(min=3, max=64)])
    submit = SubmitField('Create')

class HouseholdJoinForm(FlaskForm):
    join_code = StringField('Join Code', validators=[DataRequired("You must input a code!"), Length(min=4, max=10)])
    submit = SubmitField('Join')
