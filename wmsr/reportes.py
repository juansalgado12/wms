from flask import Blueprint, render_template, request, send_file, flash
from .models import Productos, Inventario, Ubicaciones
from .auth import login_required
from . import db
from wmsr.utils.export_excel import exportar_a_excel
from io import BytesIO

bp = Blueprint('reportes', __name__, url_prefix='/reportes')

@bp.route('/inventario')
@login_required
def reporte_inventario():
    # filtros opcionales
    q = (request.args.get('q') or '').strip()
    ubi = request.args.get('ubicacion')

    # Consulta: total por producto
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
        query = query.join(Ubicaciones, Inventario.inv_cod_ubicacion == Ubicaciones.ubi_codigo).filter(Ubicaciones.ubi_codigo == ubi)
    
    rows = query.all()

    # Generar reporte en formato excel
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
        columnas = ['Código Producto', 'Nombre Producto', 'Cantidad Total', 'Cantidad de ubicaciones']
        return exportar_a_excel('reporte_inventario', columnas, data)
    return render_template('reports/reportes.html', rows=rows, q=q, ubi=ubi)