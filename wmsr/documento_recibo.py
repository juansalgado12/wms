from flask import Blueprint, render_template, request, flash, redirect, url_for, make_response

from .auth import login_required
from .models import DocumentoRecibo, Proveedor
from . import db
from wmsr.utils.export_excel import exportar_a_excel
from datetime import datetime, timezone
from zoneinfo import ZoneInfo # manejo de zonas horarias
import pdfkit

bp = Blueprint('documento_recibo', __name__, url_prefix='/documento_recibo')

@bp.route('/')
@login_required
def lista_documentos():
    # obtener todos los documentos de recibo de la base de datos y proveedores relacionados

    documentos = DocumentoRecibo.query.all()
    proveedores = Proveedor.query.all()

    # Mapear los IDs de proveedores a sus nombres para un acceso rápido
    proveedores_map = {p.prov_id: p.prov_razon_social for p in proveedores}


    return render_template('documento_recibo/listadocumentos.html', documentos=documentos, proveedores=proveedores, proveedores_map=proveedores_map)

@bp.route('/crear', methods=('GET', 'POST'))
@login_required
def crear_documento():

    if request.method == 'POST':
        id_documento = request.form.get('doc_id')
        proveedor = request.form.get('proveedor')
        estado = request.form.get('estado')
        descripcion = request.form.get('descripcion')

        # Validar campos obligatorios
        if not id_documento or not proveedor or not estado:
            flash('Por favor, complete todos los campos obligatorios.', 'error')
            proveedores = Proveedor.query.all()
            return render_template('documento_recibo/creardocumentos.html', proveedores=proveedores, estados=['PENDIENTE', 'RECHAZADO', 'ACEPTADO'])
        
        # Validar unicidad del ID del documento
        id_existente = DocumentoRecibo.query.filter_by(doc_id=id_documento).first()
        if id_existente:
            flash(f'El ID del documento {id_documento} ya existe. Por favor, digite uno diferente.', 'error')
            proveedores = Proveedor.query.all()
            return render_template('documento_recibo/creardocumentos.html', proveedores=proveedores, estados=['PENDIENTE', 'RECHAZADO', 'ACEPTADO'])
        
        # validar existencia del proveedor
        try:
            prov_id = int(proveedor)
        except (ValueError, TypeError):
            flash('Proveedor inválido. Por favor, seleccione un proveedor válido.', 'error')
            proveedores = Proveedor.query.all()
            return render_template('documento_recibo/creardocumentos.html', proveedores=proveedores, estados=['PENDIENTE', 'RECHAZADO', 'ACEPTADO'])
        
        if not Proveedor.query.get(prov_id):
            flash('El proveedor seleccionado no existe. Por favor, seleccione un proveedor válido.', 'error')
            proveedores = Proveedor.query.all()
            return render_template('documento_recibo/creardocumentos.html', proveedores=proveedores, estados=['PENDIENTE', 'RECHAZADO', 'ACEPTADO'])
        
        # Obtener o establecer la fecha de creación (se espera formato YYYY-MM-DD desde el formulario)
        tz_colombia = ZoneInfo("America/Bogota")
        fecha_str = request.form.get('fecha')
        if fecha_str:
            try:
                fecha = datetime.strptime(fecha_str, '%Y-%m-%d')
                # establecer la fecha como timezone-aware en hora colombiana
                fecha = fecha.replace(tzinfo=tz_colombia)
            except ValueError:
                flash('Fecha inválida. Use el formato AAAA-MM-DD.', 'error')
                proveedores = Proveedor.query.all()
                return render_template('documento_recibo/creardocumentos.html', proveedores=proveedores, estados=['PENDIENTE', 'RECHAZADO', 'ACEPTADO'])
        else:
            # usar la hora actual en Colombia
            fecha = datetime.now(tz_colombia)

        # Crear y guardar el nuevo documento pasando los campos requeridos al constructor
        # El constructor de DocumentoRecibo requiere al menos doc_id y doc_id_proveedor, por eso los proporcionamos aquí.
        try:
            documento = DocumentoRecibo(
                doc_id=id_documento,
                doc_id_proveedor=prov_id,
                doc_fecha=fecha,
                doc_estado=estado,
                doc_descripcion=descripcion
            )
        except TypeError:
            # Si la clase espera argumentos posicionales, usar la forma posicional como respaldo
            documento = DocumentoRecibo(id_documento, prov_id)
            documento.doc_fecha = fecha
            documento.doc_estado = estado
            documento.doc_descripcion = descripcion

        db.session.add(documento)
        db.session.commit()
        flash(f'Documento {id_documento} creado correctamente.', 'success')
        return redirect(url_for('documento_recibo.lista_documentos'))


    # En el GET incluir proveedores y estados para que aparezcan en el formulario
    return render_template('documento_recibo/creardocumentos.html', proveedores=Proveedor.query.all(), estados=['PENDIENTE', 'RECHAZADO', 'ACEPTADO'])

@bp.route('/editar/<string:doc_id>', methods=('GET', 'POST'))
@login_required
def editar_documento(doc_id):
    # Buscar el documento por su ID
    documento = DocumentoRecibo.query.get_or_404(doc_id)
    if not documento:
        flash(f'El documento con ID {doc_id} no existe.', 'error')
        return redirect(url_for('documento_recibo.lista_documentos'))
    
    if request.method == 'POST':
        # Leer los datos del formulario
        id_documento = (request.form.get('doc_id') or '').strip()
        proveedor = request.form.get('proveedor')
        estado = request.form.get('estado')
        descripcion = request.form.get('descripcion')

        # Validar campos obligatorios
        if not id_documento or not proveedor or not estado:
            flash('Por favor, complete todos los campos obligatorios.', 'error')
            return render_template('documento_recibo/editardocumento.html', documento=documento, proveedores=Proveedor.query.all(), estados=['PENDIENTE', 'RECHAZADO', 'ACEPTADO'])

        # Validar unicidad del ID del documento si fue modificado
        if id_documento != documento.doc_id:
            existente = DocumentoRecibo.query.filter_by(doc_id=id_documento).first()
            if existente:
                flash(f'El ID del documento {id_documento} ya existe. Por favor, digite uno diferente.', 'error')
                return render_template('documento_recibo/editardocumentos.html', documento=documento, proveedores=Proveedor.query.all(), estados=['PENDIENTE', 'RECHAZADO', 'ACEPTADO'])

        # validar existencia del proveedor
        try:
            prov_id = int(proveedor)
        except (ValueError, TypeError):
            flash('Proveedor inválido. Por favor, seleccione un proveedor válido.', 'error')
            return render_template('documento_recibo/editardocumento.html', documento=documento, proveedores=Proveedor.query.all(), estados=['PENDIENTE', 'RECHAZADO', 'ACEPTADO'])
        
        if not Proveedor.query.get(prov_id):
            flash('El proveedor seleccionado no existe. Por favor, seleccione un proveedor válido.', 'error')
            return render_template('documento_recibo/editardocumento.html', documento=documento, proveedores=Proveedor.query.all(), estados=['PENDIENTE', 'RECHAZADO', 'ACEPTADO'])
        
        tz_colombia = ZoneInfo("America/Bogota")
        fecha_str = request.form.get('fecha')
        if fecha_str:
            try:
                fecha = datetime.strptime(fecha_str, '%Y-%m-%d')
                # establecer la fecha como timezone-aware en hora colombiana
                fecha = fecha.replace(tzinfo=tz_colombia)
            except ValueError:
                flash('Fecha inválida. Use el formato AAAA-MM-DD.', 'error')
                proveedores = Proveedor.query.all()
                return render_template('documento_recibo/creardocumentos.html', proveedores=proveedores, estados=['PENDIENTE', 'RECHAZADO', 'ACEPTADO'])
        else:
            # usar la hora actual en Colombia
            fecha = datetime.now(tz_colombia)
        
        # Actualizar los campos del documento
        documento.doc_id = id_documento
        documento.doc_id_proveedor = prov_id
        documento.doc_fecha = fecha
        documento.doc_estado = estado
        documento.doc_descripcion = descripcion

        db.session.commit()
        flash(f'Documento {id_documento} actualizado correctamente.', 'success')
        return redirect(url_for('documento_recibo.lista_documentos'))


    return render_template('documento_recibo/editardocumentos.html', documento=documento, proveedores=Proveedor.query.all(), estados=['PENDIENTE', 'RECHAZADO', 'ACEPTADO'])

@bp.route('/borrar/<string:doc_id>', methods=('GET', 'POST'))
@login_required
def borrar_documento(doc_id):
    documento = DocumentoRecibo.query.get_or_404(doc_id)
    if not documento:
        flash(f'El documento con ID {doc_id} no existe.', 'error')
    else:
        db.session.delete(documento)
        db.session.commit()
        flash(f'Documento {doc_id} eliminado correctamente.', 'success')
    return redirect(url_for('documento_recibo.lista_documentos'))


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

@bp.route('/descargar/<string:doc_id>')
@login_required
def descargar_documento_pdf(doc_id):
    # doc_id es un identificador alfanumérico (ej. 'doc_03'), no un entero
    documento = DocumentoRecibo.query.get_or_404(doc_id)
    proveedor = Proveedor.query.get(documento.doc_id_proveedor)

    # Renderizar el HTML con los datos del documento
    html = render_template('documento_recibo/pdf_documento.html', 
                           documento=documento, 
                           proveedor=proveedor,
                           now=datetime.now(ZoneInfo("America/Bogota")))

    # Configuración de PDFKit (opcional: puedes ajustar tamaño, márgenes, etc.)
    options = {
        'encoding': 'UTF-8',
        'enable-local-file-access': None,
        'page-size': 'A4',
        'margin-top': '10mm',
        'margin-bottom': '10mm',
        'margin-left': '10mm',
        'margin-right': '10mm'
    }

    # Convertir el HTML en PDF (sin guardarlo en disco)
    pdf = pdfkit.from_string(html, False, options=options)

    # Devolverlo como descarga
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=documento_{documento.doc_id}.pdf'

    return response