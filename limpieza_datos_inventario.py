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
    df['Stock_Actual'].fillna(valor_reemplazo, inplace=True)
    df['Stock_Actual'] = df['Stock_Actual'].astype(int)
    df['Stock_Actual'] = df['Stock_Actual'].abs()
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
        medidas_catg[categoria_unica] = {'moda': moda, 'mediana': mediana, 'media': promedio}

    for categoria_unica in categorias_unicas:
        # Identificamos valores que superan el límite superior
        mask_outliers_altos = (df['Categoria'] == categoria_unica) & (df['Costo_Unitario_USD'] > LIMITE_SUPERIOR)
        num_outliers_altos = mask_outliers_altos.sum()

        # Identificamos valores que están por debajo del límite inferior
        mask_outliers_bajos = (df['Categoria'] == categoria_unica) & (df['Costo_Unitario_USD'] < LIMITE_INFERIOR)
        num_outliers_bajos = mask_outliers_bajos.sum()

        # Obtenemos la moda de la categoría
        if remplazo == 'moda':
            valor_remplazo = medidas_catg[categoria_unica]['moda']
        elif remplazo == "mediana":
            valor_remplazo = medidas_catg[categoria_unica]['mediana']
        elif remplazo == "media":
            valor_remplazo = medidas_catg[categoria_unica]['media']
        else:
            raise ValueError("El parámetro 'remplazo' debe ser 'media', 'mediana' o 'moda'.")

        if num_outliers_altos > 0:
            # Reemplazamos valores altos con la moda
            df.loc[mask_outliers_altos, 'Costo_Unitario_USD'] = valor_remplazo
        if num_outliers_bajos > 0:
            # Reemplazamos valores bajos con la moda
            df.loc[mask_outliers_bajos, 'Costo_Unitario_USD'] = valor_remplazo
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
    df['Categoria'] = df['Categoria'].replace({'LAPTOP':'Laptops',
                                       'smart-phone':'Smartphones',
                                       '???': np.nan})
    if remplazo not in ['moda', 'mediana', 'media']:
        raise ValueError("El parámetro 'remplazo' debe ser 'moda', 'mediana' o 'media'.")
    df['Categoria'] = df['Categoria'].astype(str)   
    # Obtenemos categorías únicas excluyendo NaN y 'nan'
    categorias_unicas = df['Categoria'].unique()
    categorias_validas = [cat for cat in categorias_unicas if cat not in ['nan', np.nan]]
    
    # Calculamos las medidas estadísticas para cada categoría válida
    medidas_por_categoria = {}
    
    for cat in categorias_validas:
        datos_cat = df[df['Categoria'] == cat]['Costo_Unitario_USD']
        if remplazo == 'moda':
            medida = datos_cat.mode()[0]
        elif remplazo == 'mediana':
            medida = datos_cat.median()
        else:  # media
            medida = datos_cat.mean()
        medidas_por_categoria[cat] = medida
    
    # Identificamos filas con categoria "???" o 'nan' (string después de astype)
    mask_desconocidos = (df['Categoria'] == 'nan')
    # Reemplazamos cada "???" con la categoría cuya medida esté más cercana
    for idx in df[mask_desconocidos].index:
        costo_valor = df.loc[idx, 'Costo_Unitario_USD']
        
        # Encontramos la categoría con la medida más cercana
        categoria_asignada = min(medidas_por_categoria.keys(), 
                                key=lambda cat: abs(medidas_por_categoria[cat] - costo_valor))
        print(f"Reemplazando '???' en índice {idx} con categoría '{categoria_asignada}' basada en costo unitario de {costo_valor}.")
        # Reemplazamos la categoría
        df.loc[idx, 'Categoria'] = categoria_asignada
    
    return df

def limpiezar_fecha_ultima_revision(df):
    df['Ultima_Revision'] = pd.to_datetime(df['Ultima_Revision'], errors='coerce')
    fecha_minima = df['Ultima_Revision'].min()
    df['Ultima_Revision'].fillna(fecha_minima, inplace=True)
    return df