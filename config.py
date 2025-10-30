mysql = 'mysql+mysqlconnector://root:root@localhost:3306/wms_db' # Reemplaza con tus credenciales y nombre de base de datos

class Config:
    DEBUG = True
    SECRET_KEY = 'dev'
    SQLALCHEMY_DATABASE_URI = mysql
