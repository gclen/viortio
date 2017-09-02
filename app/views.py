from datetime import datetime
from dateutil.parser import parse
from flask import render_template, flash, redirect, url_for, session, request, g, jsonify, abort
from flask_login import login_required, logout_user, login_user, current_user
from flask_httpauth import HTTPBasicAuth
from flask_babel import gettext
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, db, lm
from .task import Task
from .forms import TaskForm, LoginForm, RegistrationForm
from .models import User, Task

auth = HTTPBasicAuth()

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

# Creating a REST API
@app.route('/viortio/api/v1.0/users/<int:id>', methods=['GET'])
def get_user(id):
    u = User.query.get(id)
    if not u:
        abort(400)
    return jsonify({'username': u.nickname})


@app.route('/viortio/api/v1.0/register', methods=['POST'])
def register_user():
    username = request.json.get('username')
    password = request.json.get('password')

    if username is None or password is None:
        abort(400)
    if User.query.filter_by(nickname=username).first() is not None:
        abort(400)

    user = User(nickname=username, password_hash=generate_password_hash(password))
    db.session.add(user)
    db.session.commit()

    return (jsonify({'username': user.nickname}), 201, {'Location': url_for('get_user', id=user.id, _external=True)})

@app.route('/viortio/api/v1.0/tasks', methods=['GET'])
@auth.login_required
def get_tasks():
    tasks = [t.to_JSON() for t in g.user.get_tasklist()]
    return jsonify({'tasks': tasks})

@auth.verify_password
def verify_password(username, password):
    u = User.query.filter_by(nickname=username).first()
    if not u or not check_password_hash(u.password_hash, password):
        return False
    g.user = u
    return True


@app.route('/viortio/api/v1.0/tasks/create', methods=['POST'])
@auth.login_required
def create_task():
    if not request.json or not 'name' in request.json:
        abort(400)

    due_date = parse(request.json.get('due_date')) if request.json.get('due_date') else None
    start_date = parse(request.json.get('start_date')) if request.json.get('start_date') else datetime.utcnow()

    t = Task(name=request.json.get('name'), due_date=due_date, start_date=start_date,
             project=request.json.get('project', None), user_id=g.user.id)

    db.session.add(t)
    db.session.commit()

    return jsonify(t.to_JSON()), 201

@app.route('/viortio/api/v1.0/tasks/update/<int:id>', methods=['POST'])
@auth.login_required
def update_task(id):

    t = Task.query.filter_by(id=id, user_id=g.user.id).first()

    if t is None:
        abort(404)

    if request.json.get('name'):
        t.name = request.json.get('name')
    if request.json.get('due_date'):
        t.due_date = parse(request.json.get('due_date'))
    if request.json.get('start_date'):
        t.start_date = parse(request.json.get('start_date'))
    if request.json.get('project'):
        t.project = request.json.get('project')
    if request.json.get('complete'):
        t.complete = request.json.get('complete')

    db.session.commit()

    return jsonify(t.to_JSON()), 201


@app.route('/viortio/api/v1.0/tasks/delete/<int:id>', methods=['POST'])
@auth.login_required
def delete_task(id):

    t = Task.query.filter_by(id=id, user_id=g.user.id).first()
    if t is None:
        abort(404)

    db.session.delete(t)
    db.session.commit()

    return jsonify({'deleted': id}), 201


@app.route('/viortio/api/v1.0/tasks/completed', methods=['GET'])
@auth.login_required
def get_completed_tasks():
    tasks = [t.to_JSON() for t in g.user.get_completed_tasks()]
    return jsonify({'completed': tasks})


@app.route('/viortio/api/v1.0/projects', methods=['GET'])
@auth.login_required
def get_projects():
    projects = [p[0] for p in g.user.get_projects()]
    return jsonify({'projects': projects})


@app.route('/viortio/api/v1.0/projects/<project_name>', methods=['GET'])
@auth.login_required
def get_tasks_for_project(project_name):
    project_tasks = Task.query.filter_by(project=project_name, complete=False).order_by('start_date').all()
    project_tasks = [t.to_JSON() for t in project_tasks]
    return jsonify({'project': project_name, 'tasks': project_tasks})
