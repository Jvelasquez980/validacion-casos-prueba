import pandas as pd

def integrar_datos(df_transaccion, df_feedback, df_inventario):
    """
    Integra los dataframes de transacción, feedback e inventario en un solo dataframe.
    
    Parámetros:
    -----------
    df_transaccion : DataFrame
        DataFrame de transacciones logísticas
    df_feedback : DataFrame
        DataFrame de feedback de clientes
    df_inventario : DataFrame
        DataFrame de inventario central
    
    Retorna:
    --------
    DataFrame : Dataframe integrado con todas las fuentes de datos
    """
    # Merge transacción con feedback de clientes por Transaccion_ID
    df_merged = pd.merge(df_transaccion, df_feedback, on='Transaccion_ID', how='inner')
    print(f"Merge transacción + feedback: {len(df_merged)} filas")
    
    # Merge con inventario por SKU_ID
    df_merged = pd.merge(df_merged, df_inventario, on='SKU_ID', how='inner')
    print(f"Merge final con inventario: {len(df_merged)} filas")
    
    print("\nDatos integrados exitosamente")
    print(f"Columnas totales: {len(df_merged.columns)}")
    
    return df_merged

def crear_metricas_nuevas(df_merged):
    """
    Crea nuevas métricas en el dataframe integrado.
    
    Parámetros:
    -----------
    df_merged : DataFrame
        DataFrame integrado con todas las fuentes de datos
        
    Retorna:
    --------
    DataFrame : Dataframe con nuevas métricas añadidas
    """
    df_merged['Rating_Servicio'] = (df_merged['Rating_Producto'] * df_merged['Rating_Logistica'])/5 # El calculo de esta metrica es basado en el maximo puntaje de ambos,  este siendo 5 en ambos valores
    # Lo que nos da un puntaje maximo de 25, por lo que lo dividimos entre 5 para normalizarlo a una escala de 0 a 5.

    return df_merged

    
    # Métrica