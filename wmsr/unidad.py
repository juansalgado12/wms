from flask import Blueprint, render_template, redirect, flash, request, url_for

#from .auth import login_required
#from .models import Unidad cuando se implemente el modelo
#from wmsr import db cuando se implemente la base de datos

bp = Blueprint('unidad', __name__, url_prefix='/unidad')

@bp.route('/')
def lista_unidades():
    # unidades = Unidad.query.all() #cuando se implemente el modelo
    return render_template('productos/unidad/listaunidad.html') #, unidades=unidades

@bp.route('/crear', methods=('GET', 'POST'))
def crear_unidad():
    # if request.method == 'POST':
    #     nombre = request.form.get('nombre')
    #     descripcion = request.form.get('descripcion')
    #     # Aquí se agregarían las validaciones y la lógica para guardar la unidad en la base de datos

    #     unidad = Unidad(nombre, descripcion)

    #     #validaciones
    #     error = None
    #     nombre_unidad = Unidad.query.filter_by(nombre=nombre).first()
    #     if nombre_unidad == None:
    #         #registrar en la base de datos
    #         db.session.add(unidad)
    #         db.session.commit()
    #         flash('Unidad creada exitosamente.')
    #         return redirect(url_for('unidad.lista_unidades'))
    #     else:
    #         error = 'La unidad ya existe.'
    #     flash(error)
    return render_template('productos/unidad/crearunidad.html')

@bp.route('/editar')
def editar_unidad():
    return render_template('productos/unidad/editarunidad.html')