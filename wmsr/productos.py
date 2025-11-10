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

# Ruta para editar un producto existente (editar por código)
@bp.route('/editar/<string:codigo>', methods=('GET', 'POST'))
@login_required
def editar_producto(codigo):
    # Buscar producto por código
    producto = Productos.query.get(codigo)
    if not producto:
        flash('Producto no encontrado.', 'error')
        return redirect(url_for('productos.catalogo'))

    if request.method == 'POST':
        # Leer campos del formulario
        new_codigo = request.form.get('pro_codigo')
        nombre = request.form.get('pro_nombre')
        categoria = request.form.get('pro_cat_id')
        presentacion = request.form.get('pro_pres_id')
        unidad = request.form.get('pro_uni_id')
        marca = request.form.get('pro_mar_id')
        descripcion = request.form.get('pro_descripcion')
        imagen = request.files.get('image') or request.files.get('images')

        # Validaciones básicas
        if not new_codigo or not nombre or not categoria or not presentacion or not unidad or not marca:
            flash('Por favor, complete todos los campos obligatorios.', 'error')
            # recargar selects abajo
        else:
            # unicidad nombre (excluir el producto actual)
            otro_nombre = Productos.query.filter(Productos.pro_nombre == nombre, Productos.pro_codigo != producto.pro_codigo).first()
            if otro_nombre:
                flash('Ya existe otro producto con ese nombre.', 'error')
            else:
                # Si cambió el código, validar que no exista ya
                codigo_cambiado = (new_codigo != producto.pro_codigo)
                if codigo_cambiado and Productos.query.get(new_codigo):
                    flash('El nuevo código ya está en uso por otro producto.', 'error')
                else:
                    # Validar FK ids
                    try:
                        cat_id = int(categoria)
                        pres_id = int(presentacion)
                        uni_id = int(unidad)
                        mar_id = int(marca)
                    except (ValueError, TypeError):
                        flash('Selecciona opciones válidas para categoría/presentación/unidad/marca.', 'error')
                        cat_id = pres_id = uni_id = mar_id = None

                    if not (cat_id and pres_id and uni_id and mar_id):
                        pass
                    elif not (Categorias.query.get(cat_id) and Presentacion.query.get(pres_id) and Unidad.query.get(uni_id) and Marca.query.get(mar_id)):
                        flash('Alguna de las opciones seleccionadas no existe en la base de datos.', 'error')
                    else:
                        # Comenzar transacción
                        try:
                            if codigo_cambiado:
                                # Crear nuevo producto con el nuevo código
                                nuevo = Productos(pro_codigo=new_codigo, pro_nombre=nombre, pro_cat_id=cat_id, pro_pres_id=pres_id, pro_uni_id=uni_id, pro_mar_id=mar_id, pro_descripcion=descripcion)
                                db.session.add(nuevo)
                                db.session.flush()

                                # Mover imágenes existentes al nuevo código (si las hay)
                                imagenes = ProductoImagenes.query.filter_by(img_pro_codigo=producto.pro_codigo).all()
                                for im in imagenes:
                                    im.img_pro_codigo = new_codigo
                                    db.session.add(im)

                                # Manejo de imagen subida (reemplazo)
                                if imagen and imagen.filename:
                                    # Guardar fichero nuevo
                                    filename = secure_filename(imagen.filename)
                                    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
                                    name, ext = os.path.splitext(filename)
                                    name = name[:40]
                                    filename = f"{new_codigo}_{timestamp}_{name}{ext}"
                                    upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'products')
                                    os.makedirs(upload_folder, exist_ok=True)
                                    save_path = os.path.join(upload_folder, filename)
                                    imagen.save(save_path)
                                    img_url = url_for('static', filename=f'uploads/products/{filename}')

                                    # Si había imágenes previamente, reemplazar la primera
                                    im_first = ProductoImagenes.query.filter_by(img_pro_codigo=new_codigo).first()
                                    if im_first:
                                        # eliminar archivo anterior en disco (si existe)
                                        try:
                                            old_filename = os.path.basename(im_first.img_url)
                                            old_path = os.path.join(current_app.root_path, 'static', 'uploads', 'products', old_filename)
                                            if os.path.exists(old_path):
                                                os.remove(old_path)
                                        except Exception:
                                            current_app.logger.exception('No se pudo eliminar la imagen anterior')
                                        im_first.img_url = img_url
                                        db.session.add(im_first)
                                    else:
                                        new_im = ProductoImagenes(img_pro_codigo=new_codigo, img_url=img_url, img_descripcion=None)
                                        db.session.add(new_im)

                                # Borrar el producto antiguo
                                db.session.delete(producto)
                                db.session.commit()
                                flash('Producto actualizado correctamente.', 'success')
                                return redirect(url_for('productos.catalogo'))

                            else:
                                # Código no cambia, actualizar campos sobre el mismo objeto
                                producto.pro_nombre = nombre
                                producto.pro_cat_id = cat_id
                                producto.pro_pres_id = pres_id
                                producto.pro_uni_id = uni_id
                                producto.pro_mar_id = mar_id
                                producto.pro_descripcion = descripcion
                                db.session.add(producto)
                                db.session.flush()

                                # Manejo de imagen: reemplazar si se sube una nueva
                                if imagen and imagen.filename:
                                    filename = secure_filename(imagen.filename)
                                    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
                                    name, ext = os.path.splitext(filename)
                                    name = name[:40]
                                    filename = f"{producto.pro_codigo}_{timestamp}_{name}{ext}"
                                    upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'products')
                                    os.makedirs(upload_folder, exist_ok=True)
                                    save_path = os.path.join(upload_folder, filename)
                                    imagen.save(save_path)
                                    img_url = url_for('static', filename=f'uploads/products/{filename}')

                                    im_first = ProductoImagenes.query.filter_by(img_pro_codigo=producto.pro_codigo).first()
                                    if im_first:
                                        # eliminar archivo anterior
                                        try:
                                            old_filename = os.path.basename(im_first.img_url)
                                            old_path = os.path.join(current_app.root_path, 'static', 'uploads', 'products', old_filename)
                                            if os.path.exists(old_path):
                                                os.remove(old_path)
                                        except Exception:
                                            current_app.logger.exception('No se pudo eliminar la imagen anterior')
                                        im_first.img_url = img_url
                                        db.session.add(im_first)
                                    else:
                                        new_im = ProductoImagenes(img_pro_codigo=producto.pro_codigo, img_url=img_url, img_descripcion=None)
                                        db.session.add(new_im)

                                db.session.commit()
                                flash('Producto actualizado correctamente.', 'success')
                                return redirect(url_for('productos.catalogo'))

                        except Exception as e:
                            db.session.rollback()
                            current_app.logger.exception('Error actualizando producto')
                            flash('Ocurrió un error al actualizar el producto. (' + f"{e.__class__.__name__}: {e}" + ')', 'error')

    # GET: renderizar formulario con datos para selects (y por si POST falló, recargar selects)
    categorias = Categorias.query.all()
    presentaciones = Presentacion.query.all()
    unidades = Unidad.query.all()
    marcas = Marca.query.all()

    # obtener primera imagen
    img_row = ProductoImagenes.query.filter_by(img_pro_codigo=producto.pro_codigo).first()
    producto_image_url = img_row.img_url if img_row else None

    return render_template('productos/editarproducto.html', producto=producto, categorias=categorias, presentaciones=presentaciones, unidades=unidades, marcas=marcas, producto_image_url=producto_image_url)

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