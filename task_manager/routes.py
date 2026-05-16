from task_manager import app,db
from flask import render_template, redirect, url_for, flash, request,session
from task_manager.models import  User,Task
from task_manager.forms import RegisterForm, LoginForm, AddForm
from flask_login import login_user, logout_user, login_required, current_user


@app.route('/')
@app.route('/home')
@login_required
def home_page():

    search = request.args.get('search')

    if search:

        tasks = Task.query.filter(
            Task.user_id == session['user_id'],
            Task.completed == False,
            Task.title.contains(search)
        ).all()

    else:

        tasks = Task.query.filter_by(
            user_id=session['user_id'],
            completed=False
        ).all()

    completed_tasks = Task.query.filter_by(
        user_id=session['user_id'],
        completed=True
    ).all()

    return render_template(
        'home.html',
        tasks=tasks,
        completed_tasks=completed_tasks
    )

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(username=form.username.data,
                              email_address=form.email_address.data,
                              password=form.password1.data)
        db.session.add(user_to_create)
        db.session.commit()
        login_user(user_to_create)
        flash(f"Account created successfully! You are now logged in as {user_to_create.username}", category='success')
        return redirect(url_for('add_task_page'))
    if form.errors != {}: #If there are not errors from the validations
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user: {err_msg}', category='danger')

    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(
                attempted_password=form.password.data
        ):
            login_user(attempted_user)
            session['user_id'] = attempted_user.id
            flash(f'Success! You are logged in as: {attempted_user.username}', category='success')
            return redirect(url_for('home_page'))
        else:
            flash('Username and password are not match! Please try again', category='danger')

    return render_template('login.html', form=form)

@app.route('/logout')
def logout_page():
    session.pop('user_id', None)
    logout_user()
    flash("You have been logged out!", category='info')
    return redirect(url_for("home_page"))

@app.route('/add_task', methods=['GET', 'POST'])
@login_required
def add_task_page():
    form=AddForm()
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    if request.method == 'POST':
        title=request.form['title']
        priority=request.form['priority']
        category=request.form['category']
        deadline=request.form['deadline']
        task=Task(title=title,priority=priority,category=category,deadline=deadline,user_id=session['user_id'])
        db.session.add(task)
        db.session.commit()
        flash('Task added successfully!', category='success')
        return redirect(url_for('home_page'))
    return render_template('add_task.html',form=form)

@app.route('/complete_task/<int:task_id>')
def complete_task(task_id):

    task = Task.query.get_or_404(task_id)

    task.completed = True

    db.session.commit()

    flash("Task Completed Successfully!", category='success')

    return redirect(url_for('home_page'))


@app.route('/delete_task/<int:task_id>')
def delete_task(task_id):

    task = Task.query.get_or_404(task_id)

    db.session.delete(task)

    db.session.commit()

    flash("Task Deleted Successfully!", category='danger')

    return redirect(url_for('home_page'))

@app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):

    task = Task.query.get_or_404(task_id)

    if request.method == 'POST':

        task.title = request.form['title']
        task.priority = request.form['priority']

        db.session.commit()

        flash('Task Updated Successfully!', category='success')

        return redirect(url_for('home_page'))

    return render_template('edit_task.html', task=task)