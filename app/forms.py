import re
from flask_wtf import FlaskForm
from wtforms import StringField, DateField, PasswordField, BooleanField, validators, ValidationError
from .models import User

class LoginForm(FlaskForm):
    username = StringField('Username', [validators.DataRequired('Please enter your username')])
    password = PasswordField('Password', [validators.DataRequired('Please enter your password')])
    remember_me = BooleanField('remember_me', default=False)


class TaskForm(FlaskForm):
    task = StringField('Task', [validators.DataRequired('Please enter the task')])
    due_date = DateField('Due date', [validators.Optional()])
    start_date = DateField('Start date', [validators.Optional()])

class RegistrationForm(FlaskForm):
    username = StringField('Username', [validators.Length(min=4, max=80)])
    password = PasswordField('New password', [validators.DataRequired(),
                                              validators.EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Confirm password')

    def validate_username(form, field):
        if not re.match(r'^[\w_\-]+$', field.data):
            raise ValidationError('Username must only contain alphanumeric characters, underscores and hyphens')
        if User.query.filter_by(nickname=field.data).first():
            raise ValidationError('Username is taken. Please enter a unique username')





