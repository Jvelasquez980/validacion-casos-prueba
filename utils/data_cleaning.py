"""
Módulo integrado de limpieza de datos para todas las fuentes
"""
from limpieza_datos_inventario import (
    imputar_valores_columna_stock_actual,
    imputar_valores_columna_lead_time_dias,
    corregir_tipos_datos_punto_reorden,
    corregir_nombres_bodega_origen,
    limpiar_atipicos_costo_unitario,
    imputar_valores_columna_categoria,
    limpiezar_fecha_ultima_revision
)

from limpieza_datos_feedback import (
    manejar_outliers_rating_producto,
    manejar_outliers_edad_cliente,
    imputar_valores_comentario_texto,
    imputar_valores_recomienda_marca
)

from limpieza_datos_transacciones import (
    corregir_nombres_ciudad_destino,
    corregir_canal_venta,
    corregir_valores_negativos_cantidad_vendida,
    reemplazar_outliers_tiempo_entrega_real,
    imputar_costo_envio,
    imputar_estado_envio
)

import pandas as pd
import numpy as np


def calcular_health_score(df):
    """
    Calcula el health score de un dataframe basado en:
    - Porcentaje de valores nulos
    - Duplicados completos
    - Proporción de outliers (usando IQR)
    - Valores negativos en columnas que no deberían tenerlos
    
    Retorna un score entre 0 y 100
    """
    no_negative_colums = ['Stock_Actual', 'Cantidad_Vendida']
    if df.empty or len(df) == 0:
        return 0.0
    
    n_rows, n_cols = df.shape
    
    # Calcular nulidad global
    if 'Comentario_Texto' in df.columns:
        df.loc[df['Comentario_Texto'] == "---", 'Comentario_Texto'] = np.nan
    null_global_pct = (df.isna().sum().sum() / (n_rows * n_cols) * 100) if (n_rows and n_cols) else 0.0
    
    # Calcular duplicados
    dup_rows = int(df.duplicated().sum())
    dup_ratio = (dup_rows / n_rows * 100) if n_rows else 0.0
    
    # Calcular outliers en columnas numéricas usando IQR
    outlier_ratio = 0.0
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    
    if len(numeric_cols) > 0:
        total_outliers = 0
        for col in numeric_cols:
            try:
                s = pd.to_numeric(df[col], errors='coerce').dropna()
                if len(s) > 0:
                    q1 = s.quantile(0.25)
                    q3 = s.quantile(0.75)
                    iqr = q3 - q1
                    if iqr > 0:
                        lower = q1 - 1.5 * iqr
                        upper = q3 + 1.5 * iqr
                        mask = (s < lower) | (s > upper)
                        total_outliers += mask.sum()
            except:
                pass
        
        outlier_ratio = (total_outliers / (n_rows * len(numeric_cols)) * 100) if (n_rows and len(numeric_cols)) else 0.0
    
    # Calcular valores negativos en columnas que no deberían tenerlos
    negative_ratio = 0.0
    negative_count = 0
    for col in no_negative_colums:
        if col in df.columns:
            try:
                s = pd.to_numeric(df[col], errors='coerce')
                negative_in_col = (s < 0).sum()
                negative_count += negative_in_col
            except:
                pass
    
    if negative_count > 0:
        negative_ratio = (negative_count / n_rows * 100)
    
    # Calcular health score con pesos basados en severidad
    # Los pesos representan independientemente cuán grave es cada problema
    # No necesitan sumar 100 porque los errores son acumulativos
    penalty_nulls = null_global_pct * 0.4           # Moderadamente grave (se pueden imputar)
    penalty_dup = dup_ratio * 0.5                   # Grave (datos redundantes)
    penalty_outliers = outlier_ratio * 0.7          # Muy grave (sesgan análisis y modelos)
    penalty_negatives = negative_ratio * 0.6        # Muy grave (valores inválidos claros)
    
    score = 100 - (penalty_nulls + penalty_dup + penalty_outliers + penalty_negatives)
    score = float(max(0, min(100, score)))
    
    return score


def contar_valores_invalidos(df):
    """
    Cuenta los valores negativos en columnas que no deberían tenerlos
    Retorna el total de valores inválidos encontrados
    """
    no_negative_colums = ['Stock_Actual', 'Cantidad_Vendida']
    invalid_count = 0
    
    for col in no_negative_colums:
        if col in df.columns:
            try:
                s = pd.to_numeric(df[col], errors='coerce')
                invalid_count += (s < 0).sum()
            except:
                pass
    
    return invalid_count


def generar_audit_summary(df_antes, df_despues, dataset_name="Dataset"):
    """
    Genera un resumen de auditoría comparativo antes y después de limpieza
    Retorna un diccionario con las métricas
    """
    return {
        'dataset': dataset_name,
        'registros_antes': len(df_antes),
        'registros_despues': len(df_despues),
        'registros_eliminados': len(df_antes) - len(df_despues),
        'pct_registros_perdidos': ((len(df_antes) - len(df_despues)) / len(df_antes) * 100) if len(df_antes) > 0 else 0.0,
        'health_score_antes': calcular_health_score(df_antes),
        'health_score_despues': calcular_health_score(df_despues),
        'columnas': len(df_antes.columns),
        'nulos_antes': df_antes.isna().sum().sum(),
        'nulos_despues': df_despues.isna().sum().sum(),
        'valores_invalidos_antes': contar_valores_invalidos(df_antes),
        'valores_invalidos_despues': contar_valores_invalidos(df_despues),
    }





def limpiar_inventario(df):
    """Aplica todas las funciones de limpieza para datos de Inventario"""
    df = df.copy()
    
    try:
        df = imputar_valores_columna_stock_actual(df, 'mediana')
    except:
        pass
    
    try:
        df = imputar_valores_columna_lead_time_dias(df)
    except:
        pass
    
    try:
        df = corregir_tipos_datos_punto_reorden(df)
    except:
        pass
    
    try:
        df = corregir_nombres_bodega_origen(df)
    except:
        pass
    
    try:
        df = limpiar_atipicos_costo_unitario(df, 'Mediana')
    except:
        pass
    
    try:
        df = imputar_valores_columna_categoria(df, 'Mediana')
    except:
        pass
    
    try:
        df = limpiezar_fecha_ultima_revision(df)
    except:
        pass
    
    return df


def limpiar_feedback(df):
    """Aplica todas las funciones de limpieza para datos de Feedback"""
    df = df.copy()
    print("Manejando outliers en Rating_Producto...")
    try:
        df = manejar_outliers_rating_producto(df, 'Mediana')
    except:
        pass
    print("Manejando outliers en Edad_Cliente...")
    try:
        df = manejar_outliers_edad_cliente(df, 'Mediana')
    except:
        pass
    print("Imputando valores en Comentario_Texto...")
    try:
        df = imputar_valores_comentario_texto(df)
    except:
        print("Error imputando Comentario_Texto")
        pass
    print("Imputando valores en Recomienda_Marca...")
    try:
        df = imputar_valores_recomienda_marca(df)
    except:
        pass
    
    return df


def limpiar_transacciones(df):
    """Aplica todas las funciones de limpieza para datos de Transacciones"""
    df = df.copy()
    
    try:
        df = corregir_nombres_ciudad_destino(df)
    except:
        pass
    
    try:
        df = corregir_canal_venta(df)
    except:
        pass
    
    try:
        df = corregir_valores_negativos_cantidad_vendida(df)
    except:
        pass
    
    try:
        df = reemplazar_outliers_tiempo_entrega_real(df, 'Mediana')
    except:
        pass
    
    try:
        df = imputar_costo_envio(df, 'Mediana')
    except:
        pass
    
    try:
        df = imputar_estado_envio(df, 'Moda')
    except:
        pass
    
    return df
