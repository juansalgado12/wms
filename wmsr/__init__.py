from flask import Flask

def create_app():
    #crear la app
    app = Flask(__name__)
    #llamamos la configuracion de config.py
    app.config.from_object('config.Config')

    #Registrar vistas (blueprints)
    from wmsr import home
    app.register_blueprint(home.bp) #vista de home

    

    return app