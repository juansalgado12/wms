from flask import Blueprint, render_template

bp = Blueprint('home', __name__)

# Ruta para la página de bienvenida
@bp.route('/')
def welcome():
    return render_template('welcome.html')

# Ruta para la página del almacén
@bp.route('/almacen')
def almacen():
    return render_template('layouts/base.html')