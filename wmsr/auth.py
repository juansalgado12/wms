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

        user = Usuarios(usu_nombre=username, usu_email=email, usu_password=generate_password_hash(password)) #crear una instancia del usuario con la contraseña hasheada

        # validar los datos del formulario
        error = None
        user_email = Usuarios.query.filter_by(usu_email=email).first() #verificar si el email ya existe en la base de datos

        if user_email == None:
            #si no existe el email, agregar el usuario a la base de datos
            db.session.add(user)
            db.session.commit()
            flash('Cuenta creada exitosamente. Ahora puedes iniciar sesión.', 'success')
            return redirect(url_for('auth.login'))
        else:
            #de lo contrario, mostrar un mensaje de error
            error = f'El correo {email} ya está registrado.'
            flash(error, 'error')
    return render_template('auth/registro.html')

@bp.route('/login', methods = ('GET', 'POST'))
def login():
    # if request.method == 'POST': #si el metodo es POST
    #     email = request.form.get('email')#obtener el email del formulario
    #     password = request.form.get('password')#obtener la contraseña del formulario

    #     #validar los datos 
    #     error = None
    #     user = User.query.filter_by(email = email).first() #buscar el usuario por email
    #     if user == None or not check_password_hash(user.password, password):
    #         #si no existe el usuario o la contraseña es incorrecta
    #         error = 'Datos incorrectos. Por favor, intente de nuevo.'
        
    #     #iniciar sesion si no hay errores
    #     if error is None:
    #         session.clear() #limpiar la sesion
    #         session['user_id'] = user.id #guardar el id del usuario en la sesion
    #         return redirect(url_for('home.almacen')) #redireccionar a la pagina de almacen
    #     flash(error)
        
    return render_template('auth/login.html')

# Mantener la sesión del usuario
# @bp.before_app_request
# def mantener_sesion():
#     user_id = session.get('user_id')#obtener el id del usuario de la sesion

#     if user_id is None:
#         g.user = None #si no hay usuario, g.user es None
#     else:
#         g.user = User.query.get_or_404(user_id)#obtener el usuario de la base de datos
#         #g.user almacena el usuario durante la solicitud

#Cerrar sesión
# @bp.route('/logout')
# def logout():
#     session.clear() #limpiar la sesion
#     return redirect(url_for('home.welcome')) #redireccionar a la pagina de bienvenida

#decorador para proteger rutas que requieren autenticación
# import functools
# def login_required(view): 
#     @functools.wraps(view) #preservar la información de la vista original
#     def wrapped_views(**kwargs): #funcion envuelta
#         if g.user is None: #si no hay usuario en g
#             return redirect(url_for('auth.login')) #redireccionar a la pagina de login
#         return view(**kwargs) #si hay usuario, llamar a la vista original
#     return wrapped_views

@bp.route('/perfil')
def perfil():
    return render_template('auth/profile.html')