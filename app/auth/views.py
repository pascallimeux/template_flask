
from flask import Flask, render_template, url_for, request, redirect, flash, session
from flask_login import login_user, logout_user, login_required

from . import auth
from ..models import User, UserRole, Visitor
from .forms import RegisterForm, LoginForm

@auth.route('/login', methods=['get', 'post'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        visitor = Visitor()
        if 'uuid' not in session:
            visitor.create(request)
            session['uuid'] = str(visitor.id)

        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data
            remember = form.remember.data

            if User.objects(username=username):
                user = User.objects.get(username=username)
                if user.check_password(password):
                    if user.is_active():
                        login_user(user, remember=remember)
                        user.refresh_last_login()
                        user.save()
                        if visitor.id:
                            visitor.user = user.id
                            visitor.save()
                        return redirect(url_for('home.index'))
                    else:
                        flash('Unactivated account.', 'danger')
                        return redirect(url_for('auth.login'))
                else:
                    flash('Access denied, bad password.', 'danger')
            else:
                flash('Access denied, unknown user.', 'danger')

    return render_template('auth/login.html', form=form, title='Login')


@auth.route('/register', methods=['get', 'post'])
def register():
    form = RegisterForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                user = User(username=form.username.data, 
                            firstname=form.firstname.data, 
                            lastname=form.lastname.data , 
                            email=form.email.data, 
                            password=form.password.data,
                            role=int(form.role.data))
                user.create()
                flash('Account registred.', 'success')
                return redirect(url_for('home.index'))
            except Exception as e:
                msg = 'Account not registered, error:' + str(e)
                flash(msg, 'danger')

    return render_template('auth/register.html', form=form, roles_list=UserRole, title='register')


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('auth.login'))

