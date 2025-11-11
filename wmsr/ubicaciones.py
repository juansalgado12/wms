from flask import Blueprint, render_template, request, flash, redirect, url_for
from wmsr.utils.export_excel import exportar_a_excel

from .auth import login_required # Importar el decorador de login requerido si es necesario
from .models import Ubicaciones, Categorias # Importar el modelo de Inventario y Ubicaciones
from . import db # Importar la base de datos

bp = Blueprint('ubicaciones', __name__, url_prefix='/ubicaciones')

@bp.route('/')
def lista_ubicaciones():
    return render_template('inventario/ubicaciones/listaubicaciones.html')

@bp.route('/crear')
def crear_ubicacion():
    return render_template('inventario/ubicaciones/crearubicaciones.html')

@bp.route('/editar')
def editar_ubicacion():
    return render_template('inventario/ubicaciones/editarubicaciones.html')