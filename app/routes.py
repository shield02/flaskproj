from flask import render_template, flash, redirect, url_for
from flask_login import current_user, login_user
import sqlalchemy as sa
from app import app, db
from app.models import User
from app.auth.login import LoginForm

@app.route('/')
@app.route('/index')
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
    return render_template('index.html', title='Home', user=user, posts=posts)

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
        return redirect(url_for('index'))
    return render_template('/auth/login.html', title='Sign in', form=form)
