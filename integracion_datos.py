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
    DataFrame : Dataframe con nuevas métricas añadidas:
        - Rating_Servicio: Combinación de ratings de producto y logística
        - Margen_Unitario_Pct: Margen porcentual por unidad (antes de envío)
        - Ganancia_Neta_Total: Ganancia total REAL (considerando envío) en USD
        - Margen_Real_Pct: Margen porcentual REAL (considerando envío y cantidad)
    """
    df_merged = df_merged.copy()
    
    # ============================================================
    # 1. Rating_Servicio: Combinación de ratings
    # ============================================================
    if 'Rating_Producto' in df_merged.columns and 'Rating_Logistica' in df_merged.columns:
        df_merged['Rating_Servicio'] = (df_merged['Rating_Producto'] * df_merged['Rating_Logistica']) / 5
    elif 'Rating_Producto' in df_merged.columns:
        df_merged['Rating_Servicio'] = df_merged['Rating_Producto']
    
    # ============================================================
    # 2. Margen_Unitario_Pct: Margen por unidad (solo costo de producto)
    # ============================================================
    if 'Precio_Venta_Final' in df_merged.columns and 'Costo_Unitario_USD' in df_merged.columns:
        df_merged['Margen_Unitario_Pct'] = (
            (df_merged['Precio_Venta_Final'] - df_merged['Costo_Unitario_USD']) 
            / df_merged['Precio_Venta_Final'] * 100
        ).fillna(0).clip(lower=0)  # No permitir márgenes negativos
    elif 'Costo_Unitario_USD' in df_merged.columns:
        df_merged['Margen_Unitario_Pct'] = df_merged['Costo_Unitario_USD']
    
    # ============================================================
    # 3. Ganancia_Neta_Total: Ganancia TOTAL considerando envío
    # ============================================================
    if 'Precio_Venta_Final' in df_merged.columns and 'Costo_Unitario_USD' in df_merged.columns:
        # Garantizar que Cantidad_Vendida > 0 para evitar división por cero
        cantidad_vendida = df_merged.get('Cantidad_Vendida', 1).copy()
        cantidad_vendida = cantidad_vendida.replace(0, 1)  # Reemplazar 0 con 1 para evitar errores
        
        # Costo de envío por unidad
        costo_envio = df_merged.get('Costo_Envio', 0).fillna(0)
        costo_envio_unitario = costo_envio / cantidad_vendida
        
        # Ganancia por unidad (considerando costo de envío)
        ganancia_unitaria = (
            df_merged['Precio_Venta_Final'] 
            - df_merged['Costo_Unitario_USD'] 
            - costo_envio_unitario
        )
        
        # Ganancia total = ganancia por unidad × cantidad vendida
        df_merged['Ganancia_Neta_Total'] = (ganancia_unitaria * cantidad_vendida).clip(lower=0).fillna(0)
    
    # ============================================================
    # 4. Margen_Real_Pct: Margen porcentual considerando TODOS los costos
    # ============================================================
    if 'Precio_Venta_Final' in df_merged.columns and 'Ganancia_Neta_Total' in df_merged.columns:
        # Revenue total = Precio_Venta × Cantidad
        cantidad_vendida = df_merged.get('Cantidad_Vendida', 1).copy()
        cantidad_vendida = cantidad_vendida.replace(0, 1)
        revenue_total = df_merged['Precio_Venta_Final'] * cantidad_vendida
        
        # Margen real = (Ganancia / Revenue) × 100
        df_merged['Margen_Real_Pct'] = (
            (df_merged['Ganancia_Neta_Total'] / revenue_total * 100)
            .fillna(0)
            .clip(lower=-100, upper=100)  # Limitar entre -100% y 100%
        )
    
    return df_merged