from flask import Blueprint, render_template

bp = Blueprint('presentacion', __name__, url_prefix='/presentacion')

@bp.route('/')
def lista_presentaciones():
    return render_template('productos/presentacion/listapresentacion.html')

@bp.route('/crear')
def crear_presentacion():
    return render_template('productos/presentacion/crearpresentacion.html')

@bp.route('/editar')
def editar_presentacion():
    return render_template('productos/presentacion/editarpresentacion.html')
