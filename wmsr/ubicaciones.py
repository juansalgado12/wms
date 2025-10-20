from flask import Blueprint

bp = Blueprint('ubicaciones', __name__, url_prefix='/ubicaciones')

@bp.route('/')
def lista_ubicaciones():
    return 'pagina de lista de ubicaciones'

@bp.route('/crear')
def crear_ubicacion():
    return 'Pagina de crear ubicacion'

@bp.route('/editar')
def editar_ubicacion():
    return 'Pagina de editar ubicacion'