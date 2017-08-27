from flask_wtf import FlaskForm
from wtforms import StringField, DateField, validators

class TaskForm(FlaskForm):
    task = StringField('Task', [validators.DataRequired('Please enter the task')])
    due_date = DateField('Due date', [validators.Optional()])
    start_date = DateField('Start date', [validators.Optional()])











