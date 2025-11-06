from flask import Blueprint, render_template

bp = Blueprint('documento_recibo', __name__, url_prefix='/documento_recibo')

@bp.route('/')
def lista_documentos():
    return render_template('documento_recibo/listadocumentos.html')

@bp.route('/crear')
def crear_documento():
    return render_template('documento_recibo/creardocumento.html')

@bp.route('/editar')
def editar_documento():
    return render_template('documento_recibo/editardocumento.html')