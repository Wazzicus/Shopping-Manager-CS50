from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired,Length

class ShoppingListForm(FlaskForm):
    name = StringField('List Name', validators=[DataRequired()])
    submit = SubmitField('Create List')


class AddItemForm(FlaskForm):
    name = StringField('Item Name', validators=[DataRequired("You must choose a name"), Length(min=2, max=100)])
    quantity = IntegerField('Quantity', default=1)
    measure = StringField('Measure', validators=[Length(min=1, max=5)])
    submit = SubmitField('Add Item')

class EditShoppingListForm(FlaskForm):
    name = StringField('List Name', validators=[DataRequired("You must choose a name"), Length(min=2, max=100)])
    submit = SubmitField('Save Changes')

class EditItemForm(FlaskForm):
    name = StringField('Item Name', validators=[DataRequired("You must choose a name"), Length(min=2, max=100)])
    quantity = IntegerField('Quantity', validators=[DataRequired("You must choose a name")])
    measure = StringField('Measure', validators=[DataRequired("You must choose a name"),Length(min=1, max=5)])
    submit = SubmitField('Save Changes')    
