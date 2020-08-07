from flask import render_template, url_for, request, redirect, flash
from flask_login import login_required, current_user

from . import user
from ..models import User, UserRole
from .forms import UserForm, UserEditForm
from ..utils import admin_required, owner_or_admin_required

@user.route('/user/add', methods=['get', 'post'])
@admin_required
def user_add():
    form = UserForm()
    if request.method == 'POST':
        if form.back.data:
            return redirect(url_for('user.users_list'))
            
        if form.validate_on_submit():
            try:
                user = User(username=form.username.data, 
                            firstname=form.firstname.data, 
                            lastname=form.lastname.data , 
                            email=form.email.data, 
                            role=int(form.role.data),
                            password=form.password.data)
                user.create()
                flash('user {} created'.format(user.username), 'success')
                return redirect(url_for('user.users_list'))
            except Exception as e:
                flash('user not created, error:' + str(e), 'danger')

    return render_template('user/add-user.html', form=form, roles_list=UserRole, title='add user')

 
  
@user.route('/user/delete/<string:userid>', methods = ['get', 'post'])
@admin_required
def user_delete(userid):
    user = User.objects.get_or_404(id=userid)
    if str(current_user.id) == userid:
        flash('unauthorized operation', 'danger')
    else:
        user.delete()
        flash("User {} Deleted".format(user.username), 'success')
    return redirect(url_for('user.users_list'))
 
 
@user.route('/user/edit/<string:userid>', methods = ['get', 'post'])
@owner_or_admin_required
def user_edit(userid):
    user = User.objects.get_or_404(id=userid)
    form = UserEditForm(obj=user)
    owner = userid == str(current_user.id)
    admin = current_user.is_admin()

    if request.method == 'POST':
        if form.back.data:
            return redirect(url_for('user.users_list'))
            
        if form.validate_on_submit():
            try:
                if owner:
                    user.username=form.username.data
                    user.firstname=form.firstname.data
                    user.lastname=form.lastname.data
                    user.email=form.email.data
                if admin:
                    user.role=int(form.role.data)
                    user.active=form.active.data
                user.save()
                flash('user {} updated'.format(user.username), 'success')
                return redirect(url_for('user.users_list'))
            except Exception as e:
                msg = 'Error, your account is not register:' + str(e)
                flash(msg, 'danger')
 
    return render_template('user/edit-user.html', form=form, roles_list=UserRole, owner=owner, admin=admin, title='edit user')
 

@user.route('/users', methods = ['get'])
@login_required
def users_list():
    return render_template('user/list-users.html', users=User.objects(), roles_list=UserRole, admin=current_user.is_admin(), title='Liste des utilisateurs')


