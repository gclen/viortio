import json
from datetime import datetime
from sqlalchemy import desc
from app import db


class DatetimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.strftime('%Y-%m-%d %H:%M:%S')
        return json.JSONEncoder.default(self, o)


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
        return str(self.id)

    def get_tasklist(self):
        return Task.query.filter_by(user_id=self.id, complete=False).filter(Task.start_date <= datetime.utcnow()).order_by('start_date').all()

    def get_completed_tasks(self):
        return Task.query.filter_by(user_id=self.id, complete=True).order_by(desc('start_date')).all()

    def get_projects(self):
        return Task.query.with_entities(Task.project.distinct()).filter_by(user_id=self.id).filter(Task.project != None).order_by('project').all()


    def __repr__(self):
        return '<User {}>'.format(self.nickname)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(140), index=True)
    start_date = db.Column(db.DateTime, index=True)
    due_date = db.Column(db.DateTime, index=True)
    project = db.Column(db.String(140), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    complete = db.Column(db.Boolean, default=False)

    def to_JSON(self):
        d = {'id': self.id, 'name': self.name, 'due_date': self.due_date, 'start_date': self.start_date,
             'project': self.project, 'complete': self.complete}
        return json.dumps(d, sort_keys=True, cls=DatetimeEncoder)

    def __repr__(self):
        return 'Task is: {}'.format(self.name)

