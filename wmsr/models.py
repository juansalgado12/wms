from wmsr import db # Importar la instancia de la base de datos
from datetime import datetime # Importar datetime para manejar fechas
from sqlalchemy import Enum, ForeignKey, UniqueConstraint # Importar Enum, ForeignKey y UniqueConstraint de SQLAlchemy


####################################
# Modelos de tablas independientes #
####################################


# Modelo para la tabla Categorias
class Categorias(db.Model):
    __tablename__ = 'Categorias'

    cat_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cat_nombre = db.Column(db.String(100), nullable=False, unique=True)
    cat_descripcion = db.Column(db.Text)

    # Constructor
    def __init__(self, cat_nombre, cat_descripcion=None):
        self.cat_nombre = cat_nombre
        self.cat_descripcion = cat_descripcion

    # Representación del objeto
    def __repr__(self):
        return f"<Categoria {self.cat_nombre}>"

# Modelo para la tabla Presentacion
class Presentacion(db.Model):
    __tablename__ = 'Presentacion'

    pres_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pres_nombre = db.Column(db.String(100), nullable=False, unique=True)
    pres_descripcion = db.Column(db.Text)

    # Constructor
    def __init__(self, pres_nombre, pres_descripcion=None):
        self.pres_nombre = pres_nombre
        self.pres_descripcion = pres_descripcion
    
    # Representación del objeto
    def __repr__(self):
        return f"<Presentacion {self.pres_nombre}>"
    
# Modelo para la tabla Unidad
class Unidad(db.Model):
    __tablename__ = 'Unidad'

    uni_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uni_nombre = db.Column(db.String(50), nullable=False, unique=True)
    uni_descripcion = db.Column(db.Text)

    # Constructor
    def __init__(self, uni_nombre, uni_descripcion=None):
        self.uni_nombre = uni_nombre
        self.uni_descripcion = uni_descripcion
    
    # Representación del objeto
    def __repr__(self):
        return f"<Unidad {self.uni_nombre}>"

# Modelo para la tabla Marca
class Marca(db.Model):
    __tablename__ = 'Marca'

    mar_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    mar_nombre = db.Column(db.String(100), nullable=False, unique=True)
    mar_descripcion = db.Column(db.Text)

    # Constructor
    def __init__(self, mar_nombre, mar_descripcion=None):
        self.mar_nombre = mar_nombre
        self.mar_descripcion = mar_descripcion
    
    # Representación del objeto
    def __repr__(self):
        return f"<Marca {self.mar_nombre}>"    

# Model para la tabla Usuarios
class Usuarios(db.Model):
    __tablename__ = 'Usuarios'
    usu_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    usu_nombre = db.Column(db.String(100), nullable=False)
    usu_email = db.Column(db.String(100), nullable=False, unique=True)
    usu_password = db.Column(db.String(255), nullable=False)
    usu_rol = db.Column(Enum('ADMIN', 'OPERADOR', name='rol_enum'), nullable=False, default='OPERADOR')

    # Constructor
    def __init__(self, usu_nombre, usu_email, usu_password, usu_rol='OPERADOR'):
        self.usu_nombre = usu_nombre
        self.usu_email = usu_email
        self.usu_password = usu_password
        self.usu_rol = usu_rol
    
    # Representación del objeto
    def __repr__(self):
        return f"<Usuario {self.usu_nombre}>"
    

# Modelo para la tabla proveedor
class Proveedor(db.Model):
    __tablename__ = 'Proveedor'

    prov_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    prov_razon_social = db.Column(db.String(100), nullable=False, unique=True)
    prov_direccion = db.Column(db.String(100), unique=True, nullable=False)
    prov_telefono = db.Column(db.String(15), unique=True, nullable=False)
    prov_email = db.Column(db.String(100), unique=True, nullable=False)
    prov_descripcion = db.Column(db.Text)

    # Constructor
    def __init__(self, prov_razon_social, prov_direccion, prov_telefono, prov_email, prov_descripcion=None):
        self.prov_razon_social = prov_razon_social
        self.prov_direccion = prov_direccion
        self.prov_telefono = prov_telefono
        self.prov_email = prov_email
        self.prov_descripcion = prov_descripcion
    
    # Representación del objeto
    def __repr__(self):
        return f"<Proveedor {self.prov_razon_social}>"
    

######################
# Tablas con Relación#
######################


# Modelo para la tabla Productos
class Productos(db.Model):
    __tablename__ = 'Productos'
    pro_codigo = db.Column(db.String(13), primary_key=True)
    pro_nombre = db.Column(db.String(200), nullable=False)
    pro_descripcion = db.Column(db.Text)
    pro_cat_id = db.Column(db.Integer, ForeignKey('Categorias.cat_id'), nullable=False)
    pro_pres_id = db.Column(db.Integer, ForeignKey('Presentacion.pres_id'), nullable=False)
    pro_uni_id = db.Column(db.Integer, ForeignKey('Unidad.uni_id'), nullable=False)
    pro_mar_id = db.Column(db.Integer, ForeignKey('Marca.mar_id'), nullable=False)

    # Constructor
    def __init__(self, pro_codigo, pro_nombre, pro_cat_id, pro_pres_id, pro_uni_id, pro_mar_id, pro_descripcion=None):
        self.pro_codigo = pro_codigo
        self.pro_nombre = pro_nombre
        self.pro_descripcion = pro_descripcion
        self.pro_cat_id = pro_cat_id
        self.pro_pres_id = pro_pres_id
        self.pro_uni_id = pro_uni_id
        self.pro_mar_id = pro_mar_id

    # Representación del objeto
    def __repr__(self):
        return f"<Producto {self.pro_nombre}>"

# Modelo para la tabla de imagenes de productos
class ProductoImagenes(db.Model):
    __tablename__ = 'Producto_Imagenes'
    img_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    img_pro_codigo = db.Column(db.String(13), ForeignKey('Productos.pro_codigo'), nullable=False)
    img_url = db.Column(db.String(200), nullable=False)
    img_descripcion = db.Column(db.Text)

    # Constructor
    def __init__(self, img_pro_codigo, img_url, img_descripcion=None):
        self.img_pro_codigo = img_pro_codigo
        self.img_url = img_url
        self.img_descripcion = img_descripcion
    
    # Representación del objeto
    def __repr__(self):
        return f"<ProductoImagen {self.img_url} for Producto {self.img_pro_codigo}>"

# Modelo para la tabla Ubicaciones
class Ubicaciones(db.Model):
    __tablename__ = 'Ubicaciones'

    ubi_codigo = db.Column(db.String(50), primary_key=True)
    ubi_estanteria = db.Column(db.String(100), nullable=False)
    ubi_nivel = db.Column(db.String(100), nullable=False)
    ubi_cat_id = db.Column(db.Integer, ForeignKey('Categorias.cat_id'), nullable=False)
    ubi_capacidad = db.Column(db.Integer, nullable=False)
    ubi_descripcion = db.Column(db.Text)

    # Constructor
    def __init__(self, ubi_codigo, ubi_estanteria, ubi_nivel, ubi_cat_id, ubi_capacidad, ubi_descripcion=None):
        self.ubi_codigo = ubi_codigo
        self.ubi_estanteria = ubi_estanteria
        self.ubi_nivel = ubi_nivel
        self.ubi_cat_id = ubi_cat_id
        self.ubi_capacidad = ubi_capacidad
        self.ubi_descripcion = ubi_descripcion
    
    # Representación del objeto
    def __repr__(self):
        return f"<Ubicacion {self.ubi_codigo}>"
    
# Modelo para la tabla Documento de recibo
class DocumentoRecibo(db.Model):
    __tablename__ = 'Documento_recibo'
    doc_id = db.Column(db.String(100), primary_key=True)
    doc_id_proveedor = db.Column(db.Integer, ForeignKey('Proveedor.prov_id'), nullable=False)
    doc_fecha = db.Column(db.DateTime, default=datetime.utcnow)
    doc_estado = db.Column(Enum('PENDIENTE', 'RECHAZADO', 'ACEPTADO', name='estado_recibo_enum'), nullable=False, default='PENDIENTE')
    doc_descripcion = db.Column(db.Text)

    # Constructor
    def __init__(self, doc_id, doc_id_proveedor, doc_estado='PENDIENTE', doc_descripcion=None):
        self.doc_id = doc_id
        self.doc_id_proveedor = doc_id_proveedor
        self.doc_estado = doc_estado
        self.doc_descripcion = doc_descripcion

    # Representación del objeto
    def __repr__(self):
        return f"<DocumentoRecibo {self.doc_id}>"
    
# Modelo para la tabla de inventario
class Inventario(db.Model):
    __tablename__ = 'Inventario'

    inv_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    inv_pro_codigo = db.Column(db.String(13), db.ForeignKey('Productos.pro_codigo'), nullable=False)
    inv_cod_ubicacion = db.Column(db.String(50), db.ForeignKey('Ubicaciones.ubi_codigo'), nullable=False, unique=True)
    inv_cantidad = db.Column(db.Integer, nullable=False, default=0)
    inv_saldo = db.Column(db.Float, nullable=False, default=0.0)
    inv_fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Constructor
    def __init__(self, inv_pro_codigo, inv_cod_ubicacion, inv_cantidad=0, inv_saldo=0.0, inv_fecha_actualizacion=None):
        self.inv_pro_codigo = inv_pro_codigo
        self.inv_cod_ubicacion = inv_cod_ubicacion
        self.inv_cantidad = inv_cantidad
        self.inv_saldo = inv_saldo
        self.inv_fecha_actualizacion = inv_fecha_actualizacion
    
    # Representación del objeto
    def __repr__(self):
        return f"<Inventario Producto: {self.inv_pro_codigo} en Ubicacion: {self.inv_cod_ubicacion}>"

# Modelo para la tabla Movimientos
class Movimientos(db.Model):
    __tablename__ = 'Movimientos'

    mov_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    mov_pro_codigo = db.Column(db.String(13), ForeignKey('Productos.pro_codigo'), nullable=False)
    mov_inv_id = db.Column(db.Integer, ForeignKey('Inventario.inv_id'), nullable=False)
    mov_cantidad = db.Column(db.Integer, nullable=False)
    mov_doc_id = db.Column(db.String(100), ForeignKey('Documento_recibo.doc_id'), nullable=True)
    mov_fecha = db.Column(db.DateTime, default=datetime.utcnow)
    mov_tipo = db.Column(Enum('INGRESO', 'SALIDA', name='tipo_movimiento_enum'), nullable=False)
    mov_destino = db.Column(db.String(100), nullable=True)
    mov_usu_id = db.Column(db.Integer, ForeignKey('Usuarios.usu_id'), nullable=False)
    mov_observacion = db.Column(db.Text)

    # Constructor
    def __init__(self, mov_pro_codigo, mov_inv_id, mov_cantidad, mov_doc_id, mov_tipo, mov_usu_id, mov_destino=None, mov_observacion=None):
        self.mov_pro_codigo = mov_pro_codigo
        self.mov_inv_id = mov_inv_id
        self.mov_cantidad = mov_cantidad
        self.mov_doc_id = mov_doc_id
        self.mov_tipo = mov_tipo
        self.mov_usu_id = mov_usu_id
        self.mov_destino = mov_destino
        self.mov_observacion = mov_observacion

    # Representación del objeto
    def __repr__(self):
        return f"<Movimiento {self.mov_tipo} Producto: {self.mov_pro_codigo} Cantidad: {self.mov_cantidad}>"

        
