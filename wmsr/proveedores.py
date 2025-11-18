from flask import Blueprint, render_template, request, flash, redirect, url_for
from wmsr.utils.export_excel import exportar_a_excel

from .auth import login_required # Importar el decorador de login requerido si es necesario
from .models import Proveedor, DocumentoRecibo # Importar el modelo de Proveedor
from . import db # Importar la base de datos

bp = Blueprint('proveedores', __name__, url_prefix='/proveedores')

# Ruta para la lista de proveedores
@bp.route('/')
@login_required
def lista_proveedores():
    # Aquí iría la lógica para obtener la lista de proveedores

    q = (request.args.get('q') or '').strip()
    proveedores = Proveedor.query.all()

    if q:
        proveedores = (
            db.session.query(Proveedor)
            .filter(
                (Proveedor.prov_razon_social.ilike(f'%{q}%')) |
                (Proveedor.prov_direccion.ilike(f'%{q}%')) |       
                (Proveedor.prov_telefono.ilike(f'%{q}%')) |
                (Proveedor.prov_email.ilike(f'%{q}%'))
            ).all()
        )
    else:
        proveedores = Proveedor.query.all()

    return render_template('documento_recibo/proveedores/listaproveedores.html', proveedores=proveedores, q=q)

@bp.route('/crear', methods=('GET', 'POST'))
@login_required
def crear_proveedor():
    if request.method == 'POST':
        razonsocial = request.form.get('razonsocial')
        direccion = request.form.get('direccion')
        telefono = request.form.get('telefono')
        correo = request.form.get('correo')
        descripcion = request.form.get('descripcion')

        # Validar unicidad (mensaje genérico)
        existe = (
            (razonsocial and Proveedor.query.filter_by(prov_razon_social=razonsocial).first()) or
            (direccion and Proveedor.query.filter_by(prov_direccion=direccion).first()) or
            (telefono and Proveedor.query.filter_by(prov_telefono=telefono).first()) or
            (correo and Proveedor.query.filter_by(prov_email=correo).first())
        )
        if existe:
            flash('Uno o más campos ya están registrados.', 'error')
            return redirect(url_for('proveedores.crear_proveedor'))

        try:
            nuevo_proveedor = Proveedor(
                prov_razon_social=razonsocial,
                prov_direccion=direccion,
                prov_telefono=telefono,
                prov_email=correo,
                prov_descripcion=descripcion
            )
            db.session.add(nuevo_proveedor)
            db.session.commit()
            flash('Proveedor creado correctamente.', 'success')
            return redirect(url_for('proveedores.lista_proveedores'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear el proveedor: {e}', 'error')
            return redirect(url_for('proveedores.crear_proveedor'))

    return render_template('documento_recibo/proveedores/crearproveedores.html')

@bp.route('/editar/<int:id>', methods=('GET', 'POST'))
@login_required
def editar_proveedor(id):
    proveedor = Proveedor.query.get_or_404(id)

    if request.method == 'POST':
        razonsocial = (request.form.get('razonsocial') or '').strip()
        direccion = (request.form.get('direccion') or '').strip()
        telefono = (request.form.get('telefono') or '').strip()
        correo = (request.form.get('correo') or '').strip()
        descripcion = request.form.get('descripcion')  # descripción puede ser opcional y con espacios

        # Validar unicidad excluyendo el registro actual
        conflictos = []
        if razonsocial:
            existe = Proveedor.query.filter(
                Proveedor.prov_razon_social == razonsocial,
                Proveedor.prov_id != id
            ).first()
            if existe:
                conflictos.append('razón social')
        if direccion:
            existe = Proveedor.query.filter(
                Proveedor.prov_direccion == direccion,
                Proveedor.prov_id != id
            ).first()
            if existe:
                conflictos.append('dirección')
        if telefono:
            existe = Proveedor.query.filter(
                Proveedor.prov_telefono == telefono,
                Proveedor.prov_id != id
            ).first()
            if existe:
                conflictos.append('teléfono')
        if correo:
            existe = Proveedor.query.filter(
                Proveedor.prov_email == correo,
                Proveedor.prov_id != id
            ).first()
            if existe:
                conflictos.append('correo')

        if conflictos:
            flash(f'Los siguientes campos ya están registrados: {", ".join(conflictos)}.', 'error')
            return redirect(url_for('proveedores.editar_proveedor', id=id))

        try:
            # Actualizar campos (si se envía vacío se guarda como cadena vacía)
            proveedor.prov_razon_social = razonsocial
            proveedor.prov_direccion = direccion
            proveedor.prov_telefono = telefono
            proveedor.prov_email = correo
            proveedor.prov_descripcion = descripcion

            db.session.commit()
            flash('Proveedor actualizado correctamente.', 'success')
            return redirect(url_for('proveedores.lista_proveedores'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar el proveedor: {e}', 'error')
            return redirect(url_for('proveedores.editar_proveedor', id=id))

    return render_template('documento_recibo/proveedores/editarproveedores.html', proveedor=proveedor)

@bp.route('/borrar/<int:id>', methods=('GET', 'POST'))
@login_required
def borrar_proveedor(id):
    proveedor = Proveedor.query.get_or_404(id)

    #Verificar si el proveedor está asociado a algún documento de recibo

    documentos_asociados = DocumentoRecibo.query.filter_by(doc_id_proveedor=id).count()
    if documentos_asociados > 0:
        flash(f'No se puede eliminar el proveedor "{proveedor.prov_razon_social}" porque está asociado a {documentos_asociados} documento(s) de recibo.', 'error')
        return redirect(url_for('proveedores.lista_proveedores'))
    
    db.session.delete(proveedor)
    db.session.commit()

    mensaje_exito = 'Proveedor borrado exitosamente.'
    flash(mensaje_exito, 'success')

    return redirect(url_for('proveedores.lista_proveedores', mensaje_exito=mensaje_exito))

@bp.route('/exportar_excel')
@login_required
def exportar_proveedores_excel():
    proveedores = Proveedor.query.all()

    data = [
        {   
            'ID': p.prov_id,
            'Razón Social': p.prov_razon_social,
            'Dirección': p.prov_direccion,
            'Teléfono': p.prov_telefono,
            'Correo': p.prov_email,
            'Descripción': p.prov_descripcion,
        }
        for p in proveedores
    ]

    columnas = ['Razón Social', 'Dirección', 'Teléfono', 'Correo', 'Descripción']
    return exportar_a_excel('proveedores', columnas, data)