from flask import Blueprint, render_template, request, flash, redirect, url_for

#from .auth import login_required # Importar el decorador de login requerido si es necesario
#from .models import categorias cuando esta disponible el modelo categorias
#from wmsr import db  # cuando esta disponible la instancia de la base de datos

bp = Blueprint('categorias', __name__, url_prefix='/categorias')

# Ruta para la lista de categorías
@bp.route('/')
def lista_categorias(): 
    # Aquí iría la lógica para obtener la lista de categorías
    #categorias = Categorias.query.all()  # Ejemplo de consulta a la base de datos
    return render_template('productos/categorias/listacategorias.html')

# Ruta para crear una nueva categoría
@bp.route('/crear', methods=('GET', 'POST'))
def crear_categoria():
    # if request.method == 'POST':
    #     nombre = request.form.get('nombre') #obtener el nombre de la categoría del formulario
    #     descripcion = request.form.get('descripcion') #obtener la descripción de la categoría del formulario

    #     # Aquí iría la lógica para crear y guardar la nueva categoría
    #     nueva_categoria = Categorias(nombre, descripcion)
    #     # validar datos del formulario
    #     error = None
    #     nombre_categoria = Categorias.query.filter_by(nombre=nombre).first() #verificar si el nombre ya existe en la base de datos

    #     if nombre_categoria == None:
    #         #si no existe el nombre, agregar la categoría a la base de datos
    #         db.session.add(nueva_categoria)
    #         db.session.commit()
    #         flash('Categoría creada exitosamente.')
    #         return redirect(url_for('categorias.lista_categorias'))
    #     else:
    #         #devuelve error si el nombre ya existe
    #         error = f'La categoría {nombre} ya existe.'
    #     flash(error)
    return render_template('productos/categorias/crearcategorias.html')

# Ruta para editar una categoría existente
@bp.route('/editar')
def editar_categoria():
    return render_template('productos/categorias/editarcategoria.html')