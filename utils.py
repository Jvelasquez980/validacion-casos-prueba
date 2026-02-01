"""
Módulo de Utilidades - TechLogistics DSS
Funciones para carga, procesamiento y análisis de datos
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import streamlit as st


# ================================
# CARGA Y PROCESAMIENTO DE DATOS
# ================================

def load_uploaded_file(uploaded_file):
    """Carga un archivo CSV subido por el usuario"""
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            return df
        except Exception as e:
            st.error(f"Error al cargar el archivo: {e}")
            return None
    return None


def process_dates(df, date_columns):
    """Convierte columnas de fecha al formato datetime"""
    df_copy = df.copy()
    for col in date_columns:
        if col in df_copy.columns:
            df_copy[col] = pd.to_datetime(df_copy[col], errors='coerce')
    return df_copy


def safe_merge(df1, df2, on_col, df1_name, df2_name):
    """Intenta hacer merge si la columna existe en ambos dataframes"""
    if on_col in df1.columns and on_col in df2.columns:
        try:
            result = df1.merge(df2, on=on_col, how='left', suffixes=('', f'_{df2_name.lower()}'))
            st.success(f"✅ Integrado: {df1_name} + {df2_name} usando columna '{on_col}'")
            return result, True
        except Exception as e:
            st.warning(f"⚠️ No se pudo integrar {df1_name} con {df2_name}: {str(e)}")
            return df1, False
    return df1, False


# ================================
# ANÁLISIS Y MÉTRICAS
# ================================

def calculate_health_score(df, dataset_name):
    """Calcula el Health Score de un dataset (0-100)"""
    total_cells = df.shape[0] * df.shape[1]
    missing_cells = df.isnull().sum().sum()
    completeness = (1 - missing_cells / total_cells) * 100
    
    duplicates = df.duplicated().sum()
    uniqueness = (1 - duplicates / len(df)) * 100 if len(df) > 0 else 100
    
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


def create_health_gauge(score, title):
    """Crea un gráfico de velocímetro para el Health Score"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 20}},
        delta={'reference': 90},
        gauge={
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "#1E2761"},
            'bar': {'color': "#1E2761"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "#CADCFC",
            'steps': [
                {'range': [0, 50], 'color': '#F96167'},
                {'range': [50, 75], 'color': '#F9E795'},
                {'range': [75, 100], 'color': '#97BC62'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    
    fig.update_layout(height=300, margin=dict(l=20, r=20, t=60, b=20))
    return fig


def filter_data(df, filters):
    """Aplica filtros dinámicos al dataframe"""
    filtered_df = df.copy()
    
    for column, values in filters.items():
        if column in filtered_df.columns and values:
            filtered_df = filtered_df[filtered_df[column].isin(values)]
    
    return filtered_df


# ================================
# DETECCIÓN AUTOMÁTICA
# ================================

def detect_date_columns(df):
    """Detecta columnas de fecha en el dataframe"""
    return [col for col in df.columns if 'fecha' in col.lower() or 'date' in col.lower()]


def detect_categorical_columns(df, max_unique=50, min_unique=2):
    """Detecta columnas categóricas apropiadas para filtros"""
    categorical_cols = []
    for col in df.select_dtypes(include=['object']).columns:
        unique_count = df[col].nunique()
        if min_unique <= unique_count <= max_unique:
            categorical_cols.append(col)
    return categorical_cols


# ================================
# ESTILOS CSS
# ================================

def get_custom_css():
    """Retorna los estilos CSS personalizados"""
    return """
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E2761;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #CADCFC 0%, #FFFFFF 100%);
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #1E2761;
    }
    .kpi-container {
        background-color: #CADCFC;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
    }
    .insight-box {
        background-color: #FFF9E6;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #F9E795;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #FFE6E6;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #F96167;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #E6F9E6;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #2C5F2D;
        margin: 1rem 0;
    }
    .upload-section {
        background-color: #F0F2F6;
        padding: 2rem;
        border-radius: 10px;
        border: 2px dashed #1E2761;
        margin: 1rem 0;
    }
    </style>
    """