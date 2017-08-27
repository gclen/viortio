from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(80), index=True, unique=True)
    password_hash = db.Column(db.String(256))
    tasks = db.relationship('Task', backref='author', lazy='dynamic')

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return unicode(self.id)
        except NameError:
            return str(self.id)

    def __repr__(self):
        return '<User {}>'.format(self.nickname)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(140), index=True)
    start_date = db.Column(db.DateTime, index=True)
    due_date = db.Column(db.DateTime, index=True)
    project = db.Column(db.String(140), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    status = db.Column(db.String(80), index=True, default='Incomplete')

    def __repr__(self):
        return 'Task is: {}'.format(self.name)

