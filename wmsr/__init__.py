from flask import Flask

def create_app():
    #crear la app
    app = Flask(__name__)
    #llamamos la configuracion de config.py
    app.config.from_object('config.Config')

    #Registrar vistas (blueprints)
    from wmsr import home, auth, productos, ubicaciones
    app.register_blueprint(home.bp) #vista de home
    app.register_blueprint(auth.bp) #vista de auth
    app.register_blueprint(productos.bp) #vista de productos
    app.register_blueprint(ubicaciones.bp) #vista de ubicaciones


    

    return app