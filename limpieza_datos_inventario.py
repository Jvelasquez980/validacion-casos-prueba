import pandas as pd
import numpy as np

def imputar_valores_columna_stock_actual(df,remplazo):
    if remplazo == 'media':
        valor_reemplazo = df['Stock_Actual'].mean()
    elif remplazo == 'mediana':
        valor_reemplazo = df['Stock_Actual'].median()
    elif remplazo == 'moda':
        valor_reemplazo = df['Stock_Actual'].mode()[0]
    else:
        raise ValueError("El parámetro 'remplazo' debe ser 'media', 'mediana' o 'moda'.")
    df['Stock_Sctual'].fillna(valor_reemplazo, inplace=True)
    df['Stock_Sctual'] = df['Stock_Sctual'].astype(int)
    df['Stock_Sctual'] = df['Stock_Sctual'].abs()
    return df

def imputar_valores_columna_lead_time_dias(df):
    df['Lead_Time_Dias'] = df['Lead_Time_Dias'].replace({
        '25-30 dias': 27,
        '25-30 días': 27,
        'Inmediato': 0
    })

    # Convertimos a int, manejando posibles NaN con fillna
    df['Lead_Time_Dias'] = pd.to_numeric(df['Lead_Time_Dias'], errors='coerce')
    df['Lead_Time_Dias'] = df['Lead_Time_Dias'].fillna(df['Lead_Time_Dias'].median()).astype(int)

    return df
def corregir_tipos_datos_punto_reorden(df):
    df['Punto_Reorden'] = pd.to_numeric(df['Punto_Reorden'], errors='coerce')
    df['Punto_Reorden'] = df['Punto_Reorden'].fillna(df['Punto_Reorden'].median()).astype(int)
    df['Punto_Reorden'] = df['Punto_Reorden'].abs()
    return df
def corregir_nombres_bodega_origen(df):
    df['Bodega_Origen'] = df['Bodega_Origen'].str.upper().str.strip()
    return df


def limpiar_atipicos_costo_unitario(df,remplazo):
    categorias_unicas = df['Categoria'].unique()
    LIMITE_SUPERIOR = 10000 # Estos limites fueron seleccionados de forma manual, por lo que no se sigue ningun patron exacto de manejo de datos atipicos
    LIMITE_INFERIOR = 30
    medidas_catg = {}
    for categoria_unica in categorias_unicas:
        moda = df[df['Categoria'] == categoria_unica]['Costo_Unitario_USD'].mode()[0]
        mediana = df[df['Categoria'] == categoria_unica]['Costo_Unitario_USD'].median()
        promedio = df[df['Categoria'] == categoria_unica]['Costo_Unitario_USD'].mean()
        medidas_catg[categoria_unica] = {'Moda': moda, 'Mediana': mediana, 'Promedio': promedio}

    for categoria_unica in categorias_unicas:
        # Identificamos valores que superan el límite superior
        mask_outliers_altos = (df['categoria'] == categoria_unica) & (df['costo_unitario'] > LIMITE_SUPERIOR)
        num_outliers_altos = mask_outliers_altos.sum()

        # Identificamos valores que están por debajo del límite inferior
        mask_outliers_bajos = (df['categoria'] == categoria_unica) & (df['costo_unitario'] < LIMITE_INFERIOR)
        num_outliers_bajos = mask_outliers_bajos.sum()

        # Obtenemos la moda de la categoría
        if remplazo == 'Moda':
            valor_remplazo = medidas_catg[categoria_unica]['Moda']
        elif remplazo == "Mediana":
            valor_remplazo = medidas_catg[categoria_unica]['Mediana']
        elif remplazo == "Promedio":
            valor_remplazo = medidas_catg[categoria_unica]['Promedio']
        else:
            raise ValueError("El parámetro 'remplazo' debe ser 'media', 'mediana' o 'moda'.")

        if num_outliers_altos > 0:
            # Reemplazamos valores altos con la moda
            df.loc[mask_outliers_altos, 'costo_unitario'] = valor_remplazo
        if num_outliers_bajos > 0:
            # Reemplazamos valores bajos con la moda
            df.loc[mask_outliers_bajos, 'costo_unitario'] = valor_remplazo
    return df

def imputar_valores_columna_categoria(df, remplazo):
    """
    Reemplaza valores '???' en la columna Categoria basándose en la medida estadística
    más cercana del costo_unitario.
    
    Args:
        df: DataFrame con los datos
        remplazo: 'Moda', 'Mediana' o 'Promedio' - medida a usar para la comparación
    
    Returns:
        DataFrame con categorías imputadas
    """
    if remplazo not in ['Moda', 'Mediana', 'Promedio']:
        raise ValueError("El parámetro 'remplazo' debe ser 'Moda', 'Mediana' o 'Promedio'.")
    
    # Obtenemos categorías únicas excluyendo '???'
    categorias_unicas = df['Categoria'].unique()
    categorias_validas = [cat for cat in categorias_unicas if cat != '???']
    
    # Calculamos las medidas estadísticas para cada categoría válida
    medidas_por_categoria = {}
    
    for cat in categorias_validas:
        datos_cat = df[df['Categoria'] == cat]['Costo_Unitario_USD']
        if remplazo == 'Moda':
            medida = datos_cat.mode()[0]
        elif remplazo == 'Mediana':
            medida = datos_cat.median()
        else:  # Promedio
            medida = datos_cat.mean()
        medidas_por_categoria[cat] = medida
    
    # Identificamos filas con categoria "???"
    mask_desconocidos = df['Categoria'] == '???'
    
    # Reemplazamos cada "???" con la categoría cuya medida esté más cercana
    for idx in df[mask_desconocidos].index:
        costo_valor = df.loc[idx, 'Costo_Unitario_USD']
        
        # Encontramos la categoría con la medida más cercana
        categoria_asignada = min(medidas_por_categoria.keys(), 
                                key=lambda cat: abs(medidas_por_categoria[cat] - costo_valor))
        
        # Reemplazamos la categoría
        df.loc[idx, 'Categoria'] = categoria_asignada
    
    return df

def limpiezar_fecha_ultima_revision(df):
    df['ultima_revision'] = pd.to_datetime(df['ultima_revision'], errors='coerce')
    fecha_minima = df['ultima_revision'].min()
    df['ultima_revision'].fillna(fecha_minima, inplace=True)
    return df