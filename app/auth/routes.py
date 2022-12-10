from flask import Blueprint, redirect, url_for, render_template, flash, request
from flask_login import login_user, logout_user, login_required
from app import db, bcrypt
from app.auth.forms import RegistrationForm, LoginForm
from app.auth.models import User
from app.auth.decorators import login_forbidden
from flask_login import current_user

auth = Blueprint('auth', __name__)


@auth.route('/register', methods=['GET', 'POST'])
@login_forbidden
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        pwd_hash = bcrypt.generate_password_hash(form.password.data, 16).decode('utf-8')
        user = User(username=form.username.data, password=pwd_hash, email=form.email.data)
        db.session.add(user)
        db.session.commit()
        login_user(user, remember=True)
        return redirect(url_for('game.logout'))
    return render_template('auth/register.html', form=form)


@auth.route('/login', methods=['GET', 'POST'])
@login_forbidden
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('game.home', user_id=current_user.id))
        flash('error', 'Something went wrong.')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('game.logout'))


@auth.route('/profile/<user_id>')
def profile(user_id):
    user = User.query.filter_by(id=user_id).first()
    return render_template('auth/profile.html', user=user)