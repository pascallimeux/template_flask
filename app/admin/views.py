from flask import render_template, url_for, request, redirect, flash
from flask_login import login_required

from ..models import Visitor, User
from ..utils import admin_required
from . import admin


@admin.route('/visitors', methods = ['get'])
@admin_required
def visitors_list():
    visitors = Visitor.objects()
    return render_template('admin/list-visitors.html', visitors=visitors, title='Liste des visiteurs')

 