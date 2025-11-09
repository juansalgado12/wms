from flask import Blueprint, render_template, request, flash, redirect, url_for

from wmsr.utils.export_excel import exportar_a_excel

from .auth import login_required # Importar el decorador de login requerido
from .models import Presentacion, Productos # Importar el modelo de Presentacion
from wmsr import db # Importar la base de datos

bp = Blueprint('presentacion', __name__, url_prefix='/presentacion')


@bp.route('/')
@login_required
def lista_presentaciones():

    # AquÍ iría la lógica para obtener la lista de presentaciones
    presentaciones = Presentacion.query.all() # Obtener todas las presentaciones
    return render_template('productos/presentacion/listapresentacion.html', presentaciones=presentaciones)


@bp.route('/crear', methods=('GET', 'POST'))
@login_required
def crear_presentacion():
    mensaje_exito = None

    if request.method == 'POST':
        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion')

        nombre_normalizado = nombre.strip().lower() if nombre else ''

        error = None
        nombre_presentacion = Presentacion.query.filter(db.func.lower(db.func.trim(Presentacion.pres_nombre)) == nombre_normalizado).first()

        if nombre_presentacion is None and nombre_normalizado:
            nueva_presentacion = Presentacion(nombre.strip(), descripcion)
            db.session.add(nueva_presentacion)
            db.session.commit()
            mensaje_exito = 'Presentación creada exitosamente.'
            flash(mensaje_exito, 'success')
            return redirect(url_for('presentacion.lista_presentaciones', mensaje_exito=mensaje_exito))
        else:
            error = f'La presentación "{nombre}" ya existe o el nombre es inválido.'
            flash(error)
    return render_template('productos/presentacion/crearpresentacion.html', mensaje_exito=mensaje_exito)


@bp.route('/editar/<int:id>', methods=('GET', 'POST'))
@login_required
def editar_presentacion(id):
    presentacion = Presentacion.query.get_or_404(id)

    if request.method == 'POST':
        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion')
        nombre_normalizado = nombre.strip().lower() if nombre else '' # Normalizar el nombre

        # Verificar si el nuevo nombre ya existe en otra presentación
        presentacion_existente = Presentacion.query.filter(db.func.lower(db.func.trim(Presentacion.pres_nombre)) == nombre_normalizado, Presentacion.pres_id != id).first()

        if presentacion_existente:
            flash(f'La presentación "{nombre}" ya existe.')
        elif not nombre_normalizado:
            flash('El nombre de la presentación no puede estar vacío.')
        else:
            presentacion.pres_nombre = nombre.strip()
            presentacion.pres_descripcion = descripcion
            db.session.commit()

            mensaje_exito = 'Presentación actualizada exitosamente.'
            flash(mensaje_exito, 'success')
            return redirect(url_for('presentacion.lista_presentaciones', mensaje_exito=mensaje_exito))
    return render_template('productos/presentacion/editarpresentacion.html', presentacion=presentacion)


@bp.route('/borrar/<int:id>', methods=('GET', 'POST'))
@login_required
def borrar_presentacion(id):
    presentacion = Presentacion.query.get_or_404(id)

    # Verificar si la presentación está asignada a algún producto
    
    productos_asociados = Productos.query.filter_by(pro_pres_id=id).count()
    if productos_asociados > 0:
        flash(f'No se puede eliminar la presentación "{presentacion.pres_nombre}" porque está asociada a {productos_asociados} producto(s).', 'error')
        return redirect(url_for('presentacion.lista_presentaciones'))

    db.session.delete(presentacion)
    db.session.commit()

    mensaje_exito = 'Presentación eliminada exitosamente.'
    flash(mensaje_exito, 'success')
    
    return redirect(url_for('presentacion.lista_presentaciones', mensaje_exito=mensaje_exito))

@bp.route('/exportar_excel')
@login_required
def exportar_presentaciones_excel():
    presentaciones = Presentacion.query.all()

    data = [
        {
            'ID': p.pres_id,
            'Nombre': p.pres_nombre,
            'Descripción': p.pres_descripcion
        } 
        for p in presentaciones
    ]

    columnas = ['ID', 'Nombre', 'Descripción']
    return exportar_a_excel('presentaciones', columnas, data)