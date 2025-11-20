from operator import inv
from flask import Blueprint, render_template, request, flash, redirect, url_for
from wmsr.utils.export_excel import exportar_a_excel

from .auth import login_required # Importar el decorador de login requerido si es necesario
from sqlalchemy import or_
from .models import Inventario, Ubicaciones, Productos, Categorias # Importar el modelo de Inventario, Ubicaciones, Productos y Categorias
from . import db # Importar la base de datos
from datetime import datetime # Importar datetime para manejar fechas
from zoneinfo import ZoneInfo # Importar ZoneInfo para zonas horarias

bp = Blueprint('inventario', __name__, url_prefix='/inventario')

# Ruta para la lista de inventario
@bp.route('/')
@login_required
def lista_inventario():
    # Obtenemos todos los registros de inventario, productos y ubicaciones de la base de datos

    # Soportar búsqueda por query string ?q=texto
    q = (request.args.get('q') or '').strip()

    productos = Productos.query.all()
    ubicaciones = Ubicaciones.query.all()

    if q:
        # Buscar por nombre de producto, código de producto, código de ubicación o nombre de categoría
        inventario = (
            db.session.query(Inventario)
            .join(Productos, Inventario.inv_pro_codigo == Productos.pro_codigo)
            .join(Ubicaciones, Inventario.inv_cod_ubicacion == Ubicaciones.ubi_codigo)
            .outerjoin(Categorias, Productos.pro_cat_id == Categorias.cat_id)
            .filter(
                or_(
                    Productos.pro_nombre.ilike(f"%{q}%"),
                    Productos.pro_codigo.ilike(f"%{q}%"),
                    Ubicaciones.ubi_codigo.ilike(f"%{q}%"),
                    Categorias.cat_nombre.ilike(f"%{q}%")
                )
            )
            .all()
        )
    else:
        inventario = Inventario.query.all()

    # Mapeamos los productos y ubicaciones por su código para un acceso rápido
    productos_map = {p.pro_codigo: p for p in productos}
    ubicaciones_map = {u.ubi_codigo: u for u in ubicaciones}

    return render_template('inventario/listainventario.html', inventario=inventario, productos_map=productos_map, ubicaciones_map=ubicaciones_map, q=q)

@bp.route('/crear', methods=('GET', 'POST'))
@login_required
def crear_inventario():
    # Preparar datos que se usan en GET y en posibles re-renders tras errores POST
    productos = Productos.query.all()
    ubicaciones = Ubicaciones.query.all()
    categorias = Categorias.query.all()
    categorias_map = {c.cat_id: c.cat_nombre for c in categorias}

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
            ubicaciones = Ubicaciones.query.all()
            return render_template('inventario/crearinventario.html', producto=productos, ubicacion=ubicaciones, categorias_map=categorias_map)
        if not Productos.query.get(pro_codigo):
            flash('El producto seleccionado no existe. Por favor, seleccione un producto válido.', 'error')
            productos = Productos.query.all()
            ubicaciones = Ubicaciones.query.all()
            return render_template('inventario/crearinventario.html', producto=productos, ubicacion=ubicaciones, categorias_map=categorias_map)
        
        # Validar existencia de las ubicaciones
        try:
            ubi_codigo = str(ubicacion_codigo)
        except (ValueError, TypeError):
            flash('Ubicación inválida. Por favor, seleccione una ubicación válida.', 'error')
            productos = Productos.query.all()
            ubicaciones = Ubicaciones.query.all()
            return render_template('inventario/crearinventario.html', producto=productos, ubicacion=ubicaciones, categorias_map=categorias_map)
        if not Ubicaciones.query.get(ubi_codigo):
            flash('La ubicación seleccionada no existe. Por favor, seleccione una ubicación válida.', 'error')
            productos = Productos.query.all()
            ubicaciones = Ubicaciones.query.all()
            return render_template('inventario/crearinventario.html', producto=productos, ubicacion=ubicaciones, categorias_map=categorias_map)
        
        # Validar si la ubicación ya tiene un inventario asignado
        inventario_existente = Inventario.query.filter_by(inv_cod_ubicacion=ubi_codigo).first()
        if inventario_existente:
            flash(f'La ubicación con código {ubi_codigo} ya tiene un inventario asignado.', 'error')
            productos = Productos.query.all()
            ubicaciones = Ubicaciones.query.all()
            return render_template('inventario/crearinventario.html', producto=productos, ubicacion=ubicaciones, categorias_map=categorias_map)

        # Validar que la categoría del producto coincida con la categoría de la ubicación
        if producto.pro_cat_id != ubicacion.ubi_cat_id:
            flash('La categoría del producto no coincide con la categoría de la ubicación.', 'error')
            productos = Productos.query.all()
            ubicaciones = Ubicaciones.query.all()
            return render_template('inventario/crearinventario.html', producto=productos, ubicacion=ubicaciones, categorias_map=categorias_map)
        
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
                return render_template('inventario/crearinventario.html', producto=productos, ubicacion=ubicaciones, categorias_map=categorias_map)
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
        
    return render_template('inventario/crearinventario.html', producto=productos, ubicacion=ubicaciones, categorias_map=categorias_map)

@bp.route('/editar/<int:id>', methods=('GET', 'POST'))
@login_required
def editar_inventario(id):
    inventario = Inventario.query.get_or_404(id)
    if not inventario:
        flash(f'El inventario con ID {id} no existe.', 'error')
        return redirect(url_for('inventario.lista_inventario'))

    # Preparar listas y mapa de categorias para re-renders y la plantilla
    productos = Productos.query.all()
    ubicaciones = Ubicaciones.query.all()
    categorias = Categorias.query.all()
    categorias_map = {c.cat_id: c.cat_nombre for c in categorias}

    if request.method == 'POST':
        # Leer datos del formulario
        producto_codigo = request.form.get('producto')
        ubicacion_codigo = request.form.get('ubicacion')
        cantidad = request.form.get('cantidad')
        saldo = request.form.get('saldo')

        # Validar campos obligatorios
        if not producto_codigo or not ubicacion_codigo or cantidad is None or saldo is None:
            flash('Por favor, complete todos los campos obligatorios.', 'error')
            return render_template('inventario/editarinventario.html', inventario=inventario, producto=productos, ubicacion=ubicaciones, categorias_map=categorias_map)
        
        # Validar existencia de los productos
        try:
            pro_codigo = str(producto_codigo)
        except (ValueError, TypeError):
            flash('Producto inválido. Por favor, seleccione un producto válido.', 'error')
            productos = Productos.query.all()
            ubicaciones = Ubicaciones.query.all()
            return render_template('inventario/editarinventario.html', inventario=inventario, producto=productos, ubicacion=ubicaciones, categorias_map=categorias_map)
        
        if not Productos.query.get(pro_codigo):
            flash('El producto seleccionado no existe.', 'error')
            productos = Productos.query.all()
            ubicaciones = Ubicaciones.query.all()
            return render_template('inventario/editarinventario.html', inventario=inventario, producto=productos, ubicacion=ubicaciones, categorias_map=categorias_map)

        # Validar existencia de las ubicaciones
        try:
            ubi_codigo = str(ubicacion_codigo)
        except (ValueError, TypeError):
            flash('Ubicación inválida. Por favor, seleccione una ubicación válida.', 'error')
            productos = Productos.query.all()
            ubicaciones = Ubicaciones.query.all()
            return render_template('inventario/editarinventario.html', inventario=inventario, producto=productos, ubicacion=ubicaciones, categorias_map=categorias_map)
        
        if not Ubicaciones.query.get(ubi_codigo):
            flash('La ubicación seleccionada no existe.', 'error')
            productos = Productos.query.all()
            ubicaciones = Ubicaciones.query.all()
            return render_template('inventario/editarinventario.html', inventario=inventario, producto=productos, ubicacion=ubicaciones, categorias_map=categorias_map)
        
        # Validar si la ubicación ya tiene un inventario asignado (y no es el actual)
        inventario_existente = Inventario.query.filter_by(inv_cod_ubicacion=ubi_codigo).first()
        if inventario_existente and inventario_existente.inv_id != inventario.inv_id:
            flash(f'La ubicación con código {ubi_codigo} ya tiene un inventario asignado.', 'error')
            productos = Productos.query.all()
            ubicaciones = Ubicaciones.query.all()
            return render_template('inventario/editarinventario.html', inventario=inventario, producto=productos, ubicacion=ubicaciones, categorias_map=categorias_map)
        
        # Validar que la cantidad o saldo sean enteros no negativos
        try:
            cantidad = int(cantidad)
            saldo = float(saldo)
            if cantidad < 0 or saldo < 0:
                raise ValueError
        except ValueError:
            flash('La cantidad y el saldo deben ser números enteros no negativos.', 'error')
            productos = Productos.query.all()
            ubicaciones = Ubicaciones.query.all()
            return render_template('inventario/editarinventario.html', inventario=inventario, producto=productos, ubicacion=ubicaciones, categorias_map=categorias_map)
        
        # Validar que la cantidad de inventario no supere la capacidad de la ubicación
        u_cantidad = Ubicaciones.query.get(ubi_codigo)
        if cantidad > u_cantidad.ubi_capacidad:
            flash(f'La cantidad de inventario ({cantidad}) supera la capacidad de la ubicación {ubi_codigo} ({u_cantidad.ubi_capacidad}).', 'error')
            productos = Productos.query.all()
            ubicaciones = Ubicaciones.query.all()
            return render_template('inventario/editarinventario.html', inventario=inventario, producto=productos, ubicacion=ubicaciones, categorias_map=categorias_map)
        
        # Validar que la categoría del producto coincida con la categoría de la ubicación
        producto = Productos.query.get(pro_codigo)
        ubicacion = Ubicaciones.query.get(ubi_codigo)
        if producto.pro_cat_id != ubicacion.ubi_cat_id:
            flash('La categoría del producto no coincide con la categoría de la ubicación.', 'error')
            productos = Productos.query.all()
            ubicaciones = Ubicaciones.query.all()
            return render_template('inventario/editarinventario.html', inventario=inventario, producto=productos, ubicacion=ubicaciones, categorias_map=categorias_map)
        
        # Fecha de actualización
        tz_colombia = 'America/Bogota'
        fecha = datetime.now(ZoneInfo(tz_colombia))

        # Actualizar los datos del inventario
        inventario.inv_pro_codigo = pro_codigo
        inventario.inv_cod_ubicacion = ubi_codigo
        inventario.inv_cantidad = cantidad
        inventario.inv_saldo = saldo
        inventario.inv_fecha_actualizacion = fecha

        db.session.commit()
        flash('Inventario actualizado exitosamente.', 'success')
        return redirect(url_for('inventario.lista_inventario'))
    
    return render_template('inventario/editarinventario.html', inventario=inventario, producto=productos, ubicacion=ubicaciones, categorias_map=categorias_map)

@bp.route('/borrar/<int:id>', methods=('GET', 'POST'))
@login_required
def borrar_inventario(id):
    inventario = Inventario.query.get_or_404(id)
    if not inventario:
        flash(f'El inventario con ID {id} no existe.', 'error')
    else:
        db.session.delete(inventario)
        db.session.commit()
        flash('Inventario borrado exitosamente.', 'success')
    return redirect(url_for('inventario.lista_inventario'))

@bp.route('/exportar')
@login_required
def exportar_inventario_excel():
    # Hacer join con las tablas de productos y ubicaciones para obtener los nombres
    inventarios = (
        db.session.query(
            Inventario.inv_id,
            Inventario.inv_pro_codigo,
            Productos.pro_nombre.label('producto_nombre'),
            Inventario.inv_cod_ubicacion,
            Inventario.inv_cantidad,
            Inventario.inv_saldo,
            Inventario.inv_fecha_actualizacion
        )
        .outerjoin(Productos, Inventario.inv_pro_codigo == Productos.pro_codigo)
    )

    # Convertir resultados a una lista de diccionarios
    data = [
        {
            'ID de Inventario': inv.inv_id,
            'Código de producto': inv.inv_pro_codigo,
            'Nombre de producto': inv.producto_nombre,
            'Código de ubicación': inv.inv_cod_ubicacion,
            'Cantidad': inv.inv_cantidad,
            'Saldo': inv.inv_saldo,
            'Fecha de actualización': inv.inv_fecha_actualizacion
        }
        for inv in inventarios
    ]

    columnas = ['ID de Inventario', 'Código de producto', 'Nombre de producto', 'Código de ubicación', 'Cantidad', 'Saldo', 'Fecha de actualización']

    return exportar_a_excel('inventario', columnas, data)
