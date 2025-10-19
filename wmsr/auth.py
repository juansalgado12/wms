from flask import blueprints, render_template

bp = blueprints.Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/registro')
def registro():
    return ('Pagina de registro de usuario')

@bp.route('/inicio-sesion')
def inicio_sesion():
    return ('Pagina de inicio de sesion de usuario')

@bp.route('/perfil')
def perfil():
    return ('Pagina de perfil de usuario')