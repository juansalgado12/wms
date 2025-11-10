from flask import Blueprint, render_template, request, flash, redirect, url_for

from .auth import login_required
from .models import DocumentoRecibo, Proveedor
from . import db
from wmsr.utils.export_excel import exportar_a_excel

bp = Blueprint('documento_recibo', __name__, url_prefix='/documento_recibo')

@bp.route('/')
def lista_documentos():
    # obtener todos los documentos de recibo de la base de datos y proveedores relacionados

    documentos = DocumentoRecibo.query.all()
    proveedores = Proveedor.query.all()

    # Mapear los IDs de proveedores a sus nombres para un acceso rápido
    proveedores_map = {p.prov_id: p.prov_razon_social for p in proveedores}


    return render_template('documento_recibo/listadocumentos.html', documentos=documentos, proveedores=proveedores, proveedores_map=proveedores_map)

@bp.route('/crear')
def crear_documento():
    return render_template('documento_recibo/creardocumento.html')

@bp.route('/editar')
def editar_documento():
    return render_template('documento_recibo/editardocumento.html')

@bp.route('/exportar_excel')
@login_required
def exportar_documentos_excel():
    # Hacer join con proveedores para obtener nombres
    documentos = (
        db.session.query(
            DocumentoRecibo.doc_id,
            DocumentoRecibo.doc_id_proveedor,
            Proveedor.prov_razon_social.label("Razon_social"),
            DocumentoRecibo.doc_fecha,
            DocumentoRecibo.doc_estado,
            DocumentoRecibo.doc_descripcion
        )
        .outerjoin(Proveedor, DocumentoRecibo.doc_id_proveedor == Proveedor.prov_id)
    )

    # Convertir los resultados a una lista de diccionarios
    data = [
        {
            'ID Documento': d.doc_id,
            'ID Proveedor': d.doc_id_proveedor,
            'Razon Social del Proveedor': d.Razon_social or '',
            'Fecha': d.doc_fecha,
            'Estado': d.doc_estado,
            'Descripcion': d.doc_descripcion
        }
        for d in documentos
    ]

    columnas = ['ID Documento', 'ID Proveedor', 'Razon Social del Proveedor', 'Fecha', 'Estado', 'Descripcion']

    return exportar_a_excel('documentos_recibo', columnas, data)