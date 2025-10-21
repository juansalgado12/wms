from flask import Blueprint, render_template

bp = Blueprint('categorias', __name__, url_prefix='/categorias')

# Ruta para la lista de categorías
@bp.route('/')
def lista_categorias():
    return render_template('categorias/listacategorias.html')

# Ruta para crear una nueva categoría
@bp.route('/crear')
def crear_categoria():
    return render_template('categorias/crearcategorias.html')

# Ruta para editar una categoría existente
@bp.route('/editar')
def editar_categoria():
    return render_template('categorias/editarcategorias.html')