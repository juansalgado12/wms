from flask import Blueprint, render_template

bp = Blueprint('home', __name__)

@bp.route('/')
def welcome():
    return render_template('welcome.html')

@bp.route('/almacen')
def almacen():
    return render_template('layouts/base.html')