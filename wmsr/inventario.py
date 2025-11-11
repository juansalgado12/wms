from flask import Blueprint, render_template, request, flash, redirect, url_for
from wmsr.utils.export_excel import exportar_a_excel

from .auth import login_required # Importar el decorador de login requerido si es necesario
from .models import Inventario, Ubicaciones # Importar el modelo de Inventario y Ubicaciones
from . import db # Importar la base de datos

bp = Blueprint('inventario', __name__, url_prefix='/inventario')

# Ruta para la lista de inventario
@bp.route('/')
@login_required
def lista_inventario():
    return render_template('inventario/listainventario.html')

@bp.route('/crear', methods=('GET', 'POST'))
@login_required
def crear_inventario():
    return render_template('inventario/crearinventario.html')

@bp.route('/editar/<int:id>', methods=('GET', 'POST'))
@login_required
def editar_inventario(id):
    return render_template('inventario/editarinventario.html')