from flask import Blueprint, render_template, request
from .models import Productos, Inventario, Ubicaciones, Movimientos, Usuarios, ProductoImagenes, DocumentoRecibo, Proveedor
from .auth import login_required
from . import db
from wmsr.utils.export_excel import exportar_a_excel
from datetime import datetime, timedelta

bp = Blueprint('reportes', __name__, url_prefix='/reportes')

@bp.route('/')
@login_required
def reportes():

    # =======================
    # Reporte de movimientos
    # =======================

    #Total de movimientos, total ingresos y total salidas
    total_movimientos = Movimientos.query.count()
    ingresos = Movimientos.query.filter(Movimientos.mov_tipo == 'INGRESO').count()
    salidas = Movimientos.query.filter(Movimientos.mov_tipo == 'SALIDA').count()

    # =======================
    # 5 usuarios con más movimientos
    # =======================
    usuarios_top = (
        db.session.query(
            Usuarios.usu_nombre,
            Usuarios.usu_email,
            db.func.count(Movimientos.mov_id).label('total_movimientos')
        )
        .join(Usuarios, Usuarios.usu_id == Movimientos.mov_usu_id)
        .group_by(Usuarios.usu_id, Usuarios.usu_nombre, Usuarios.usu_email)
        .order_by(db.func.count(Movimientos.mov_id).desc())
        .limit(5)
        .all()
    )

    # =======================
    # Movimientos ultimos 7 dias
    # =======================

    cutoff_7 = datetime.now() - timedelta(days=7)
    total_7d = Movimientos.query.filter(Movimientos.mov_fecha >= cutoff_7).count()
    ingresos_7d = Movimientos.query.filter(Movimientos.mov_tipo == 'INGRESO', Movimientos.mov_fecha >= cutoff_7).count()
    salidas_7d = Movimientos.query.filter(Movimientos.mov_tipo == 'SALIDA', Movimientos.mov_fecha >= cutoff_7).count()

    #========================
    # Movimientos ultimos 30 dias
    #========================

    cutoff_30 = datetime.now() - timedelta (days=30)
    total_30d = Movimientos.query.filter(Movimientos.mov_fecha >= cutoff_30).count()
    ingresos_30d = Movimientos.query.filter(Movimientos.mov_tipo == 'INGRESO', Movimientos.mov_fecha >= cutoff_30).count()
    salidas_30d = Movimientos.query.filter(Movimientos.mov_tipo == 'SALIDA', Movimientos.mov_fecha >= cutoff_30).count()

     #========================
    # Productos en relacion a movimientos
    #========================

    productos = Productos.query.order_by(Productos.pro_nombre).all()
    producto_seleccionado = (request.args.get('producto') or '').strip() or None

    stats_productos = None
    if producto_seleccionado:
        # totales de movimientos por tipo para el producto seleccionado
        total_prod = Movimientos.query.filter(Movimientos.mov_pro_codigo == producto_seleccionado).count()
        ingresos_prod = Movimientos.query.filter(Movimientos.mov_pro_codigo == producto_seleccionado, Movimientos.mov_tipo == 'INGRESO').count()
        salidas_prod = Movimientos.query.filter(Movimientos.mov_pro_codigo == producto_seleccionado, Movimientos.mov_tipo == 'SALIDA').count()

        # movimientos en productos ultimos 7 dias
        pro_cutoff_7 = datetime.now() - timedelta(days=7)
        total_7d_prod = Movimientos.query.filter(Movimientos.mov_pro_codigo == producto_seleccionado, Movimientos.mov_fecha >= pro_cutoff_7).count()

        ingresos_7d_prod = Movimientos.query.filter(Movimientos.mov_pro_codigo == producto_seleccionado, Movimientos.mov_tipo == 'INGRESO', Movimientos.mov_fecha >= pro_cutoff_7).count()

        salidas_7d_prod = Movimientos.query.filter(Movimientos.mov_pro_codigo == producto_seleccionado, Movimientos.mov_tipo == 'SALIDA', Movimientos.mov_fecha >= pro_cutoff_7).count()

        # Movimientos en productos ultimos 30 dias
        pro_cutoff_30 = datetime.now() - timedelta(days=30)
        total_30d_prod = Movimientos.query.filter(Movimientos.mov_pro_codigo == producto_seleccionado, Movimientos.mov_fecha >= pro_cutoff_30).count()

        ingresos_30d_prod = Movimientos.query.filter(Movimientos.mov_pro_codigo == producto_seleccionado, Movimientos.mov_tipo == 'INGRESO', Movimientos.mov_fecha >= pro_cutoff_30).count()

        salidas_30d_prod = Movimientos.query.filter(Movimientos.mov_pro_codigo == producto_seleccionado, Movimientos.mov_tipo == 'SALIDA', Movimientos.mov_fecha >= pro_cutoff_30).count()

        # stock actual del producto seleccionado
        stock_actual = db.session.query(
            db.func.sum(Inventario.inv_cantidad)
        ).filter(Inventario.inv_pro_codigo == producto_seleccionado).scalar() or 0

        # Imagen del producto seleccionado
        img = ProductoImagenes.query.filter(ProductoImagenes.img_pro_codigo == producto_seleccionado).order_by(getattr(ProductoImagenes, 'img_id').desc()).first()
        if img and getattr(img, 'img_url', None):
            producto_imagen_url = img.img_url
        else:
            producto_imagen_url = None
        

        stats_productos = {
            'total': total_prod,
            'ingresos': ingresos_prod,
            'salidas': salidas_prod,
            'total_7d': total_7d_prod,
            'ingresos_7d': ingresos_7d_prod,
            'salidas_7d': salidas_7d_prod,
            'total_30d': total_30d_prod,
            'ingresos_30d': ingresos_30d_prod,
            'salidas_30d': salidas_30d_prod,
            'stock_actual': stock_actual,
            'imagen_url': producto_imagen_url
        }
    
    # =======================
    # Proveedores (selector)
    # =======================

    proveedores = Proveedor.query.order_by(Proveedor.prov_razon_social).all()
    proveedor_seleccionado = (request.args.get('proveedor') or '').strip() or None
    prov_stats = None
    if proveedor_seleccionado:
        # normalizar id si es numerico
        try:
            prov_id = int(proveedor_seleccionado)
        except Exception:
            prov_id = proveedor_seleccionado
        
        # total movimientos tipos ingresos asociados al proveedor
        
        ingresos_prov = db.session.query(db.func.count(Movimientos.mov_id))\
            .join(DocumentoRecibo, DocumentoRecibo.doc_id == Movimientos.mov_doc_id)\
            .filter(DocumentoRecibo.doc_id_proveedor == prov_id, Movimientos.mov_tipo == 'INGRESO').scalar() or 0
    
        # ingresos ultimos 7 dias
        prov_cutoff_7 = datetime.now() - timedelta(days=7)
        ingresos_7d_prov = db.session.query(db.func.count(Movimientos.mov_id))\
            .join(DocumentoRecibo, DocumentoRecibo.doc_id == Movimientos.mov_doc_id)\
            .filter(DocumentoRecibo.doc_id_proveedor == prov_id, Movimientos.mov_tipo == 'INGRESO', Movimientos.mov_fecha >= prov_cutoff_7).scalar() or 0
        
        # ingresos ultimos 30 dias
        prov_cutoff_30 = datetime.now() - timedelta(days=30)
        ingresos_30d_prov = db.session.query(db.func.count(Movimientos.mov_id))\
            .join(DocumentoRecibo, DocumentoRecibo.doc_id == Movimientos.mov_doc_id)\
            .filter(DocumentoRecibo.doc_id_proveedor == prov_id, Movimientos.mov_tipo == 'INGRESO', Movimientos.mov_fecha >= prov_cutoff_30).scalar() or 0
        
        prov_stats = {
            'ingresos': ingresos_prov,
            'ingresos_7d': ingresos_7d_prov,
            'ingresos_30d': ingresos_30d_prov
        }

    # =======================
    # Reporte de inventario
    # =======================

    q = (request.args.get('q') or '').strip()
    ubi = request.args.get('ubicacion')

    query = (
        db.session.query(
            Productos.pro_codigo,
            Productos.pro_nombre,
            db.func.sum(Inventario.inv_cantidad).label('total_cantidad'),
            db.func.count(Inventario.inv_id).label('cantidad_ubicaciones')
        )
        .join(Inventario, Inventario.inv_pro_codigo == Productos.pro_codigo)
        .group_by(Productos.pro_codigo, Productos.pro_nombre)
    )

    if q:
        query = query.filter(Productos.pro_nombre.ilike(f'%{q}%'))
    if ubi:
        query = query.join(Ubicaciones, Inventario.inv_cod_ubicacion == Ubicaciones.ubi_codigo)\
                     .filter(Ubicaciones.ubi_codigo == ubi)

    rows = query.all()

    # Exportar a Excel
    if request.args.get('exportar') == 'excel':
        data = [
            {
                'Código Producto': r.pro_codigo,
                'Nombre Producto': r.pro_nombre,
                'Cantidad Total': r.total_cantidad,
                'Cantidad de ubicaciones': r.cantidad_ubicaciones
            }
            for r in rows
        ]
        columns = ['Código Producto', 'Nombre Producto', 'Cantidad Total', 'Cantidad de ubicaciones']
        return exportar_a_excel('reporte_inventario', columns, data)

    # =======================
    # Render final con Todo
    # =======================
    return render_template(
        'reports/reportes.html',
        total_movimientos=total_movimientos,
        usuarios_top=usuarios_top,
        ingresos=ingresos,
        salidas=salidas,
        total_7d=total_7d,
        ingresos_7d=ingresos_7d,
        salidas_7d=salidas_7d,
        total_30d=total_30d,
        ingresos_30d=ingresos_30d,
        salidas_30d=salidas_30d,
        productos=productos,
        producto_seleccionado=producto_seleccionado,
        stats_productos=stats_productos,
        proveedores=proveedores,
        proveedor_seleccionado=proveedor_seleccionado,
        prov_stats=prov_stats,
        rows=rows,
        q=q,
        ubi=ubi
    )
