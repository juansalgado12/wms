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
    # Obtener todos los movimientos de la base de datos
    q = (request.args.get('q') or '').strip()
    # Obtener movimientos y datos relacionados
    movimientos = Movimientos.query.all()
    productos = Productos.query.all()
    usuarios = Usuarios.query.all()
    ubicaciones = Ubicaciones.query.all()
    inventarios = Inventario.query.all()

    if q:
        # Filtrar movimientos por producto, codigo de ubicación, usuario o tipo de movimiento
        movimientos = (
            db.session.query(Movimientos)
            .join(Productos, Movimientos.mov_pro_codigo == Productos.pro_codigo)
            .join(Usuarios, Movimientos.mov_usu_id == Usuarios.usu_id)
            .join(Inventario, Movimientos.mov_inv_id == Inventario.inv_id)
            .join(Ubicaciones, Inventario.inv_cod_ubicacion == Ubicaciones.ubi_codigo)
            .filter(
                (Productos.pro_nombre.ilike(f'%{q}%')) |
                (Usuarios.usu_nombre.ilike(f'%{q}%')) |
                (DocumentoRecibo.doc_id.ilike(f'%{q}%')) |
                (Movimientos.mov_tipo.ilike(f'%{q}%')) |
                (Inventario.inv_cod_ubicacion.ilike(f'%{q}%')) |
                (Ubicaciones.ubi_codigo.ilike(f'%{q}%'))
            )
            .all()
        )
    else:
        movimientos = Movimientos.query.all()

    # Mapear nombre de producto, usuario responsable
    productos_map = {p.pro_codigo: p.pro_nombre for p in productos}

    usuarios_map = {u.usu_id: u.usu_nombre for u in usuarios}

    inv_to_ubi = {inv.inv_id: inv.inv_cod_ubicacion for inv in inventarios}

    ubicaciones_map = {u.ubi_codigo: u.ubi_codigo for u in ubicaciones}

    return render_template('movimientos/listamovimientos.html', movimientos=movimientos, productos_map=productos_map, inv_to_ubi=inv_to_ubi, ubicaciones_map=ubicaciones_map, usuarios_map=usuarios_map, q=q)

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
            return redirect(url_for('movimientos.realizar_movimientos', productos=productos, documentos=documentos, inventarios=inventarios))
        
        if not Productos.query.get(pro_codigo) or not DocumentoRecibo.query.get(doc_codigo) or not Inventario.query.get(inv_id):
            flash('Algunas de las opciones seleccionadas no existen.', 'error')
            productos = Productos.query.all()
            documentos = DocumentoRecibo.query.all()
            inventarios = Inventario.query.all()
            return render_template('movimientos/realizarmovimientos.html', productos=productos, documentos=documentos, inventarios=inventarios)
        
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
            return render_template('movimientos/realizarmovimientos.html', productos=productos, documentos=documentos, inventarios=inventarios)
        
        
        # Validar tipo de movimiento
        if tipo_movimiento not in ['INGRESO', 'SALIDA']:
            flash('Tipo de movimiento inválido.', 'error')
            productos = Productos.query.all()
            documentos = DocumentoRecibo.query.all()
            inventarios = Inventario.query.all()
            return render_template('movimientos/realizarmovimientos.html', productos=productos, documentos=documentos, inventarios=inventarios)
        
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

        # Validar que el producto del movimiento coincida con el del inventario
        # Normalizar tipos a str() para evitar discrepancias entre int/str en la comparación.
        if not inventario_obj or str(inventario_obj.inv_pro_codigo) != str(pro_codigo):
            flash('El producto seleccionado no coincide con el del inventario.', 'error')
            productos = Productos.query.all()
            documentos = DocumentoRecibo.query.all()
            inventarios = Inventario.query.all()
            return render_template('movimientos/realizarmovimientos.html', productos=productos, documentos=documentos, inventarios=inventarios)
        

        # Validaciones de capacidad y saldo
        if tipo_movimiento == 'INGRESO':
            if ubicacion_obj and ubicacion_obj.ubi_capacidad is not None:
                if (inventario_obj.inv_cantidad + cantidad) > ubicacion_obj.ubi_capacidad:
                    flash(f'Capacidad excedida: la ubicación {ubicacion_obj.ubi_codigo} tiene capacidad {ubicacion_obj.ubi_capacidad} y contiene {inventario_obj.inv_cantidad}.', 'error')
                    productos = Productos.query.all()
                    documentos = DocumentoRecibo.query.all()
                    inventarios = Inventario.query.all()
                    return render_template('movimientos/realizarmovimientos.html', productos=productos, documentos=documentos, inventarios=inventarios)
        else:  # SALIDA
            if inventario_obj.inv_cantidad - cantidad < 0:
                flash(f'Cantidad insuficiente en inventario. Saldo actual: {inventario_obj.inv_cantidad}.', 'error')
                productos = Productos.query.all()
                documentos = DocumentoRecibo.query.all()
                inventarios = Inventario.query.all()
                return render_template('movimientos/realizarmovimientos.html', productos=productos, documentos=documentos, inventarios=inventarios)
            
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

        flash('Movimiento realizado exitosamente.', 'success')
        return redirect(url_for('movimientos.realizar_movimiento'))

    return render_template('movimientos/realizarmovimientos.html', productos = Productos.query.all(), documentos=DocumentoRecibo.query.all(), inventarios=Inventario.query.all())

@bp.route('/editar/<int:mov_id>', methods=('GET', 'POST'))
@login_required
def editar_movimiento(mov_id):
    movimiento = Movimientos.query.get(mov_id)
    if not movimiento:
        flash('Movimiento no encontrado.', 'error')
        return redirect(url_for('movimientos.lista_movimientos'))

    if request.method == 'POST':
        producto = request.form.get('producto')
        cantidad = request.form.get('cantidad')
        documento = request.form.get('documento')
        tipo = request.form.get('tipo')
        destino = request.form.get('destino')
        inventario = request.form.get('inventario')
        observaciones = request.form.get('observaciones')

        # Validar campos obligatorios
        if not producto or not cantidad or not tipo or not inventario:
            flash('Por favor, complete todos los campos obligatorios.', 'error')
            return render_template('movimientos/editarmovimientos.html', movimiento=movimiento, productos=Productos.query.all(), documentos=DocumentoRecibo.query.all(), inventarios=Inventario.query.all())

        # Validar cantidad
        try:
            new_cantidad = int(cantidad)
            if new_cantidad <= 0:
                raise ValueError
        except ValueError:
            flash('La cantidad debe ser un número entero positivo.', 'error')
            return render_template('movimientos/editarmovimientos.html', movimiento=movimiento, productos=Productos.query.all(), documentos=DocumentoRecibo.query.all(), inventarios=Inventario.query.all())

        # Validar existencia
        try:
            new_inv_id = int(inventario)
        except (TypeError, ValueError):
            flash('Inventario inválido.', 'error')
            return render_template('movimientos/editarmovimientos.html', movimiento=movimiento, productos=Productos.query.all(), documentos=DocumentoRecibo.query.all(), inventarios=Inventario.query.all())

        if not Productos.query.get(str(producto)) or not DocumentoRecibo.query.get(str(documento)) or not Inventario.query.get(new_inv_id):
            flash('Seleccione opciones válidas para producto, documento e inventario.', 'error')
            return render_template('movimientos/editarmovimientos.html', movimiento=movimiento, productos=Productos.query.all(), documentos=DocumentoRecibo.query.all(), inventarios=Inventario.query.all())

        # Cargar inventarios involucrados
        old_inv = Inventario.query.get(movimiento.mov_inv_id) if movimiento.mov_inv_id else None
        new_inv = Inventario.query.get(new_inv_id)

        # Verificar que el producto seleccionado corresponde al inventario destino
        if new_inv.inv_pro_codigo and str(new_inv.inv_pro_codigo) != str(producto):
            flash('El producto seleccionado no coincide con el del inventario destino.', 'error')
            return render_template('movimientos/editarmovimientos.html', movimiento=movimiento, productos=Productos.query.all(), documentos=DocumentoRecibo.query.all(), inventarios=Inventario.query.all())

        # Función para calcular efecto (positivo para ingreso, negativo para salida)
        def efecto(tipo_mov, qty):
            return qty if tipo_mov == 'INGRESO' else -qty

        old_effect = efecto(movimiento.mov_tipo, movimiento.mov_cantidad)
        new_effect = efecto(tipo, new_cantidad)

        # Si no cambia el inventario y el efecto es igual, evitar modificar cantidades
        if movimiento.mov_inv_id == new_inv_id and old_effect == new_effect:
            # Actualizar solo campos informativos
            movimiento.mov_pro_codigo = str(producto)
            movimiento.mov_doc_id = str(documento)
            movimiento.mov_destino = destino
            movimiento.mov_observacion = observaciones
            movimiento.mov_tipo = tipo
            movimiento.mov_cantidad = new_cantidad
            movimiento.mov_fecha = datetime.now(ZoneInfo('America/Bogota'))
            db.session.add(movimiento)
            db.session.commit()
            flash('Movimiento actualizado (sin cambios en inventario).', 'success')
            return redirect(url_for('movimientos.lista_movimientos'))

        # Si el inventario es el mismo pero el efecto cambia, aplicar delta
        if old_inv and old_inv.inv_id == new_inv_id:
            delta = new_effect - old_effect
            resultado = old_inv.inv_cantidad + delta
            # Validaciones
            if resultado < 0:
                flash(f'Operación inválida: inventario resultaría negativo ({resultado}).', 'error')
                return render_template('movimientos/editarmovimientos.html', movimiento=movimiento, productos=Productos.query.all(), documentos=DocumentoRecibo.query.all(), inventarios=Inventario.query.all())
            ubic = Ubicaciones.query.get(old_inv.inv_cod_ubicacion)
            if ubic and ubic.ubi_capacidad is not None and resultado > ubic.ubi_capacidad:
                flash(f'Capacidad excedida en la ubicación ({ubic.ubi_capacidad}).', 'error')
                return render_template('movimientos/editarmovimientos.html', movimiento=movimiento, productos=Productos.query.all(), documentos=DocumentoRecibo.query.all(), inventarios=Inventario.query.all())

            old_inv.inv_cantidad = resultado
            old_inv.inv_saldo = (old_inv.inv_saldo or 0) + (new_effect - old_effect)
            # Actualizar movimiento
            movimiento.mov_pro_codigo = str(producto)
            movimiento.mov_doc_id = str(documento)
            movimiento.mov_destino = destino
            movimiento.mov_observacion = observaciones
            movimiento.mov_tipo = tipo
            movimiento.mov_cantidad = new_cantidad
            movimiento.mov_fecha = datetime.now(ZoneInfo('America/Bogota'))
            db.session.add(old_inv)
            db.session.add(movimiento)
            db.session.commit()
            flash('Movimiento actualizado correctamente.', 'success')
            return redirect(url_for('movimientos.lista_movimientos'))

        # Si cambia de inventario: revertir efecto antiguo en old_inv (si existe) y aplicar new_effect en new_inv
        if old_inv:
            reverted = old_inv.inv_cantidad - old_effect
            if reverted < 0:
                flash('No es posible revertir el movimiento en el inventario original (quedaría negativo).', 'error')
                return render_template('movimientos/editarmovimientos.html', movimiento=movimiento, productos=Productos.query.all(), documentos=DocumentoRecibo.query.all(), inventarios=Inventario.query.all())
            old_inv.inv_cantidad = reverted
            old_inv.inv_saldo = (old_inv.inv_saldo or 0) - old_effect

        # Aplicar en new_inv
        applied = new_inv.inv_cantidad + new_effect
        new_ubi = Ubicaciones.query.get(new_inv.inv_cod_ubicacion)
        if applied < 0:
            flash('No es posible aplicar el nuevo movimiento en el inventario destino (quedaría negativo).', 'error')
            return render_template('movimientos/editarmovimientos.html', movimiento=movimiento, productos=Productos.query.all(), documentos=DocumentoRecibo.query.all(), inventarios=Inventario.query.all())
        if new_ubi and new_ubi.ubi_capacidad is not None and applied > new_ubi.ubi_capacidad:
            flash('Capacidad excedida en la ubicación destino.', 'error')
            return render_template('movimientos/editarmovimientos.html', movimiento=movimiento, productos=Productos.query.all(), documentos=DocumentoRecibo.query.all(), inventarios=Inventario.query.all())

        new_inv.inv_cantidad = applied
        new_inv.inv_saldo = (new_inv.inv_saldo or 0) + new_effect

        # Actualizar movimiento
        movimiento.mov_pro_codigo = str(producto)
        movimiento.mov_doc_id = str(documento)
        movimiento.mov_destino = destino
        movimiento.mov_observacion = observaciones
        movimiento.mov_tipo = tipo
        movimiento.mov_cantidad = new_cantidad
        movimiento.mov_inv_id = new_inv_id
        movimiento.mov_fecha = datetime.now(ZoneInfo('America/Bogota'))

        if old_inv:
            db.session.add(old_inv)
        db.session.add(new_inv)
        db.session.add(movimiento)
        db.session.commit()
        flash('Movimiento actualizado correctamente (inventarios ajustados).', 'success')
        return redirect(url_for('movimientos.lista_movimientos'))

    # GET
    return render_template('movimientos/editarmovimientos.html', movimiento=movimiento, productos=Productos.query.all(), documentos=DocumentoRecibo.query.all(), inventarios=Inventario.query.all())

@bp.route('/borrar/<int:id>', methods=('GET', 'POST'))
@login_required
def borrar_movimiento(id):
    movimiento = Movimientos.query.get_or_404(id)
    if not movimiento:
        flash(f'El movimiento con ID {id} no existe.', 'error')
    else:
        db.session.delete(movimiento)
        db.session.commit()
        flash(f'Movimiento {id} eliminado correctamente.', 'success')
    return redirect(url_for('movimientos.lista_movimientos'))

@bp.route('/exportar', methods=('GET', 'POST'))
@login_required
def exportar_movimientos_excel():
    # Hacer join con tablas relacionadas para obtener nombres y códigos
    movimientos = (
        db.session.query(
            Movimientos.mov_id,
            Movimientos.mov_inv_id,
            Movimientos.mov_pro_codigo,
            Productos.pro_nombre.label('Nombre_producto'),
            Inventario.inv_cod_ubicacion.label('Codigo_ubicacion'),
            Movimientos.mov_cantidad,
            Movimientos.mov_doc_id,
            Movimientos.mov_tipo,
            Movimientos.mov_destino,
            Usuarios.usu_nombre.label('Usuario_responsable'),
            Movimientos.mov_fecha,
            Movimientos.mov_observacion
        )
        .join(Productos, Movimientos.mov_pro_codigo == Productos.pro_codigo)
        .join(Inventario, Movimientos.mov_inv_id == Inventario.inv_id)
        .join(DocumentoRecibo, Movimientos.mov_doc_id == DocumentoRecibo.doc_id)
        .join(Usuarios, Movimientos.mov_usu_id == Usuarios.usu_id)
    )

    # Convertir resultados a lista de diccionarios
    data = [
        {
            'ID Movimiento': m.mov_id,
            'Código Producto': m.mov_pro_codigo,
            'Nombre Producto': m.Nombre_producto or '',
            'ID Inventario': m.mov_inv_id,
            'Código Ubicación': m.Codigo_ubicacion or '',
            'Cantidad': m.mov_cantidad,
            'Documento ID': m.mov_doc_id,
            'Tipo Movimiento': m.mov_tipo,
            'Destino': m.mov_destino,
            'Usuario Responsable': m.Usuario_responsable or '',
            'Fecha': m.mov_fecha,
            'Observación': m.mov_observacion
        }
        for m in movimientos
    ]

    columnas = ['ID Movimiento', 'Código Producto', 'Nombre Producto', 'ID Inventario', 'Código Ubicación', 'Cantidad', 'Documento ID', 'Tipo Movimiento', 'Destino', 'Usuario Responsable', 'Fecha', 'Observación']

    return exportar_a_excel('movimientos', columnas, data)
