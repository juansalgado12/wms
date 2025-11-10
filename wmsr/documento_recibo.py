from flask import Blueprint, render_template, request, flash, redirect, url_for

from .auth import login_required
from .models import DocumentoRecibo, Proveedor
from . import db

bp = Blueprint('documento_recibo', __name__, url_prefix='/documento_recibo')

@bp.route('/')
def lista_documentos():
    # obtener todos los documentos de recibo de la base de datos y proveedores relacionados

    documentos = DocumentoRecibo.query.all()
    proveedores = Proveedor.query.all()

    # Mapear los IDs de proveedores a sus nombres para un acceso rápido
    proveedores_map = {p.prov_id: p.prov_nombre for p in proveedores}


    return render_template('documento_recibo/listadocumentos.html', documentos=documentos, proveedores=proveedores, proveedores_map=proveedores_map)

@bp.route('/crear')
def crear_documento():
    return render_template('documento_recibo/creardocumento.html')

@bp.route('/editar')
def editar_documento():
    return render_template('documento_recibo/editardocumento.html')