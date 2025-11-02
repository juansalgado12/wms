from flask import Blueprint, render_template, request, redirect, url_for, flash

from .auth import login_required # Importar el decorador de login requerido si es necesario
from .models import Marca # Importar el modelo de Marca
from wmsr import db # Importar la base de datos

bp = Blueprint('marca', __name__, url_prefix='/marcas')

@bp.route('/')
@login_required
def lista_marcas():

    # AquÍ iría la lógica para obtener la lista de marcas
    marcas = Marca.query.all()
    #mensaje_exito = request.args.get('mensaje_exito') # Obtener mensaje de éxito si existe
    return render_template('productos/marca/listamarcas.html', marcas=marcas)

@bp.route('/crear', methods=('GET', 'POST'))
def crear_marca():
    mensaje_exito = None

    if request.method == 'POST':
        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion')

        nombre_normalizado = nombre.strip().lower() if nombre else ''

        error = None
        nombre_marca = Marca.query.filter(db.func.lower(db.func.trim(Marca.mar_nombre)) == nombre_normalizado).first()

        if nombre_marca is None and nombre_normalizado:
            nueva_marca = Marca(nombre.strip(), descripcion)
            db.session.add(nueva_marca)
            db.session.commit()
            mensaje_exito = 'Marca creada exitosamente.'
            flash(mensaje_exito, 'success')
            return redirect(url_for('marca.lista_marcas', mensaje_exito=mensaje_exito))
        else:
            error = f'La marca "{nombre}" ya existe o el nombre es inválido.'
            flash(error)
    return render_template('productos/marca/crearmarca.html', mensaje_exito=mensaje_exito)

@bp.route('/editar')
def editar_marca():
    return render_template('productos/marca/editarmarca.html')

@bp.route('/borrar')
def borrar_marca():
    return redirect(url_for('marca.lista_marcas'))