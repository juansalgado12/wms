from flask import Blueprint

bp = Blueprint('document_recibo', __name__, url_prefix='/document_recibo')

@bp.route('/')
def lista_documentos():
    return 'pagina de lista de documentos'

@bp.route('/crear')
def crear_documento():
    return 'Pagina de crear documento'

@bp.route('/editar')
def editar_documento():
    return 'Pagina de editar documento'