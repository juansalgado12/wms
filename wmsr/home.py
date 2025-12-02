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

    #==================================
    # Consulta para los últimos 30 días
    #==================================
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

    #==================================
    # Consultas y map para ultimos 7 dias
    #==================================
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
    
    #==================================
    # Movimientos en los ultimos 6 meses
    #==================================
    year = today.year
    month = today.month
    months = []
    for i in range(5, -1, -1):
        m = month - i
        y = year
        while m <= 0:
            m += 12
            y -= 1
        months.append((y, m))
    
    labels_6m =[]
    data_6m = []
    for (y, m) in months:
        start = datetime(y, m, 1).date()
        # calcular el primer día del mes siguiente
        if m == 12:
            end = datetime(y + 1, 1, 1).date()
        else:
            end = datetime(y, m + 1, 1).date()
        cnt = db.session.query(db.func.count(Movimientos.mov_id))\
            .filter(Movimientos.mov_fecha >= start, Movimientos.mov_fecha < end)\
            .scalar() or 0
        
        # Etiqueta legible para la gráfica
        labels_6m.append(start.strftime('%b %Y'))  # Ejemplo: 'Jan 2024'
        data_6m.append(int(cnt))
    
    total_6m = sum(data_6m)

    #==================================
    # Movimientos ultimos 12 meses
    #==================================
    labels_12m = []
    data_12m =[]
    # generar los ultimos 12 meses (desde 11 meses atrás hasta el mes actual)
    year = today.year
    month = today.month
    for i in range(11, -1, -1):
        m = month - i
        y = year
        while m <= 0:
            m += 12
            y -= 1
        start = datetime(y, m, 1).date()
        # primer dia del mes siguiente
        if m == 12:
            end = datetime(y + 1, 1, 1).date()
        else:
            end = datetime(y, m + 1, 1).date()
        cnt = db.session.query(db.func.count(Movimientos.mov_id))\
            .filter(Movimientos.mov_fecha >= start, Movimientos.mov_fecha < end)\
            .scalar() or 0
        labels_12m.append(start.strftime('%b %Y'))
        data_12m.append(int(cnt))
    
    total_12m = sum(data_12m)

    stats = {
        'labels_30': labels_30,
        'data_30': data_30,
        'total_30': total_30,
        'labels_7': labels_7,
        'data_7': data_7,
        'total_7': total_7,
        'labels_6m': labels_6m,
        'data_6m': data_6m,
        'total_6m': total_6m,
        'labels_12m': labels_12m,
        'data_12m': data_12m,
        'total_12m': total_12m
    }
    return render_template('dashboard.html', stats=stats)
# ...existing code...