from flask import blueprints, render_template

bp = blueprints.Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/registro')
def registro():
    return render_template('auth/registro.html')

@bp.route('/login')
def login():
    return render_template('auth/login.html')

@bp.route('/perfil')
def perfil():
    return render_template('auth/profile.html')