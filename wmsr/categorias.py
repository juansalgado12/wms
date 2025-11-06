from flask import Blueprint, render_template, request, flash, redirect, url_for

from .auth import login_required # Importar el decorador de login requerido si es necesario
from .models import Categorias, Productos # Importar el modelo de Categorías
from . import db # Importar la base de datos

bp = Blueprint('categorias', __name__, url_prefix='/categorias')


# Ruta para la lista de categorías
@bp.route('/')
@login_required
def lista_categorias(): 

    # Aquí iría la lógica para obtener la lista de categorías
    categorias = Categorias.query.all()  # Ejemplo de consulta a la base de datos
    mensaje_exito = request.args.get('mensaje_exito') # Obtener mensaje de éxito si existe
    return render_template('productos/categorias/listacategorias.html', categorias=categorias, mensaje_exito=mensaje_exito)


# Ruta para crear una nueva categoría
@bp.route('/crear', methods=('GET', 'POST'))
@login_required
def crear_categoria():
    mensaje_exito = None

    if request.method == 'POST':
        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion')

        nombre_normalizado = nombre.strip().lower() if nombre else ''

        error = None
        nombre_categoria = Categorias.query.filter(
            db.func.lower(db.func.trim(Categorias.cat_nombre)) == nombre_normalizado
        ).first() 

        if nombre_categoria is None and nombre_normalizado:
            nueva_categoria = Categorias(nombre.strip(), descripcion)
            db.session.add(nueva_categoria)
            db.session.commit()
            mensaje_exito = 'Categoría creada exitosamente.'
            flash(mensaje_exito, 'success')
            return redirect(url_for('categorias.lista_categorias', mensaje_exito=mensaje_exito))
        else:
            error = f'La categoría "{nombre}" ya existe o el nombre es inválido.'
            flash(error)
    return render_template('productos/categorias/crearcategorias.html', mensaje_exito=mensaje_exito)


# Ruta para editar una categoría existente
@bp.route('/editar/<int:id>', methods=('GET', 'POST'))
@login_required
def editar_categoria(id):
    categoria = Categorias.query.get_or_404(id)

    if request.method == 'POST':
        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion')
        nombre_normalizado = nombre.strip().lower() if nombre else '' # Normalizar el nombre

        # Verificar si el nombre ya existe en otra categoría
        categoria_existente = Categorias.query.filter(
            db.func.lower(db.func.trim(Categorias.cat_nombre)) == nombre_normalizado,
            Categorias.cat_id != id
        ).first()

        if categoria_existente:
            flash(f'La categoría "{nombre}" ya existe.')
        elif not nombre_normalizado:
            flash('El nombre de la categoría no puede estar vacío.')
        else:
            categoria.cat_nombre = nombre.strip()
            categoria.cat_descripcion = descripcion
            db.session.commit()
            
            mensaje_exito = 'Categoría actualizada exitosamente.'
            flash(mensaje_exito , 'success')
            return redirect(url_for('categorias.lista_categorias', mensaje_exito=mensaje_exito))
    return render_template('productos/categorias/editarcategorias.html', categoria=categoria)


@bp.route('/borrar/<int:id>', methods=('GET', 'POST'))
@login_required
def borrar_categoria(id):
    categoria = Categorias.query.get_or_404(id)
    # Verificar si la categoría está asignada a algún producto o ubicación
    
    productos_asociados = Productos.query.filter_by(pro_cat_id=id).count()
    if productos_asociados > 0:
        flash(f'No se puede eliminar la categoría "{categoria.cat_nombre}" porque está asociada a {productos_asociados} producto(s).', 'error')
        return redirect(url_for('categorias.lista_categorias'))

    db.session.delete(categoria)
    db.session.commit()

    mensaje_exito = 'Categoría borrada exitosamente.'
    flash(mensaje_exito, 'success')
    
    return redirect(url_for('categorias.lista_categorias', mensaje_exito=mensaje_exito))