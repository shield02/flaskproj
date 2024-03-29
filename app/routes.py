from flask import request, render_template, flash, redirect, url_for
from flask_login import current_user, login_user, login_required, logout_user
import sqlalchemy as sa
from datetime import datetime, timezone
from urllib.parse import urlsplit
from app import app, db
from app.models import User
from app.auth.login import LoginForm
from app.auth.register import RegistrationForm
from app.forms import EditProfileForm

@app.route('/')
@app.route('/index')
@login_required
def index():
    user = {'username': 'Shield'}
    posts = [
        {
            'author': {'username': 'Shield'},
            'body': 'Beautiful day back to work in 2024'
        },
        {
            'author': {'username': 'John'},
            'body': 'The best movies of last year had incredible gross'
        }
    ]
    return render_template('index.html', title='Home', posts=posts)

@app.route('/auth/login', methods=['GET', 'POST'])
def login():
    # check the session for the user
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    # load the login form
    form = LoginForm()
    # validate the login form and login the user
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('/auth/login.html', title='Sign in', form=form)

@app.route('/auth/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/auth/register', methods=['GET', 'POST'])
def register():
    # check the session for the user
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    # load the registration form
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        form.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, registration is successful.')
        return redirect(url_for('login'))
    return render_template('/auth/register.html', title='Registration', form=form)

@app.route('/user/<username>')
@login_required
def user(username):
    user = db.first_or_404(sa.select(User).where(User.username == username))
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]
    return render_template('user.html', user=user, posts=posts)

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)
