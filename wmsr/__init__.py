from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Inicializar la base de datos
db = SQLAlchemy()

def create_app():
    #crear la app
    app = Flask(__name__)
    #llamamos la configuracion de config.py
    app.config.from_object('config.Config')
    #inicializar la base de datos con la app
    db.init_app(app)

    #Registrar vistas (blueprints)
    from wmsr import home, auth, productos, ubicaciones, categorias, unidad, marca, presentacion, documento_recibo, proveedores, inventario
    app.register_blueprint(home.bp) #vista de home
    app.register_blueprint(auth.bp) #vista de auth
    app.register_blueprint(productos.bp) #vista de productos
    app.register_blueprint(ubicaciones.bp) #vista de ubicaciones
    app.register_blueprint(categorias.bp) #vista de categorias
    app.register_blueprint(documento_recibo.bp) #vista de document_recibo
    app.register_blueprint(unidad.bp) #vista de unidad
    app.register_blueprint(marca.bp) #vista de marca
    app.register_blueprint(presentacion.bp) #vista de presentacion
    app.register_blueprint(proveedores.bp) #vista de proveedores
    app.register_blueprint(inventario.bp) #vista de inventario

    #Crear las tablas en la base de datos
    from .models import Categorias, Presentacion, Unidad, Marca, Usuarios, Proveedor, Productos, ProductoImagenes, Ubicaciones, DocumentoRecibo, Inventario, Movimientos
    with app.app_context():
        db.create_all()

    return app