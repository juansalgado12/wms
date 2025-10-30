from flask import Blueprint, render_template
from .auth import login_required

bp = Blueprint('home', __name__)

# Ruta para la página de bienvenida
@bp.route('/')
def welcome():
    return render_template('welcome.html')

# Ruta para la página del almacén
@bp.route('/almacen')
@login_required
def almacen():
    return render_template('layouts/base.html')