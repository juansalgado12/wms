from flask import Blueprint, render_template

bp = Blueprint('marca', __name__, url_prefix='/marcas')

@bp.route('/')
def lista_marcas():
    return render_template('productos/marca/listamarcas.html')

@bp.route('/crear')
def crear_marca():
    return render_template('productos/marca/crearmarca.html')

@bp.route('/editar')
def editar_marca():
    return render_template('productos/marca/editarmarca.html')