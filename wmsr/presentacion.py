from flask import Blueprint, render_template, request, flash, redirect, url_for

#from .auth import login_required
#from .models import Presentacion cuando se implemente el modelo
#from wmsr import db cuando se implemente la base de datos

bp = Blueprint('presentacion', __name__, url_prefix='/presentacion')

@bp.route('/')
def lista_presentaciones():
    # presentaciones = Presentacion.query.all() #cuando se implemente el modelo
    return render_template('productos/presentacion/listapresentacion.html') #, presentaciones=presentaciones

@bp.route('/crear')
def crear_presentacion():
    # if request.method == 'POST':
    #     # Obtener datos del formulario
    #     nombre = request.form.get('nombre')
    #     descripcion = request.form.get('descripcion')

    #     presentacion = Presentacion(nombre, descripcion)

    #     error = None
    #     nombre_presentacion = Presentacion.query.filter_by(nombre=nombre).first()

    #     if nombre_presentacion == None:
    #         #registrar en la base de datos
    #         db.session.add(presentacion)
    #         db.session.commit()
    #         flash('Presentación creada exitosamente.')
    #         return redirect(url_for('presentacion.lista_presentaciones'))
    #     else:
    #         error = 'La presentación ya existe.'
    #     flash(error)
    return render_template('productos/presentacion/crearpresentacion.html')

@bp.route('/editar')
def editar_presentacion():
    return render_template('productos/presentacion/editarpresentacion.html')
