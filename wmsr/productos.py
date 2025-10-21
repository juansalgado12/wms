from flask import blueprints, render_template

bp = blueprints.Blueprint('productos', __name__, url_prefix='/productos')

# Ruta para el catálogo de productos
@bp.route('/')
def catalogo():
    return render_template('productos/catalogo.html')

# Ruta para crear un nuevo producto
@bp.route('/crear')
def crear():
    return render_template('productos/crear.html')

# Ruta para editar un producto existente
@bp.route('/editar')
def editar():
    return render_template('productos/editar.html')