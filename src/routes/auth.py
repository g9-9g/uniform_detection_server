import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)

from src.utils.dataset import *

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.before_app_request
def load_logged_in_user():
    token = session.get('token')

    if token is None:
        g.username = None
    else:
        g.username =  session.get('username')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember')
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        # session['db'] = Uniform()
        try:
            token = connect_db(username, password)
            if token is None:
                raise Exception("Password or username is incorrect !")

            if remember:
                session['token'] = token
                session['username'] = username
            return redirect(url_for('predict.predict'))
        except Exception as e:
            error = e

        flash(error)
    
    return render_template('auth/login.html')

@bp.route('/logout', methods=('GET', 'POST'))
def logout():
    session.clear()
    return redirect(url_for('auth.login'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.username is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view