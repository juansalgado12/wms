from flask import Blueprint, render_template

bp = Blueprint('unidad', __name__, url_prefix='/unidad')

@bp.route('/')
def lista_unidades():
    return render_template('productos/unidad/listaunidad.html')

@bp.route('/crear')
def crear_unidad():
    return render_template('productos/unidad/crearunidad.html')

@bp.route('/editar')
def editar_unidad():
    return render_template('productos/unidad/editarunidad.html')