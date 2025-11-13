from flask import Blueprint, render_template, request, flash, redirect, url_for
from wmsr.utils.export_excel import exportar_a_excel

from .auth import login_required # Importar el decorador de login requerido si es necesario
from .models import Inventario, Ubicaciones, Productos # Importar el modelo de Inventario, Ubicaciones y Productos
from . import db # Importar la base de datos
from datetime import datetime # Importar datetime para manejar fechas
from zoneinfo import ZoneInfo # Importar ZoneInfo para zonas horarias

bp = Blueprint('inventario', __name__, url_prefix='/inventario')

# Ruta para la lista de inventario
@bp.route('/')
@login_required
def lista_inventario():
    # Obtenemos todos los registros de inventario, productos y ubicaciones de la base de datos

    inventario = Inventario.query.all()
    productos = Productos.query.all()
    ubicaciones = Ubicaciones.query.all()

    # Mapeamos los productos y ubicaciones por su código para un acceso rápido
    productos_map = {p.pro_codigo: p for p in productos}
    ubicaciones_map = {u.ubi_codigo: u for u in ubicaciones}

    return render_template('inventario/listainventario.html', inventario=inventario, productos_map=productos_map, ubicaciones_map=ubicaciones_map)

@bp.route('/crear', methods=('GET', 'POST'))
@login_required
def crear_inventario():

    if request.method == 'POST':
        # Obtener datos del formulario
        producto_codigo = request.form.get('producto')
        ubicacion_codigo = request.form.get('ubicacion')

        # Validar campos obligatorios
        if not producto_codigo or not ubicacion_codigo:
            flash('Por favor, complete todos los campos obligatorios.', 'error')
            return redirect(url_for('inventario.crear_inventario', producto=producto_codigo, ubicacion=ubicacion_codigo))
        
        # Obtener producto y ubicación desde la BD
        producto = Productos.query.get(producto_codigo)
        ubicacion = Ubicaciones.query.get(ubicacion_codigo)
        
        # Validar existencia de los productos
        try:
            pro_codigo = str(producto_codigo)
        except (ValueError, TypeError):
            flash('Producto inválido. Por favor, seleccione un producto válido.', 'error')
            productos = Productos.query.all()
            return render_template('inventario/crearinventario.html', producto=productos)
        if not Productos.query.get(pro_codigo):
            flash('El producto seleccionado no existe. Por favor, seleccione un producto válido.', 'error')
            productos = Productos.query.all()
            return render_template('inventario/crearinventario.html', producto=productos)
        
        # Validar existencia de las ubicaciones
        try:
            ubi_codigo = str(ubicacion_codigo)
        except (ValueError, TypeError):
            flash('Ubicación inválida. Por favor, seleccione una ubicación válida.', 'error')
            ubicaciones = Ubicaciones.query.all()
            return render_template('inventario/crearinventario.html', ubicacion=ubicaciones)
        if not Ubicaciones.query.get(ubi_codigo):
            flash('La ubicación seleccionada no existe. Por favor, seleccione una ubicación válida.', 'error')
            ubicaciones = Ubicaciones.query.all()
            return render_template('inventario/crearinventario.html', ubicacion=ubicaciones)
        
        # Validar si la ubicación ya tiene un inventario asignado
        inventario_existente = Inventario.query.filter_by(inv_cod_ubicacion=ubi_codigo).first()
        if inventario_existente:
            flash(f'La ubicación con código {ubi_codigo} ya tiene un inventario asignado.', 'error')
            productos = Productos.query.all()
            ubicaciones = Ubicaciones.query.all()
            return render_template('inventario/crearinventario.html', producto=productos, ubicacion=ubicaciones)

        # Validar que la categoría del producto coincida con la categoría de la ubicación
        if producto.pro_cat_id != ubicacion.ubi_cat_id:
            flash('La categoría del producto no coincide con la categoría de la ubicación.', 'error')
            productos = Productos.query.all()
            ubicaciones = Ubicaciones.query.all()
            return render_template('inventario/crearinventario.html', producto=productos, ubicacion=ubicaciones)
        
        # Establecer la fecha de creación
        tz_colombia = 'America/Bogota'
        fecha_str = request.form.get('fecha')
        if fecha_str:
            try:
                fecha = datetime.strptime(fecha_str, '%Y-%m-%d')
                # establecer la zona horaria de Colombia
                fecha = fecha.replace(tzinfo=ZoneInfo(tz_colombia))
            except ValueError:
                flash('Formato de fecha inválido. Use AAAA-MM-DD.', 'error')
                productos = Productos.query.all()
                ubicaciones = Ubicaciones.query.all()
                return render_template('inventario/crearinventario.html', producto=productos, ubicacion=ubicaciones)
        else:
            # Usar la fecha y hora actual si no se proporciona
            fecha = datetime.now(ZoneInfo(tz_colombia))
        
        # Establecer la cantidad y saldo inicial en 0
        cantidad = 0
        saldo = 0
        # Crear nuevo registro de inventario
        nuevo_inventario = Inventario(
            inv_pro_codigo=pro_codigo,
            inv_cod_ubicacion=ubi_codigo,
            inv_cantidad=cantidad,
            inv_saldo=saldo,
            inv_fecha_actualizacion=fecha
        )

        db.session.add(nuevo_inventario)
        db.session.commit()
        flash('Inventario creado exitosamente.', 'success')
        return redirect(url_for('inventario.lista_inventario'))
        
    return render_template('inventario/crearinventario.html', producto=Productos.query.all(), ubicacion=Ubicaciones.query.all())

@bp.route('/editar/<int:id>', methods=('GET', 'POST'))
@login_required
def editar_inventario(id):
    return render_template('inventario/editarinventario.html')