from flask import Blueprint, render_template, request, flash, redirect, url_for

from .auth import login_required # Importar el decorador de login requerido si es necesario
from .models import Categorias # Importar el modelo de Categorías
from . import db # Importar la base de datos

bp = Blueprint('categorias', __name__, url_prefix='/categorias')

# Ruta para la lista de categorías
@bp.route('/')
@login_required
def lista_categorias(): 
    # Aquí iría la lógica para obtener la lista de categorías
    categorias = Categorias.query.all()  # Ejemplo de consulta a la base de datos
    return render_template('productos/categorias/listacategorias.html', categorias=categorias)

# Ruta para crear una nueva categoría
@bp.route('/crear', methods=('GET', 'POST'))
@login_required
def crear_categoria():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion')

        # Normalizar el nombre: quitar espacios, convertir a minúsculas
        nombre_normalizado = nombre.strip().lower() if nombre else ''

        error = None
        # Buscar por nombre normalizado
        nombre_categoria = Categorias.query.filter(
            db.func.lower(db.func.trim(Categorias.cat_nombre)) == nombre_normalizado
        ).first() 

        if nombre_categoria is None and nombre_normalizado:
            nueva_categoria = Categorias(nombre.strip(), descripcion)
            db.session.add(nueva_categoria)
            db.session.commit()
            mensaje_exito = 'Categoría creada exitosamente.'
            return redirect(url_for('categorias.lista_categorias', mensaje_exito=mensaje_exito))
        else:
            error = f'La categoría "{nombre}" ya existe o el nombre es inválido.'
        flash(error)
    return render_template('productos/categorias/crearcategorias.html')

# Ruta para editar una categoría existente
@bp.route('/editar')
@login_required
def editar_categoria():
    return render_template('productos/categorias/editarcategoria.html')