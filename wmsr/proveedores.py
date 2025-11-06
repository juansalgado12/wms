from flask import Blueprint, render_template, request, flash, redirect, url_for

from .auth import login_required # Importar el decorador de login requerido si es necesario
from .models import Proveedor # Importar el modelo de Proveedor
from . import db # Importar la base de datos

bp = Blueprint('proveedores', __name__, url_prefix='/proveedores')

# Ruta para la lista de proveedores
@bp.route('/')
def lista_proveedores():
    # Aquí iría la lógica para obtener la lista de proveedores
    proveedores = Proveedor.query.all()
    return render_template('documento_recibo/proveedores/listaproveedores.html', proveedores=proveedores)

@bp.route('/crear', methods=['GET', 'POST'])
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

@bp.route('/editar')
def editar_proveedor():
    return render_template('documento_recibo/proveedores/editarproveedores.html')