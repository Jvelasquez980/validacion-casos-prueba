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