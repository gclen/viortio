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
    tasks = []
    form = TaskForm()
    if form.validate_on_submit():
        task = Task(name=form.task.data)
        flash(gettext('Task added!'))
        return redirect(url_for('index'))

    return render_template('index.html', tasks=tasks, form=form)

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
            return redirect(url_for('index'))
        else:
            flash('Username or password is invalid')
            return redirect(url_for('login'))

    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
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

