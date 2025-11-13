from flask import Blueprint, render_template, request, flash, redirect, url_for
from wmsr.utils.export_excel import exportar_a_excel

from .auth import login_required # Importar el decorador de login requerido si es necesario
from .models import Ubicaciones, Categorias # Importar el modelo de Inventario y Ubicaciones
from . import db # Importar la base de datos

bp = Blueprint('ubicaciones', __name__, url_prefix='/ubicaciones')

@bp.route('/')
def lista_ubicaciones():
    # Obtenemos todas las ubicaciones y categorias de la base de datos
    ubicaciones = Ubicaciones.query.all()
    categorias = Categorias.query.all()

    # Mapeamos las categorías por su ID para un acceso rápido
    categorias_map = {c.cat_id: c.cat_nombre for c in categorias}

    return render_template('inventario/ubicaciones/listaubicaciones.html', ubicaciones=ubicaciones, categorias_map=categorias_map)

@bp.route('/crear', methods=('GET', 'POST'))
def crear_ubicacion():
    if request.method == 'POST':
        codigo_ubicacion = request.form.get('codigo_ubicacion')
        estanteria = request.form.get('estanteria')
        nivel = request.form.get('nivel')
        categoria = request.form.get('categoria')
        capacidad = request.form.get('capacidad')
        descripcion = request.form.get('descripcion')

        # validar campos obligatorios
        if not codigo_ubicacion or not estanteria or not nivel or not categoria or not capacidad:
            flash('Por favor, complete todos los campos obligatorios.', 'error')
            categorias = Categorias.query.all()
            return render_template('inventario/ubicaciones/crearubicaciones.html', categoria=categorias)
        
        # Validad unicidad del código de ubicación
        codigo_existente = Ubicaciones.query.filter_by(ubi_codigo=codigo_ubicacion).first()

        if codigo_existente:
            flash(f'La ubicación con código {codigo_ubicacion} ya existe.', 'error')
            categorias = Categorias.query.all()
            return render_template('inventario/ubicaciones/crearubicaciones.html', categoria=categorias)
        
        # Validar existencia de la categoría
        try:
            cat_id = int(categoria)
        except ValueError:
            flash('Categoría inválida. Por favor, seleccione una categoría válida.', 'error')
            categorias = Categorias.query.all()
            return render_template('inventario/ubicaciones/crearubicaciones.html', categoria=categorias)
        
        if not Categorias.query.get(cat_id):
            flash('La categoría seleccionada no existe.', 'error')
            categorias = Categorias.query.all()
            return render_template('inventario/ubicaciones/crearubicaciones.html', categoria=categorias)
        
        nueva_ubicacion = Ubicaciones(
            ubi_codigo=codigo_ubicacion,
            ubi_estanteria=estanteria,
            ubi_nivel=nivel,
            ubi_cat_id=cat_id,
            ubi_capacidad=capacidad,
            ubi_descripcion=descripcion)
        
        db.session.add(nueva_ubicacion)
        db.session.commit()
        flash('Ubicación creada exitosamente.', 'success')
        return redirect(url_for('ubicaciones.lista_ubicaciones'))

    return render_template('inventario/ubicaciones/crearubicaciones.html', categoria=Categorias.query.all())

@bp.route('/editar')
def editar_ubicacion():
    return render_template('inventario/ubicaciones/editarubicaciones.html')