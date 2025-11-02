from flask import Blueprint, render_template, redirect, flash, request, url_for

from .auth import login_required # Importar el decorador de login requerido
from .models import Unidad # Importar el modelo de Unidad
from wmsr import db # Importar la base de datos

bp = Blueprint('unidad', __name__, url_prefix='/unidad')

@bp.route('/')
@login_required
def lista_unidades():
    unidades = Unidad.query.all() #obtener todas las unidades
    return render_template('productos/unidad/listaunidad.html', unidades=unidades)

@bp.route('/crear', methods=('GET', 'POST'))
@login_required
def crear_unidad():
    mensaje_exito = None

    if request.method == 'POST':
        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion')

        nombre_normalizado = nombre.strip().lower() if nombre else ''

        error = None
        nombre_unidad = Unidad.query.filter(db.func.lower(db.func.trim(Unidad.uni_nombre)) == nombre_normalizado).first()

        if nombre_unidad is None and nombre_normalizado:
            nueva_unidad = Unidad(nombre.strip(), descripcion)
            db.session.add(nueva_unidad)
            db.session.commit()
            mensaje_exito = 'Unidad creada exitosamente.'
            flash(mensaje_exito, 'success')
            return redirect(url_for('unidad.lista_unidades', mensaje_exito=mensaje_exito))
        else:
            error = f'La unidad "{nombre}" ya existe o el nombre es inválido.'
            flash(error)
    return render_template('productos/unidad/crearunidad.html', mensaje_exito=mensaje_exito)


@bp.route('/editar')
@login_required
def editar_unidad():
    return render_template('productos/unidad/editarunidad.html')