from flask import Blueprint, render_template
from .auth import login_required
from datetime import datetime, timedelta
from .models import Movimientos
from . import db

bp = Blueprint('home', __name__)

# Ruta para la página de bienvenida
@bp.route('/')
def welcome():
    return render_template('welcome.html')

# Ruta para la página del almacén
# ...existing code...
@bp.route('/almacen')
@login_required
def almacen():
    
    today = datetime.now().date()
    # rangos inclusivos: 30 días (hoy y 29 días atrás), 7 días (hoy y 6 días atrás)
    cutoff_30 = today - timedelta(days=29)
    cutoff_7 = today - timedelta(days=6)

    # usamos db.func.date(...) en el filtro para comparar por fecha (sin hora)
    q30 = (
        db.session.query(
            db.func.date(Movimientos.mov_fecha).label('fecha'),
            db.func.count(Movimientos.mov_id).label('total_movimientos')
        )
        .filter(db.func.date(Movimientos.mov_fecha) >= cutoff_30)
        .group_by(db.func.date(Movimientos.mov_fecha))
        .all()
    )

    map30 = {
        (row.fecha.isoformat() if hasattr(row.fecha, 'isoformat') else str(row.fecha)): int(row.total_movimientos)
        for row in q30
    }

    # Movimientos totales ultimos 30 dias
    total_30 = sum(map30.values())

    # Generar lista de fechas y totales para los ultimos 30 dias
    labels_30 = []
    data_30 = []
    for i in range(30):
        d = cutoff_30 + timedelta(days=i)        # d es date
        key = d.isoformat()                       # 'YYYY-MM-DD' — coincide con map30 keys
        labels_30.append(d.strftime('%d/%m'))     # formato legible en la gráfica
        data_30.append(map30.get(key, 0))

    # Consultas y map para ultimos 7 dias
    q7 = (
        db.session.query(
            db.func.date(Movimientos.mov_fecha).label('fecha'),
            db.func.count(Movimientos.mov_id).label('total_movimientos')
        )
        .filter(db.func.date(Movimientos.mov_fecha) >= cutoff_7)
        .group_by(db.func.date(Movimientos.mov_fecha))
        .all()
    )
    
    map7 = {
        (row.fecha.isoformat() if hasattr(row.fecha, 'isoformat') else str(row.fecha)): row.total_movimientos
        for row in q7
    }

    # Movimientos totales ultimos 7 dias
    total_7 = sum(map7.values())

    labels_7 = []
    data_7 = []
    for i in range(7):
        d = cutoff_7 + timedelta(days=i)
        key = d.isoformat()
        labels_7.append(d.strftime('%d/%m'))
        data_7.append(map7.get(key, 0))

    stats = {
        'labels_30': labels_30,
        'data_30': data_30,
        'total_30': total_30,
        'labels_7': labels_7,
        'data_7': data_7,
        'total_7': total_7
    }
    return render_template('dashboard.html', stats=stats)
# ...existing code...