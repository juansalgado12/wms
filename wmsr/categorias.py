from flask import Blueprint, render_template

bp = Blueprint('categorias', __name__, url_prefix='/categorias')

@bp.route('/')
def lista_categorias():
    return render_template('categorias/listacategorias.html')

@bp.route('/crear')
def crear_categoria():
    return render_template('categorias/crearcategorias.html')

@bp.route('/editar')
def editar_categoria():
    return render_template('categorias/editarcategorias.html')