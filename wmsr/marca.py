from flask import Blueprint, render_template, request, redirect, url_for, flash

#from .auth import login_required
#from .model import Marca cuando se implemente la base de datos
#from wmsr import db cuando se implemente la base de datos

bp = Blueprint('marca', __name__, url_prefix='/marcas')

@bp.route('/')
def lista_marcas():
    # unidades = Unidad.query.all() cuando se implemente la base de datos
    return render_template('productos/marca/listamarcas.html') #, unidades = unidades cuando se implemente la base de datos

@bp.route('/crear', methods=('GET', 'POST'))
def crear_marca():
    # if request.method == 'POST':
    #     nombre = request.form.get('nombre')
    #     descripcion = request.form.get('descripcion')

    #     marca = Marca(nombre, descripcion)

    #     #validar datos

    #     error = None
    #     nombre_marca = Marca.query.filter_by(nombre=nombre).first()
    #     if nombre_marca == None:
    #         #registrar la marca en la base de datos
    #         db.session.add(marca)
    #         db.session.commit()
    #         flash('Marca creada exitosamente.')
    #         return redirect(url_for('marca.lista_marcas'))
    #     else:
    #         error = 'La marca ya existe.' 
    #     flash(error)
    return render_template('productos/marca/crearmarca.html')

@bp.route('/editar')
def editar_marca():
    return render_template('productos/marca/editarmarca.html')