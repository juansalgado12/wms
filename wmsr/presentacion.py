from flask import Blueprint, render_template, request, flash, redirect, url_for

from .auth import login_required # Importar el decorador de login requerido
from .models import Presentacion # Importar el modelo de Presentacion
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

@bp.route('/editar')
@login_required
def editar_presentacion():
    return render_template('productos/presentacion/editarpresentacion.html')
