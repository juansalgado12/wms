from flask import blueprints, render_template

bp = blueprints.Blueprint('productos', __name__, url_prefix='/productos')

@bp.route('/')
def catalogo():
    return render_template('productos/catalogo.html')

@bp.route('/crear')
def crear():
    return render_template('productos/crear.html')

@bp.route('/editar')
def editar():
    return render_template('productos/editar.html')