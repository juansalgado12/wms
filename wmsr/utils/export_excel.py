import io
import pandas as pd
from flask import make_response

def exportar_a_excel(nombre_archivo, columnas, registros):
    """
    Exporta una lista de registros a un archivo Excel y devuelve la respuesta Flask.

    :param nombre_archivo: str -> nombre del archivo sin extensión (por ejemplo, 'proveedores')
    :param columnas: list[str] -> nombres de las columnas
    :param registros: list[dict] -> lista de diccionarios o filas
    """
    # Crear DataFrame
    df = pd.DataFrame(registros, columns=columnas)

    # Guardar en un buffer de memoria
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Datos')

    # Preparar respuesta Flask
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = f'attachment; filename={nombre_archivo}.xlsx'
    response.headers['Content-type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    return response
