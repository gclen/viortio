from datetime import datetime
from flask import render_template, flash, redirect, url_for, session, request, g
from flask_login import login_required, logout_user, login_user, current_user
from flask_babel import gettext
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, db, lm
from .task import Task
from .forms import TaskForm, LoginForm, RegistrationForm
from .models import User, Task


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():

    if request.form.get('is_finished'):
        t = Task.query.get(request.form.get('is_finished'))
        t.complete = True
        db.session.add(t)
        db.session.commit()

    tasks = g.user.get_tasklist()
    projects = [p[0] for p in g.user.get_projects()]

    return render_template('index.html', tasks=tasks, projects=projects)


@app.route('/completed', methods=['GET', 'POST'])
@login_required
def completed_tasks():

    tasks = g.user.get_completed_tasks()
    return render_template('completed_tasks.html', tasks=tasks)


@lm.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.before_request
def before_request():
    g.user = current_user


@app.route('/login', methods=['GET', 'POST'])
def login():
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        session['rememberme'] = form.remember_me.data
        u = User.query.filter_by(nickname=form.username.data).first()

        if u is None:
            flash('Username or password is invalid')
            return redirect(url_for('login'))
        if check_password_hash(u.password_hash, form.password.data):
            login_user(u, remember=form.remember_me.data)
            flash('Login successful')
            return redirect(url_for('index'))
        else:
            flash('Username or password is invalid')
            return redirect(url_for('login'))

    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    flash('You were logged out')
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        u = User(nickname=form.username.data, password_hash=generate_password_hash(form.password.data))
        db.session.add(u)
        db.session.commit()
        flash('You have been registered')
        return redirect(url_for('login'))

    return render_template('register.html', form=form, title='Create an account')


@app.route('/addtask', methods=['GET', 'POST'])
@login_required
def add_task():

    form = TaskForm()
    if form.validate_on_submit():
        sd = form.start_date.data if form.start_date.data else datetime.utcnow()
        project = form.project.data if form.project.data else None

        t = Task(name=form.task.data, due_date=form.due_date.data, user_id=g.user.id, start_date=sd, project=project)
        db.session.add(t)
        db.session.commit()
        flash(gettext('Task added!'))
        return redirect(url_for('index'))

    return render_template('addtask.html', form=form)


@app.route('/project/<project_name>', methods=['GET', 'POST'])
@login_required
def project(project_name):

    if request.form.get('is_finished'):
        t = Task.query.get(request.form.get('is_finished'))
        t.complete = True
        db.session.add(t)
        db.session.commit()

    project_tasks = Task.query.filter_by(project=project_name, complete=False).order_by('start_date').all()
    return render_template('project.html', tasks=project_tasks, title=project_name)


@app.errorhandler(404)
def file_not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500






