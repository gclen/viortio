from flask import render_template, flash, redirect, url_for
from flask_babel import gettext
from app import app
from .task import Task
from .forms import TaskForm

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    tasks = []
    form = TaskForm()
    if form.validate_on_submit():
        task = Task(name=form.task.data)
        flash(gettext('Task added!'))
        return redirect(url_for('index'))

    return render_template('index.html', tasks=tasks, form=form)



