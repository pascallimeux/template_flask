
from flask import render_template, url_for, redirect, request, make_response, session
from flask_login import current_user, login_required

from ..models import Visitor, UserRole
from . import home

@home.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    return render_template('home/index.html', title='Accueil')

@home.route('/cookie')
def cookie():
    nb_visites = request.cookies.get('visites')
    if not nb_visites:
        nb_visites = '1'
    else:
        nb_visites = str(int(nb_visites) + 1)
    
    if not current_user.is_authenticated:
        ret = redirect(url_for('auth.login'))
    else:
        ret = render_template('home/index.html', title='Accueil')
    response = make_response(ret)
    response.set_cookie('visites', nb_visites, httponly=True, samesite='Lax', path='/toto/')
    return response

@home.route('/contact', methods=['get'])
@login_required
def contact():
    #return 'Page contact <a href="' + url_for('home.index') + '">Retour accueil</a>'
    return render_template('home/contact.html', title='Contact')


@home.route('/help', methods=['get'])
@login_required
def help():
    return render_template('home/help.html', title='About')


@home.route('/profil', methods=['get'])
@login_required
def profil():
    qrcode = current_user.get_qrcode()
    if 'uuid' in session:
        try:
            visitor = Visitor.objects.get(id=session['uuid'])
            return render_template('home/profil.html', title='Profil', visitor=visitor, qrcode=qrcode, roles_list=UserRole)
        except:
            pass
    return render_template('home/profil.html', title='Profil', qrcode=qrcode, roles_list=UserRole)
