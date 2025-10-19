from flask import blueprints

bp = blueprints.Blueprint('productos', __name__, url_prefix='/productos')

@bp.route('/')
def catalogo():
    return ('Pagina de catalogo de productos')

@bp.route('/crear')
def crear():
    return ('Pagina de crear producto')

@bp.route('/editar')
def editar():
    return ('Pagina de editar producto')