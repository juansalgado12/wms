from flask import Blueprint, render_template, request
from .models import Productos, Inventario, Ubicaciones, Movimientos, Usuarios
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

    cutoff = datetime.now() - timedelta(days=7)
    total_7d = Movimientos.query.filter(Movimientos.mov_fecha >= cutoff).count()
    ingresos_7d = Movimientos.query.filter(Movimientos.mov_tipo == 'INGRESO', Movimientos.mov_fecha >= cutoff).count()
    salidas_7d = Movimientos.query.filter(Movimientos.mov_tipo == 'SALIDA', Movimientos.mov_fecha >= cutoff).count()

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
        rows=rows,
        q=q,
        ubi=ubi
    )
