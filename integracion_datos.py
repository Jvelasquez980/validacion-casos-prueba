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
    df_merged = df_merged.copy()
    
    # Crear Rating_Servicio si existen las columnas necesarias
    if 'Rating_Producto' in df_merged.columns and 'Rating_Logistica' in df_merged.columns:
        df_merged['Rating_Servicio'] = (df_merged['Rating_Producto'] * df_merged['Rating_Logistica'])/5
    elif 'Rating_Producto' in df_merged.columns:
        df_merged['Rating_Servicio'] = df_merged['Rating_Producto']
    
    # Crear Margen si existen las columnas necesarias
    if 'Precio_Venta_Final' in df_merged.columns and 'Costo_Unitario_USD' in df_merged.columns:
        # Evitar división por cero
        df_merged['Margen'] = ((df_merged['Precio_Venta_Final'] - df_merged['Costo_Unitario_USD']) / df_merged['Precio_Venta_Final'] * 100).fillna(0)
    elif 'Costo_Unitario_USD' in df_merged.columns:
        # Si no hay precio de venta, calcular con costo
        df_merged['Margen'] = df_merged['Costo_Unitario_USD']
    
    return df_merged

    
    # Métrica