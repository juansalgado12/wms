from flask import blueprints, render_template, redirect, request, url_for, flash, current_app

from .auth import login_required # Importar el decorador de login requerido
from .models import Productos, ProductoImagenes, Categorias, Presentacion, Unidad, Marca # Importar los modelos necesarios
from wmsr import db # Importar la base de datos

import os # Para manejo de rutas de archivos
from werkzeug.utils import secure_filename # Para asegurar nombres de archivos
from datetime import datetime # Para manejo de fechas y horas

from wmsr.utils.export_excel import exportar_a_excel

bp = blueprints.Blueprint('productos', __name__, url_prefix='/productos')

# Ruta para el catálogo de productos
@bp.route('/')
def catalogo():
    # Obtener productos y construir mapas id->nombre para usar en la plantilla
    productos = Productos.query.all()

    categorias = Categorias.query.all()
    presentaciones = Presentacion.query.all()
    unidades = Unidad.query.all()
    marcas = Marca.query.all()

    # Mapear id a nombre para cada entidad relacionada
    categorias_map = {c.cat_id: c.cat_nombre for c in categorias}
    presentaciones_map = {p.pres_id: p.pres_nombre for p in presentaciones}
    unidades_map = {u.uni_id: u.uni_nombre for u in unidades}
    marcas_map = {m.mar_id: m.mar_nombre for m in marcas}

    # Mapear la primera imagen por código de producto (si existe)
    imagenes = ProductoImagenes.query.all()
    image_map = {}
    for im in imagenes:
        if im.img_pro_codigo not in image_map:
            image_map[im.img_pro_codigo] = im.img_url

    return render_template(
        'productos/catalogo.html',
        productos=productos,
        categorias_map=categorias_map,
        presentaciones_map=presentaciones_map,
        unidades_map=unidades_map,
        marcas_map=marcas_map,
        image_map=image_map
    )


# Ruta para crear un nuevo producto
@bp.route('/crear', methods=('GET', 'POST'))
@login_required
def crear():
    mensaje_exito = None

    if request.method == 'POST':
        # Aquí iría la lógica para crear un nuevo producto
        codigo = request.form.get('pro_codigo')
        nombre = request.form.get('pro_nombre')
        categoria = request.form.get('pro_cat_id')
        presentacion = request.form.get('pro_pres_id')
        unidad = request.form.get('pro_uni_id')
        marca = request.form.get('pro_mar_id')
        descripcion = request.form.get('pro_descripcion')
        # y la imagen del formulario
        # soportar tanto 'image' como 'images' en el template (un solo fichero)
        imagen = request.files.get('image') or request.files.get('images')
        if not imagen and 'images' in request.files:
            # si es lista, intentar tomar el primero
            files = request.files.getlist('images')
            imagen = files[0] if files else None

        # Validar campos obligatorios
        if not codigo or not nombre or not categoria or not presentacion or not unidad or not marca:
            flash('Por favor, complete todos los campos obligatorios.', 'error')
            # recargar opciones para el template abajo
            categorias = Categorias.query.all()
            presentaciones = Presentacion.query.all()
            unidades = Unidad.query.all()
            marcas = Marca.query.all()
            return render_template('productos/crearproductos.html', categorias=categorias, presentaciones=presentaciones, unidades=unidades, marcas=marcas)

        # Validar unicidad por nombre y por código
        nombre_existente = Productos.query.filter_by(pro_nombre=nombre).first()
        if nombre_existente:
            flash('Ya existe un producto con ese nombre. El nombre debe ser único.', 'error')
            categorias = Categorias.query.all()
            presentaciones = Presentacion.query.all()
            unidades = Unidad.query.all()
            marcas = Marca.query.all()
            return render_template('productos/crearproductos.html', categorias=categorias, presentaciones=presentaciones, unidades=unidades, marcas=marcas)

        codigo_existente = Productos.query.get(codigo)
        if codigo_existente:
            flash('Ya existe un producto con ese código. El código debe ser único.', 'error')
            categorias = Categorias.query.all()
            presentaciones = Presentacion.query.all()
            unidades = Unidad.query.all()
            marcas = Marca.query.all()
            return render_template('productos/crearproductos.html', categorias=categorias, presentaciones=presentaciones, unidades=unidades, marcas=marcas)

        # Validar existencia de claves foráneas
        try:
            cat_id = int(categoria)
            pres_id = int(presentacion)
            uni_id = int(unidad)
            mar_id = int(marca)
        except (ValueError, TypeError):
            flash('Selecciona opciones válidas para categoría/presentación/unidad/marca.', 'error')
            categorias = Categorias.query.all()
            presentaciones = Presentacion.query.all()
            unidades = Unidad.query.all()
            marcas = Marca.query.all()
            return render_template('productos/crearproductos.html', categorias=categorias, presentaciones=presentaciones, unidades=unidades, marcas=marcas)

        if not Categorias.query.get(cat_id) or not Presentacion.query.get(pres_id) or not Unidad.query.get(uni_id) or not Marca.query.get(mar_id):
            flash('Alguna de las opciones seleccionadas no existe en la base de datos.', 'error')
            categorias = Categorias.query.all()
            presentaciones = Presentacion.query.all()
            unidades = Unidad.query.all()
            marcas = Marca.query.all()
            return render_template('productos/crearproductos.html', categorias=categorias, presentaciones=presentaciones, unidades=unidades, marcas=marcas)

        # Crear la instancia del producto
        producto = Productos(pro_codigo=codigo, pro_nombre=nombre, pro_cat_id=cat_id, pro_pres_id=pres_id, pro_uni_id=uni_id, pro_mar_id=mar_id, pro_descripcion=descripcion)

        # Guardar el producto primero (flush) para que exista la fila padre antes de insertar la imagen
        try:
            db.session.add(producto)
            db.session.flush()
        except Exception as e:
            db.session.rollback()
            current_app.logger.exception('Error guardando temporalmente el producto (flush)')
            flash('Ocurrió un error al validar el producto. Por favor revise los datos. (' + f"{e.__class__.__name__}: {e}" + ')', 'error')
            categorias = Categorias.query.all()
            presentaciones = Presentacion.query.all()
            unidades = Unidad.query.all()
            marcas = Marca.query.all()
            return render_template('productos/crearproductos.html', categorias=categorias, presentaciones=presentaciones, unidades=unidades, marcas=marcas)

        # Manejo de la imagen (opcional). Como el producto ya fue flushed, la FK existirá.
        imagen_model = None
        if imagen and imagen.filename:
            filename = secure_filename(imagen.filename)
            # generar nombre único
            timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
            # truncar nombre base para evitar ficheros muy largos, mantener extensión
            name, ext = os.path.splitext(filename)
            name = name[:40]
            filename = f"{codigo}_{timestamp}_{name}{ext}"
            upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'products')
            os.makedirs(upload_folder, exist_ok=True)
            save_path = os.path.join(upload_folder, filename)
            try:
                imagen.save(save_path)
                # url relativa para almacenar en DB
                img_url = url_for('static', filename=f'uploads/products/{filename}')
                imagen_model = ProductoImagenes(img_pro_codigo=codigo, img_url=img_url, img_descripcion=None)
            except Exception as e:
                current_app.logger.exception('Error guardando la imagen de producto')
                flash('Ocurrió un error guardando la imagen.', 'error')

        # Commit final: producto ya está en la sesión y flushed; agregar imagen_model si existe y commitear
        try:
            if imagen_model:
                db.session.add(imagen_model)
            db.session.commit()
            flash('Producto creado correctamente.', 'success')
            return redirect(url_for('productos.catalogo'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.exception('Error creando el producto')
            # Mostrar el tipo de excepción y mensaje corto para depuración local
            err_msg = f"{e.__class__.__name__}: {str(e)}"
            flash('Ocurrió un error al crear el producto. Por favor intente de nuevo. (' + err_msg + ')', 'error')



    # GET: renderizar formulario con datos para selects
    categorias = Categorias.query.all()
    presentaciones = Presentacion.query.all()
    unidades = Unidad.query.all()
    marcas = Marca.query.all()
    return render_template('productos/crearproductos.html', categorias=categorias, presentaciones=presentaciones, unidades=unidades, marcas=marcas)

# Ruta para editar un producto existente
@bp.route('/editar')
def editar():
    return render_template('productos/editar.html')

@bp.route('/exportar_excel')
@login_required
def exportar_productos_excel():
    # Hacemos los JOINs con las tablas relacionadas
    productos = (
        db.session.query(
            Productos.pro_codigo,
            Productos.pro_nombre,
            Productos.pro_descripcion,
            Productos.pro_cat_id,
            Categorias.cat_nombre.label("nombre_categoria"),
            Productos.pro_pres_id,
            Presentacion.pres_nombre.label("nombre_presentacion"),
            Productos.pro_uni_id,
            Unidad.uni_nombre.label("nombre_unidad"),
            Productos.pro_mar_id,
            Marca.mar_nombre.label("nombre_marca")
        )
        .outerjoin(Categorias, Productos.pro_cat_id == Categorias.cat_id)
        .outerjoin(Presentacion, Productos.pro_pres_id == Presentacion.pres_id)
        .outerjoin(Unidad, Productos.pro_uni_id == Unidad.uni_id)
        .outerjoin(Marca, Productos.pro_mar_id == Marca.mar_id)
        .all()
    )

    # Convertimos los resultados a diccionarios para exportar
    data = [
        {
            'Código': p.pro_codigo,
            'Nombre': p.pro_nombre,
            'Descripción': p.pro_descripcion,
            'ID Categoría': p.pro_cat_id,
            'Nombre Categoría': p.nombre_categoria or '',
            'ID Presentación': p.pro_pres_id,
            'Nombre Presentación': p.nombre_presentacion or '',
            'ID Unidad': p.pro_uni_id,
            'Nombre Unidad': p.nombre_unidad or '',
            'ID Marca': p.pro_mar_id,
            'Nombre Marca': p.nombre_marca or '',
        }
        for p in productos
    ]

    columnas = [
        'Código', 'Nombre', 'Descripción',
        'ID Categoría', 'Nombre Categoría',
        'ID Presentación', 'Nombre Presentación',
        'ID Unidad', 'Nombre Unidad',
        'ID Marca', 'Nombre Marca'
    ]

    return exportar_a_excel('productos', columnas, data)