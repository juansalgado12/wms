from flask import Blueprint, render_template, request, redirect, url_for, flash, g

from .auth import login_required
from .models import Movimientos, Inventario, Productos, DocumentoRecibo, Ubicaciones, Usuarios
from . import db
from wmsr.utils.export_excel import exportar_a_excel
from datetime import datetime
from zoneinfo import ZoneInfo

bp = Blueprint('movimientos', __name__, url_prefix='/movimientos')

@bp.route('/')
@login_required
def lista_movimientos():
    # # Listar todos los movimientos registrados
    # movimientos = Movimientos.query.all()
    # productos = Productos.query.all()
    # usuarios = Usuarios.query.all()

    # # Mapear nombre de producto y usuario responsable
    # productos_map = {p.pro_codigo: p.pro_nombre for p in productos}
    # usuarios_map = {u.usu_id: u.usu_nombre for u in usuarios}

    return render_template('movimientos/listamovimientos.html')

@bp.route('/realizar_movimiento', methods=('GET', 'POST'))
@login_required
def realizar_movimiento():

    if request.method == 'POST':
        producto_id = request.form.get('producto')
        cantidad = request.form.get('cantidad')
        documento_id = request.form.get('documento')
        tipo_movimiento = request.form.get('tipo')
        destino = request.form.get('destino')
        inventario_id = request.form.get('inventario')
        observaciones = request.form.get ('observaciones')
    
        # Validar campos obligatorios
        if not producto_id or not cantidad or not tipo_movimiento or not inventario_id:
            flash('Por favor, complete todos los campos obligatorios.', 'error')
            productos = Productos.query.all()
            documentos = DocumentoRecibo.query.all()
            inventarios = Inventario.query.all()
            return render_template('movimientos/realizarmovimientos.html', productos=productos, documentos=documentos, inventarios=inventarios)
        
        # Validar existencia de las claves foraneas
        try:
            pro_codigo = str(producto_id)
            doc_codigo = str(documento_id)
            inv_id = int(inventario_id)
        except (ValueError, TypeError):
            flash('Seleccione opciones válidas para producto, documento e inventario.', 'error')
            productos = Productos.query.all()
            documentos = DocumentoRecibo.query.all()
            inventarios = Inventario.query.all()
            return redirect(url_for('movimientos.realizar_movimiento', productos=productos, documentos=documentos, inventarios=inventarios))
        
        if not Productos.query.get(pro_codigo) or not DocumentoRecibo.query.get(doc_codigo) or not Inventario.query.get(inv_id):
            flash('Algunas de las opciones seleccionadas no existen.', 'error')
            productos = Productos.query.all()
            documentos = DocumentoRecibo.query.all()
            inventarios = Inventario.query.all()
            return render_template('movimientos/realizarmovimiento.html', productos=productos, documentos=documentos, inventarios=inventarios)
        
        #Validar que la cantidad exista, sea positiva, sea entero y no decimal.
        try:
            cantidad = int(cantidad)
            if cantidad <= 0:
                raise ValueError
        except ValueError:
            flash ('La cantidad debe ser un número entero positivo.', 'error')
            productos = Productos.query.all()
            documentos = DocumentoRecibo.query.all()
            inventarios = Inventario.query.all()
            return render_template('movimientos/realizarmovimiento.html', productos=productos, documentos=documentos, inventarios=inventarios)
        
        
        # Validar tipo de movimiento
        if tipo_movimiento not in ['INGRESO', 'SALIDA']:
            flash('Tipo de movimiento inválido.', 'error')
            productos = Productos.query.all()
            documentos = DocumentoRecibo.query.all()
            inventarios = Inventario.query.all()
            return render_template('movimientos/realizarmovimiento.html', productos=productos, documentos=documentos, inventarios=inventarios)
        
        # Validar que la cantidad no exceda el limite 
        
        # Obtener la fecha y hora actual en zona horaria de Colombia
        tz_colombia = ZoneInfo('America/Bogota')
        fecha = datetime.now(tz_colombia)

        # obtener el id del usuario logueado con g.user
        usuario_id = g.user.usu_id

        # Obtener inventario y ubicación relacionadas para validar capacidad
        inventario_obj = Inventario.query.get(inv_id)
        ubicacion_obj = None
        if inventario_obj:
            ubicacion_obj = Ubicaciones.query.get(inventario_obj.inv_cod_ubicacion)

        # Validaciones de capacidad y saldo
        if tipo_movimiento == 'INGRESO':
            if ubicacion_obj and ubicacion_obj.ubi_capacidad is not None:
                if (inventario_obj.inv_cantidad + cantidad) > ubicacion_obj.ubi_capacidad:
                    flash(f'Capacidad excedida: la ubicación {ubicacion_obj.ubi_codigo} tiene capacidad {ubicacion_obj.ubi_capacidad} y contiene {inventario_obj.inv_cantidad}.', 'error')
                    productos = Productos.query.all()
                    documentos = DocumentoRecibo.query.all()
                    inventarios = Inventario.query.all()
                    return render_template('movimientos/realizarmovimiento.html', productos=productos, documentos=documentos, inventarios=inventarios)
        else:  # SALIDA
            if inventario_obj.inv_cantidad - cantidad < 0:
                flash(f'Cantidad insuficiente en inventario. Saldo actual: {inventario_obj.inv_cantidad}.', 'error')
                productos = Productos.query.all()
                documentos = DocumentoRecibo.query.all()
                inventarios = Inventario.query.all()
                return render_template('movimientos/realizarmovimiento.html', productos=productos, documentos=documentos, inventarios=inventarios)
            
        # Crear el nuevo movimiento y actualizar inventario
        movimiento = Movimientos(
            mov_pro_codigo=pro_codigo,
            mov_inv_id=inv_id,
            mov_cantidad=cantidad,
            mov_doc_id=doc_codigo,
            mov_tipo=tipo_movimiento,
            mov_destino=destino,
            mov_usu_id=usuario_id,
            mov_observacion=observaciones
        )
        # El modelo Movimientos no acepta mov_fecha en el constructor personalizado,
        # asignarlo como atributo después de crear la instancia.
        movimiento.mov_fecha = fecha

        # Actualizar inventario según tipo
        if tipo_movimiento == 'INGRESO':
            inventario_obj.inv_cantidad = inventario_obj.inv_cantidad + cantidad
            inventario_obj.inv_saldo = (inventario_obj.inv_saldo or 0) + cantidad
        else:
            inventario_obj.inv_cantidad = inventario_obj.inv_cantidad - cantidad
            inventario_obj.inv_saldo = (inventario_obj.inv_saldo or 0) - cantidad

        db.session.add(movimiento)
        db.session.add(inventario_obj)
        db.session.commit()

        # 
        flash('Movimiento realizado exitosamente.', 'success')
        return redirect(url_for('movimientos.realizar_movimiento'))

    return render_template('movimientos/realizarmovimientos.html', productos = Productos.query.all(), documentos=DocumentoRecibo.query.all(), inventarios=Inventario.query.all())

@bp.route('/editar/<int:id>', methods=('GET', 'POST'))
@login_required
def editar_movimiento(id):
    return render_template('movimientos/editarmovimientos.html')

@bp.route('/borrar/<int:id>', methods=('GET', 'POST'))
@login_required
def borrar_movimiento(id):
    return 'Borrar movimiento - En construcción'

@bp.route('/exportar', methods=('GET', 'POST'))
@login_required
def exportar_movimientos_excel():
    return 'Exportar movimientos a Excel - En construcción'
