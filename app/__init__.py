from flask import Flask
from flask_babel import Babel
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import basedir

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
babel = Babel(app)
lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'


@app.template_filter('datetimeformat')
def datetime_format(value, format='%m-%d-%Y'):
    return value.strftime(format)

app.jinja_env.filters['datetimeformat'] = datetime_format

from app import views, models

