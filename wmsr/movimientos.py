from flask import Blueprint, render_template, request, redirect, url_for

from .auth import login_required
from .models import Movimientos, Inventario, Productos
from . import db
from wmsr.utils.export_excel import exportar_a_excel
from datetime import datetime
from zoneinfo import ZoneInfo

bp = Blueprint('movimientos', __name__, url_prefix='/movimientos')

@bp.route('/')
@login_required
def lista_movimientos():
    return render_template('movimientos/listamovimientos.html')

@bp.route('/realizar_movimiento', methods=('GET', 'POST'))
@login_required
def realizar_movimiento():
    return render_template('movimientos/realizarmovimientos.html')

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
