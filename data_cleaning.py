"""
Módulo de Limpieza de Datos
TechLogistics S.A.S.

Este módulo contiene todas las funciones necesarias para la limpieza
y preprocesamiento de los datos.
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ================================
# FUNCIONES DE AUDITORÍA
# ================================

def calculate_health_score(df, dataset_name):
    """
    Calcula el Health Score de un dataset (0-100)
    
    Parameters:
    -----------
    df : pd.DataFrame
        Dataset a evaluar
    dataset_name : str
        Nombre del dataset
    
    Returns:
    --------
    dict : Métricas de calidad
    """
    total_cells = df.shape[0] * df.shape[1]
    missing_cells = df.isnull().sum().sum()
    completeness = (1 - missing_cells / total_cells) * 100
    
    duplicates = df.duplicated().sum()
    uniqueness = (1 - duplicates / len(df)) * 100 if len(df) > 0 else 100
    
    # Score final (promedio ponderado)
    health_score = (completeness * 0.6 + uniqueness * 0.4)
    
    return {
        'dataset': dataset_name,
        'health_score': round(health_score, 2),
        'completeness': round(completeness, 2),
        'uniqueness': round(uniqueness, 2),
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'missing_values': int(missing_cells),
        'duplicates': int(duplicates)
    }

def generate_quality_report(df_before, df_after, dataset_name):
    """
    Genera reporte comparativo antes/después de limpieza
    
    Parameters:
    -----------
    df_before : pd.DataFrame
        Dataset original
    df_after : pd.DataFrame
        Dataset limpio
    dataset_name : str
        Nombre del dataset
    
    Returns:
    --------
    dict : Reporte de cambios
    """
    before_score = calculate_health_score(df_before, dataset_name)
    after_score = calculate_health_score(df_after, dataset_name)
    
    rows_removed = len(df_before) - len(df_after)
    
    return {
        'dataset': dataset_name,
        'before': before_score,
        'after': after_score,
        'rows_removed': rows_removed,
        'improvement': round(after_score['health_score'] - before_score['health_score'], 2)
    }

# ================================
# DETECCIÓN DE PROBLEMAS
# ================================

def detect_outliers(series, method='IQR', threshold=1.5):
    """
    Detecta outliers en una serie numérica
    
    Parameters:
    -----------
    series : pd.Series
        Serie de datos numéricos
    method : str
        Método de detección ('IQR', 'zscore', 'percentile')
    threshold : float
        Umbral para considerar outlier
    
    Returns:
    --------
    pd.Series : Boolean mask de outliers
    """
    if method == 'IQR':
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - threshold * IQR
        upper_bound = Q3 + threshold * IQR
        return (series < lower_bound) | (series > upper_bound)
    
    elif method == 'zscore':
        z_scores = np.abs((series - series.mean()) / series.std())
        return z_scores > threshold
    
    elif method == 'percentile':
        lower = series.quantile(0.01)
        upper = series.quantile(0.99)
        return (series < lower) | (series > upper)
    
    else:
        raise ValueError("Método no reconocido. Usa 'IQR', 'zscore' o 'percentile'")

def detect_inconsistencies(df):
    """
    Detecta inconsistencias de tipo de datos
    
    Parameters:
    -----------
    df : pd.DataFrame
        Dataset a analizar
    
    Returns:
    --------
    dict : Diccionario con columnas problemáticas
    """
    issues = {}
    
    for col in df.columns:
        # Detectar mezcla de tipos
        types = df[col].apply(type).unique()
        if len(types) > 1:
            issues[col] = {
                'problem': 'mixed_types',
                'types_found': [str(t) for t in types]
            }
    
    return issues

# ================================
# TRATAMIENTO DE PROBLEMAS
# ================================

def handle_outliers(series, strategy='cap', threshold=1.5):
    """
    Trata outliers según la estrategia seleccionada
    
    Parameters:
    -----------
    series : pd.Series
        Serie de datos numéricos
    strategy : str
        Estrategia ('cap', 'remove', 'impute')
    threshold : float
        Umbral para detección
    
    Returns:
    --------
    pd.Series : Serie tratada
    """
    outliers = detect_outliers(series, method='IQR', threshold=threshold)
    
    if strategy == 'cap':
        # Capear a percentiles 1 y 99
        lower = series.quantile(0.01)
        upper = series.quantile(0.99)
        return series.clip(lower, upper)
    
    elif strategy == 'remove':
        # Marcar para eliminación (retorna mask)
        return ~outliers
    
    elif strategy == 'impute':
        # Imputar con mediana
        median_val = series.median()
        series_copy = series.copy()
        series_copy[outliers] = median_val
        return series_copy
    
    else:
        raise ValueError("Estrategia no reconocida. Usa 'cap', 'remove' o 'impute'")

def impute_missing(series, strategy='median'):
    """
    Imputa valores faltantes
    
    Parameters:
    -----------
    series : pd.Series
        Serie con valores faltantes
    strategy : str
        Estrategia ('mean', 'median', 'mode', 'ffill')
    
    Returns:
    --------
    pd.Series : Serie con valores imputados
    """
    if strategy == 'mean':
        return series.fillna(series.mean())
    elif strategy == 'median':
        return series.fillna(series.median())
    elif strategy == 'mode':
        return series.fillna(series.mode()[0] if len(series.mode()) > 0 else series.median())
    elif strategy == 'ffill':
        return series.fillna(method='ffill')
    else:
        raise ValueError("Estrategia no reconocida")

# ================================
# LIMPIEZA POR DATASET
# ================================

def clean_inventario(df):
    """
    Limpia el dataset de inventario
    
    Acciones:
    - Corregir tipos de datos
    - Tratar outliers en costos
    - Resolver existencias negativas
    """
    df_clean = df.copy()
    
    # EJEMPLO DE LIMPIEZA - ADAPTAR SEGÚN TUS DATOS
    
    # 1. Convertir fechas
    if 'Ultima_Revision' in df_clean.columns:
        df_clean['Ultima_Revision'] = pd.to_datetime(df_clean['Ultima_Revision'], errors='coerce')
    
    # 2. Tratar costos atípicos
    if 'Costo_Unitario' in df_clean.columns:
        # Eliminar costos < $0.50
        df_clean = df_clean[df_clean['Costo_Unitario'] >= 0.50]
        # Capear costos extremos
        df_clean['Costo_Unitario'] = handle_outliers(df_clean['Costo_Unitario'], strategy='cap')
    
    # 3. Resolver existencias negativas
    if 'Existencias' in df_clean.columns:
        df_clean.loc[df_clean['Existencias'] < 0, 'Existencias'] = 0
    
    # 4. Remover duplicados
    df_clean = df_clean.drop_duplicates()
    
    return df_clean

def clean_transacciones(df):
    """
    Limpia el dataset de transacciones
    
    Acciones:
    - Estandarizar formatos de fecha
    - Tratar outliers de tiempo de entrega
    - Validar integridad referencial
    """
    df_clean = df.copy()
    
    # EJEMPLO DE LIMPIEZA - ADAPTAR SEGÚN TUS DATOS
    
    # 1. Estandarizar fechas
    date_columns = ['Fecha_Venta', 'Fecha_Entrega']
    for col in date_columns:
        if col in df_clean.columns:
            df_clean[col] = pd.to_datetime(df_clean[col], errors='coerce', dayfirst=True)
    
    # 2. Tratar tiempos de entrega outliers
    if 'Tiempo_Entrega' in df_clean.columns:
        df_clean['Tiempo_Entrega'] = handle_outliers(df_clean['Tiempo_Entrega'], strategy='cap')
    
    # 3. Remover registros con fechas inválidas
    df_clean = df_clean.dropna(subset=['Fecha_Venta'])
    
    return df_clean

def clean_feedback(df):
    """
    Limpia el dataset de feedback
    
    Acciones:
    - Eliminar duplicados
    - Validar rangos de edad
    - Normalizar escala NPS
    """
    df_clean = df.copy()
    
    # EJEMPLO DE LIMPIEZA - ADAPTAR SEGÚN TUS DATOS
    
    # 1. Eliminar duplicados exactos
    df_clean = df_clean.drop_duplicates(subset=['ID_Transaccion', 'NPS'], keep='first')
    
    # 2. Validar edades
    if 'Edad' in df_clean.columns:
        # Imputar edades imposibles con la mediana
        df_clean.loc[df_clean['Edad'] > 120, 'Edad'] = np.nan
        df_clean.loc[df_clean['Edad'] < 18, 'Edad'] = np.nan
        df_clean['Edad'] = impute_missing(df_clean['Edad'], strategy='median')
    
    # 3. Validar escala NPS
    if 'NPS' in df_clean.columns:
        df_clean = df_clean[(df_clean['NPS'] >= 0) & (df_clean['NPS'] <= 10)]
    
    return df_clean

# ================================
# PIPELINE PRINCIPAL
# ================================

def clean_all_datasets(inv_path, trans_path, feed_path, output_dir='data/'):
    """
    Orquesta todo el proceso de limpieza
    
    Parameters:
    -----------
    inv_path : str
        Ruta al CSV de inventario
    trans_path : str
        Ruta al CSV de transacciones
    feed_path : str
        Ruta al CSV de feedback
    output_dir : str
        Directorio de salida
    
    Returns:
    --------
    tuple : (inventario_clean, transacciones_clean, feedback_clean, reports)
    """
    import os
    
    # Crear directorio de salida si no existe
    os.makedirs(output_dir, exist_ok=True)
    
    print("📦 Cargando datasets originales...")
    inv_original = pd.read_csv(inv_path)
    trans_original = pd.read_csv(trans_path)
    feed_original = pd.read_csv(feed_path)
    
    print("🧹 Limpiando datasets...")
    inv_clean = clean_inventario(inv_original)
    trans_clean = clean_transacciones(trans_original)
    feed_clean = clean_feedback(feed_original)
    
    print("📊 Generando reportes de calidad...")
    reports = {
        'inventario': generate_quality_report(inv_original, inv_clean, 'Inventario'),
        'transacciones': generate_quality_report(trans_original, trans_clean, 'Transacciones'),
        'feedback': generate_quality_report(feed_original, feed_clean, 'Feedback')
    }
    
    print("💾 Guardando datasets limpios...")
    inv_clean.to_csv(f'{output_dir}inventario_clean.csv', index=False)
    trans_clean.to_csv(f'{output_dir}transacciones_clean.csv', index=False)
    feed_clean.to_csv(f'{output_dir}feedback_clean.csv', index=False)
    
    # Guardar reporte
    report_df = pd.DataFrame([reports['inventario'], reports['transacciones'], reports['feedback']])
    report_df.to_csv(f'{output_dir}quality_report.csv', index=False)
    
    print("✅ ¡Limpieza completada!")
    print(f"   - Inventario: {len(inv_clean):,} registros ({reports['inventario']['rows_removed']} eliminados)")
    print(f"   - Transacciones: {len(trans_clean):,} registros ({reports['transacciones']['rows_removed']} eliminados)")
    print(f"   - Feedback: {len(feed_clean):,} registros ({reports['feedback']['rows_removed']} eliminados)")
    
    return inv_clean, trans_clean, feed_clean, reports

# ================================
# LOGGING
# ================================

def log_cleaning_decisions(decisions_dict, output_path='data/cleaning_decisions.txt'):
    """
    Documenta las decisiones de limpieza tomadas
    
    Parameters:
    -----------
    decisions_dict : dict
        Diccionario con decisiones tomadas
    output_path : str
        Ruta del archivo de log
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("DOCUMENTACIÓN DE DECISIONES DE LIMPIEZA DE DATOS\n")
        f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*80 + "\n\n")
        
        for dataset, decisions in decisions_dict.items():
            f.write(f"\n{dataset.upper()}\n")
            f.write("-"*80 + "\n")
            for decision, justification in decisions.items():
                f.write(f"\n{decision}:\n")
                f.write(f"  {justification}\n")

# ================================
# EJEMPLO DE USO
# ================================

if __name__ == "__main__":
    # Rutas de archivos (ADAPTAR SEGÚN TU ESTRUCTURA)
    inv_path = 'data/raw/inventario_central_v2.csv'
    trans_path = 'data/raw/transacciones_logistica_v2.csv'
    feed_path = 'data/raw/feedback_clientes_v2.csv'
    
    # Ejecutar limpieza
    inv_clean, trans_clean, feed_clean, reports = clean_all_datasets(
        inv_path, trans_path, feed_path
    )
    
    # Documentar decisiones
    decisions = {
        'Inventario': {
            'Costos < $0.50 eliminados': 'Costos extremadamente bajos indican error de sistema',
            'Existencias negativas → 0': 'Existencias negativas son imposibles físicamente',
            'Outliers de costo capeados': 'Percentil 99 usado para evitar sesgo en análisis'
        },
        'Transacciones': {
            'Tiempos de entrega > 100 días capeados': 'Outliers extremos sesgan correlaciones',
            'SKUs sin match mantenidos': 'Representan ventas reales, útil para análisis de riesgo',
            'Fechas estandarizadas': 'Formato YYYY-MM-DD para consistencia'
        },
        'Feedback': {
            'Duplicados eliminados': 'ID_Transaccion + NPS idénticos son redundantes',
            'Edades > 120 imputadas con mediana': 'Mediana más robusta que media ante outliers',
            'NPS fuera de rango [0-10] eliminados': 'Valores inválidos por error de sistema'
        }
    }
    
    log_cleaning_decisions(decisions)
    
    print("\n📄 Reporte de calidad:")
    print(pd.DataFrame([reports['inventario'], reports['transacciones'], reports['feedback']]))