import pandas as pd
import numpy as np

def corregir_nombres_ciudad_destino(df):
    df['Ciudad_Destino'] = df['Ciudad_Destino'].replace({
        'BOG': 'Bogotá',
        'MED': 'Medellín'})
    return df   

def corregir_canal_venta(df):
    df['Canal_Venta'] = df['Canal_Venta'].replace({ # Consideramos que es importante manteneer App como un canal dee venta debido a que nos puede dar informacion relevante con el uso de la aplicacion y la necesidad de mantenerla.
        'WhatsApp': 'Online'
    })

def corregir_valores_negativos_cantidad_vendida(df):
    df['Cantidad_vendida'] = df['Cantidad_vendida'].abs() # Encontramos valores negativos en cantidad vendida, los cuales no tienen sentido en este contexto, por lo que tomamos su valor absoluto.
    return df


def reemplazar_outliers_tiempo_entrega_real(df, metodo):
    """
    Reemplaza outliers en Tiempo_Entrega_Real usando el método IQR.
    
    Parámetros:
    - df: DataFrame a procesar (se modifica directamente)
    - metodo: 'limite', 'media', 'mediana', 'moda'
    """
    Q1 = df['Tiempo_Entrega_Real'].quantile(0.25)
    Q3 = df['Tiempo_Entrega_Real'].quantile(0.75)
    IQR = Q3 - Q1
    limite_inferior = Q1 - 1.5 * IQR
    limite_superior = Q3 + 1.5 * IQR
    
    # No puede haber tiempos negativos
    limite_inferior = max(limite_inferior, 0)
    
    mascara_outliers = (df['Tiempo_Entrega_Real'] < limite_inferior) | (df['Tiempo_Entrega_Real'] > limite_superior)
    
    # Aplicar el método de reemplazo
    if metodo == 'Limite':
        df['Tiempo_Entrega_Real'] = df['Tiempo_Entrega_Real'].clip(lower=limite_inferior, upper=limite_superior)
    elif metodo == 'Media':
        valor_reemplazo = df['Tiempo_Entrega_Real'][~mascara_outliers].mean()
        df.loc[mascara_outliers, 'Tiempo_Entrega_Real'] = valor_reemplazo
    elif metodo == 'Mediana':
        valor_reemplazo = df['Tiempo_Entrega_Real'][~mascara_outliers].median()
        df.loc[mascara_outliers, 'Tiempo_Entrega_Real'] = valor_reemplazo
    elif metodo == 'Moda':
        valor_reemplazo = df['Tiempo_Entrega_Real'][~mascara_outliers].mode()[0]
        df.loc[mascara_outliers, 'Tiempo_Entrega_Real'] = valor_reemplazo
    else:
        raise ValueError("El parámetro 'remplazo' debe ser 'media', 'mediana' o 'moda'.")
    
    return df

def imputar_costo_envio(df, remplzar_por='Mediana'):
    """
    Imputa valores faltantes en Costo_Envio con la media.
    """
    if remplzar_por == 'Mediana':
        mediana_costo_envio = df['Costo_Envio'].median()
        df['Costo_Envio'] = df['Costo_Envio'].fillna(mediana_costo_envio)
    elif remplzar_por == 'Media':
        media_costo_envio = df['Costo_Envio'].mean()
        df['Costo_Envio'] = df['Costo_Envio'].fillna(media_costo_envio)
    elif remplzar_por == 'Moda':
        moda_costo_envio = df['Costo_Envio'].mode()[0]
        df['Costo_Envio'] = df['Costo_Envio'].fillna(moda_costo_envio)
    else:
        raise ValueError("El parámetro 'remplazo' debe ser 'media', 'mediana' o 'moda'.")
    return df

def imputar_estado_envio(df, remplazo):
    """
    Imputa valores faltantes en Estado_Envio con la moda.
    
    Parámetros:
    - df: DataFrame a procesar (se modifica directamente)
    
    Nota: Se usa la moda porque el análisis mostró que no hay relación
    entre Tiempo_Entrega_Real y Estado_Envio.
    """
    if remplazo == 'Moda':
        moda_estado_envio = df['Estado_Envio'].mode()[0]
        df['Estado_Envio'] = df['Estado_Envio'].fillna(moda_estado_envio)
    elif  remplazo == 'Mediana':
        mediana_estado_envio= df['Estado_Envio'].median()[0]
        df['Estado_Envio'] = df['Estado_Envio'].fillna(mediana_estado_envio)
    elif remplazo == 'Media':
        media_estado_envio= df['Estado_Envio'].mean()[0]
        df['Estado_Envio'] = df['Estado_Envio'].fillna(media_estado_envio)
    else:
        raise ValueError("El parámetro 'remplazo' debe ser 'media', 'mediana' o 'moda'.")
        
    
    return df