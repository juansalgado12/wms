from flask import blueprints, render_template, request, session, url_for, redirect, redirect, flash, g
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

#from .models import User (cuando esta disponible el modelo User)
#from wmsr import db (cuando esta disponible la instancia de la base de datos)

bp = blueprints.Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/registro', methods=('GET', 'POST'))
def registro():
    # if request.method == 'POST': #si el metodo es POST
    #     username = request.form.get('username') #obtener el nombre de usuario del formulario
    #     email = request.form.get('email')#obtener el email del formulario
    #     password = request.form.get('password')#obtener la contraseña del formulario

    #     user = User(username, email, generate_password_hash(password)) #crear una instancia del usuario con la contraseña hasheada

    #     # validar los datos del formulario
    #     error = None
    #     user_email = User.query.filter_by(email = email).first() #verificar si el email ya existe en la base de datos

    #     if user_email == None:
    #         #si no existe el email, agregar el usuario a la base de datos
    #         db.session.add(user)
    #         db.session.commit()
    #         return redirect(url_for('auth.login'))
    #     else:
    #         #de lo contrario, mostrar un mensaje de error
    #         error = f'El correo {email}' 'ya está registrado.'
    #     flash(error)
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

@bp.route('/perfil')
def perfil():
    return render_template('auth/profile.html')