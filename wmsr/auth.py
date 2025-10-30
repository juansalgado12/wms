from flask import blueprints, render_template, request, session, url_for, redirect, flash, g
#blueprint para las rutas
#render_template para renderizar las plantillas HTML
#request para manejar las solicitudes HTTP
#session para manejar la sesión del usuario
#url_for para generar URLs para las rutas
#redirect para redirigir a otras rutas
#flash para mostrar mensajes flash
#g para almacenar datos durante la solicitud (o guardar datos relacionados con la sesion de usuario)

from werkzeug.security import generate_password_hash, check_password_hash
#generate_password_hash para hashear contraseñas
#check_password_hash para verificar contraseñas hasheadas

from .models import Usuarios
from wmsr import db 

bp = blueprints.Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/registro', methods=('GET', 'POST'))
def registro():
    if request.method == 'POST': #si el metodo es POST
        username = request.form.get('username') #obtener el nombre de usuario del formulario
        email = request.form.get('email')#obtener el email del formulario
        password = request.form.get('password')#obtener la contraseña del formulario

        # Validación de contraseña
        error = None
        # Requisitos de la contraseña
        requisitos = []
        if not (8 <= len(password) <= 40): # longitud entre 8 y 40 caracteres
            requisitos.append('tener entre 8 y 40 caracteres')
        if not any(c.isdigit() for c in password): # al menos un número
            requisitos.append('contener al menos un número')
        if not any(c.isupper() for c in password): # al menos una letra mayúscula
            requisitos.append('contener al menos una letra mayúscula')
        if requisitos: #si hay requisitos no cumplidos
            error = 'La contraseña debe ' + ', '.join(requisitos) + '.'

        user_email = Usuarios.query.filter_by(usu_email=email).first() #verificar si el email ya existe en la base de datos

        if error:
            flash(error, 'error')
        elif user_email is None:
            user = Usuarios(usu_nombre=username, usu_email=email, usu_password=generate_password_hash(password))
            db.session.add(user)
            db.session.commit()
            flash('Cuenta creada exitosamente. Ahora puedes iniciar sesión.', 'success')
            return redirect(url_for('auth.login'))
        else:
            error = f'El correo {email} ya está registrado.'
            flash(error, 'error')
    return render_template('auth/registro.html')

@bp.route('/login', methods = ('GET', 'POST'))
def login():
    if request.method == 'POST': #si el metodo es POST
        email = request.form.get('email')#obtener el email del formulario
        password = request.form.get('password')#obtener la contraseña del formulario

        #validar los datos 
        error = None
        user = Usuarios.query.filter_by(usu_email=email).first() #buscar el usuario por email
        if user is None:
            error = 'Datos incorrectos. Por favor, intente de nuevo.'
        elif not check_password_hash(user.usu_password, password):
            error = 'Datos incorrectos. Por favor, intente de nuevo.'
        
        #iniciar sesion si no hay errores
        if error is None:
            session.clear() #limpiar la sesion
            session['usu_id'] = user.usu_id #guardar el id del usuario en la sesion
            return redirect(url_for('home.almacen')) #redireccionar a la pagina de almacen
        flash(error, 'error')
        
    return render_template('auth/login.html')

#Mantener la sesión del usuario
@bp.before_app_request
def mantener_sesion():
    user_id = session.get('usu_id')#obtener el id del usuario de la sesion

    if user_id is None:
        g.user = None #si no hay usuario, g.user es None
    else:
        g.user = Usuarios.query.get_or_404(user_id)
        #obtener el usuario de la base de datos
        #g.user almacena el usuario durante la solicitud

#Cerrar sesión
@bp.route('/logout')
def logout():
    session.clear() #limpiar la sesion
    return redirect(url_for('home.welcome')) #redireccionar a la pagina de bienvenida

# decorador para proteger rutas que requieren autenticación
import functools
def login_required(view): 
    @functools.wraps(view) #preservar la información de la vista original
    def wrapped_views(**kwargs): #funcion envuelta
        if g.user is None: #si no hay usuario en g
            return redirect(url_for('auth.login')) #redireccionar a la pagina de login
        return view(**kwargs) #si hay usuario, llamar a la vista original
    return wrapped_views

@bp.route('/perfil/<int:user_id>', methods=('GET', 'POST'))
def perfil(user_id):
    user = Usuarios.query.get_or_404(user_id) #obtener el usuario por id o 404 si no existe

    # Manejar la actualización del perfil, solo usuario y contraseña por ahora
    if request.method == 'POST':
        user.usu_nombre = request.form.get('nombre')
        password = request.form.get('password')

        error = None
        # Validación de contraseña (igual que en registro)
        requisitos = []

        if not password:#si la contraseña esta vacia
            error = 'La contraseña no puede estar vacía.'

        if password: #si se proporciona una nueva contraseña
            if not (8 <= len(password) <= 40):
                requisitos.append('tener entre 8 y 40 caracteres')
            if not any(c.isdigit() for c in password):
                requisitos.append('contener al menos un número')
            if not any(c.isupper() for c in password):
                requisitos.append('contener al menos una letra mayúscula')
            if requisitos:
                error = 'La contraseña debe ' + ', '.join(requisitos) + '.'
            else:
                user.usu_password = generate_password_hash(password)
        if error:
            flash(error, 'error')
        else:
            db.session.commit()
            flash('Perfil actualizado exitosamente.', 'success')
            return redirect(url_for('auth.perfil', user_id=user.usu_id))
    return render_template('auth/perfil.html', user=user)#renderizar la plantilla de perfil con el usuario