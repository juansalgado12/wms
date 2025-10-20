from flask import Blueprint

bp = Blueprint('categorias', __name__, url_prefix='/categorias')

@bp.route('/')
def lista_categorias():
    return 'pagina de lista de categorias'

@bp.route('/crear')
def crear_categoria():
    return 'Pagina de crear categoria'

@bp.route('/editar')
def editar_categoria():
    return 'Pagina de editar categoria'