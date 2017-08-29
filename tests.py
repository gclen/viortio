import os
import unittest
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

from config import basedir
from app import app, db
from app.models import User, Task


class ViortioTestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'test.db')
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def login(self, username, password):
        return self.app.post('/login', data=dict(username=username, password=password), follow_redirects=True)

    def logout(self):
        return self.app.get('/logout', follow_redirects=True)

    def register(self, username, password, confirm):
        return self.app.post('/register', data=dict(username=username, password=password, confirm=confirm), follow_redirects=True)

    def add_task(self, task, due_date, start_date, project):
        return self.app.post('/addtask', data=dict(task=task, due_date=due_date, start_date=start_date, project=project),
                             follow_redirects=True)

    def project_page(self, project):
        return self.app.get('/project/{}'.format(project))

    def test_user(self):
        password_hash = generate_password_hash('12345')
        u = User(nickname='Jane', password_hash=password_hash)

        assert u.nickname == 'Jane'
        assert u.password_hash == password_hash

    def test_login_logout(self):
        password_hash = generate_password_hash('12345')

        u = User(nickname='admin', password_hash=password_hash)
        db.session.add(u)
        db.session.commit()

        rv = self.login('admin', '12345')
        assert b'Login successful' in rv.data

        rv = self.logout()
        assert b'You were logged out' in rv.data

        rv = self.login('invaliduser', '12345')
        assert b'Username or password is invalid' in rv.data

        rv = self.login('admin', 'invalidpassword')
        assert b'Username or password is invalid' in rv.data

    def test_registration(self):

        rv = self.register('newuser', 'newpassword', 'newpassword')
        assert b'You have been registered' in rv.data

        rv = self.register('newuser', '', '')
        assert b'[This field is required.]' in rv.data

        rv = self.register('newuser', 'password', 'different_password')
        assert b'[Passwords must match]' in rv.data

        new_user = User.query.filter_by(nickname='newuser').first()
        assert new_user is not None

    def test_user_tasklist(self):
        u = User(nickname='Jane')
        db.session.add(u)
        db.session.commit()

        task1 = Task(name='task1', user_id=u.id, start_date=datetime.utcnow() - timedelta(days=1))
        db.session.add(task1)
        task2 = Task(name='task2', user_id=u.id, start_date=datetime.utcnow())
        db.session.add(task2)
        task3 = Task(name='task3', user_id=u.id, start_date=datetime.utcnow() + timedelta(days=1))
        db.session.add(task3)

        db.session.commit()

        tasks = [t.name for t in u.get_tasklist()]
        assert tasks == ['task1', 'task2']

    def test_completed_tasks(self):
        u = User(nickname='Jane')
        db.session.add(u)
        db.session.commit()

        task1 = Task(name='Marked as completed', user_id=u.id, start_date=datetime.utcnow(), complete=True)
        db.session.add(task1)
        task2 = Task(name='Incomplete', user_id=u.id, start_date=datetime.utcnow())
        db.session.add(task2)

        db.session.commit()

        tasks = [t.name for t in u.get_completed_tasks()]
        assert tasks == ['Marked as completed']

    def test_projects(self):
        u = User(nickname='Jane')
        db.session.add(u)
        db.session.commit()

        task1 = Task(name='Foo task', user_id=u.id, start_date=datetime.utcnow(), project='foo')
        db.session.add(task1)
        task2 = Task(name='Bar task', user_id=u.id, start_date=datetime.utcnow(), project='bar')
        db.session.add(task2)

        db.session.commit()

        projects = [p[0] for p in u.get_projects()]
        assert projects == ['bar', 'foo']

    def test_add_task(self):
        password_hash = generate_password_hash('12345')
        u = User(nickname='Jane', password_hash=password_hash)
        db.session.add(u)
        db.session.commit()

        self.login('Jane', '12345')

        rv = self.add_task(task='task1', due_date=datetime.utcnow().strftime('%Y-%m-%d'),
                           start_date=datetime.utcnow().strftime('%Y-%m-%d'), project='test project')
        assert b'Task added!' in rv.data

        rv = self.add_task(task='task1', due_date='invalid due date', start_date=datetime.utcnow().strftime('%Y-%m-%d'), project=None)
        assert b'[Not a valid date value]' in rv.data

        rv = self.add_task(task='task1', due_date=datetime.utcnow().strftime('%Y-%m-%d'), start_date='invalid_start_date', project=None)
        assert b'[Not a valid date value]' in rv.data

    def test_project(self):
        password_hash = generate_password_hash('12345')
        u = User(nickname='Jane', password_hash=password_hash)
        db.session.add(u)
        db.session.commit()

        self.login('Jane', '12345')

        project = 'foo'
        task1 = Task(name='task1 for project foo', user_id=u.id, start_date=datetime.utcnow() - timedelta(days=1), project=project)
        db.session.add(task1)
        db.session.commit()

        rv = self.project_page(project)
        assert b'task1 for project foo' in rv.data

if __name__ == '__main__':
    unittest.main()









