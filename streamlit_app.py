"""
TechLogistics S.A.S. - Sistema de Soporte a la Decisión (DSS)
Dashboard Streamlit para Análisis de Datos
Autor: [Tu Nombre]
Universidad EAFIT - 2026-1
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ================================
# CONFIGURACIÓN DE PÁGINA
# ================================
st.set_page_config(
    page_title="TechLogistics DSS",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================================
# ESTILOS CSS PERSONALIZADOS
# ================================
st.markdown("""
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
    """, unsafe_allow_html=True)

# ================================
# FUNCIONES DE CARGA DE DATOS
# ================================
def load_uploaded_file(uploaded_file):
    """
    Carga un archivo CSV subido por el usuario
    """
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            return df
        except Exception as e:
            st.error(f"Error al cargar el archivo: {e}")
            return None
    return None

def process_dates(df, date_columns):
    """
    Convierte columnas de fecha al formato datetime
    """
    df_copy = df.copy()
    for col in date_columns:
        if col in df_copy.columns:
            df_copy[col] = pd.to_datetime(df_copy[col], errors='coerce')
    return df_copy

# ================================
# FUNCIONES DE ANÁLISIS
# ================================
def calculate_health_score(df, dataset_name):
    """Calcula el Health Score de un dataset (0-100)"""
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

def create_health_gauge(score, title):
    """Crea un gráfico de velocímetro para el Health Score"""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': title, 'font': {'size': 20}},
        delta = {'reference': 90},
        gauge = {
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
# HEADER
# ================================
st.markdown('<div class="main-header">🚀 TechLogistics S.A.S. - Sistema de Soporte a la Decisión</div>', unsafe_allow_html=True)

# ================================
# SECCIÓN DE CARGA DE ARCHIVOS
# ================================
st.markdown('<div class="upload-section">', unsafe_allow_html=True)
st.header("📂 Carga de Datos")

st.markdown("""
**Instrucciones:** Sube tus archivos CSV limpios en el siguiente orden. 
Los archivos deben contener las columnas esperadas para el análisis.
""")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("📦 Inventario")
    inventario_file = st.file_uploader(
        "Sube el archivo de inventario",
        type=['csv'],
        key='inventario',
        help="Debe contener columnas como: SKU, Categoria, Existencias, Costo_Unitario, etc."
    )

with col2:
    st.subheader("🚚 Transacciones")
    transacciones_file = st.file_uploader(
        "Sube el archivo de transacciones",
        type=['csv'],
        key='transacciones',
        help="Debe contener columnas como: ID_Transaccion, SKU, Fecha_Venta, Precio_Venta, etc."
    )

with col3:
    st.subheader("💬 Feedback")
    feedback_file = st.file_uploader(
        "Sube el archivo de feedback",
        type=['csv'],
        key='feedback',
        help="Debe contener columnas como: ID_Transaccion, NPS, Comentarios, etc."
    )

st.markdown('</div>', unsafe_allow_html=True)

# Cargar los archivos
inventario = load_uploaded_file(inventario_file)
transacciones = load_uploaded_file(transacciones_file)
feedback = load_uploaded_file(feedback_file)

# Verificar que al menos un archivo fue cargado
if inventario is None and transacciones is None and feedback is None:
    st.warning("⚠️ Por favor, sube al menos un archivo CSV para comenzar el análisis.")
    st.stop()

# Procesar fechas si los archivos fueron cargados
if inventario is not None:
    inventario = process_dates(inventario, ['Ultima_Revision', 'Fecha_Registro'])
    st.success(f"✅ Inventario cargado: {len(inventario)} registros")

if transacciones is not None:
    transacciones = process_dates(transacciones, ['Fecha_Venta', 'Fecha_Entrega'])
    st.success(f"✅ Transacciones cargadas: {len(transacciones)} registros")

if feedback is not None:
    feedback = process_dates(feedback, ['Fecha_Feedback'])
    st.success(f"✅ Feedback cargado: {len(feedback)} registros")

st.markdown("---")

# Crear dataset integrado si hay datos disponibles
main_data = None

if transacciones is not None and inventario is not None and feedback is not None:
    # Merge completo
    main_data = transacciones.merge(inventario, on='SKU', how='left', suffixes=('', '_inv'))
    main_data = main_data.merge(feedback, on='ID_Transaccion', how='left', suffixes=('', '_feed'))
    st.info(f"📊 Dataset integrado creado: {len(main_data)} registros")
elif transacciones is not None and inventario is not None:
    # Merge parcial (sin feedback)
    main_data = transacciones.merge(inventario, on='SKU', how='left', suffixes=('', '_inv'))
    st.info(f"📊 Dataset integrado creado (sin feedback): {len(main_data)} registros")
elif transacciones is not None:
    # Solo transacciones
    main_data = transacciones
    st.info(f"📊 Usando solo datos de transacciones: {len(main_data)} registros")
elif inventario is not None:
    # Solo inventario
    main_data = inventario
    st.info(f"📊 Usando solo datos de inventario: {len(main_data)} registros")

# Si no hay datos integrados, usar el primer archivo disponible
if main_data is None:
    if feedback is not None:
        main_data = feedback
        st.info(f"📊 Usando solo datos de feedback: {len(main_data)} registros")

# ================================
# SIDEBAR
# ================================
with st.sidebar:
    st.image("https://via.placeholder.com/200x80/1E2761/FFFFFF?text=TechLogistics", use_container_width=True)
    st.markdown("---")
    
    st.header("🎛️ Filtros Globales")
    
    # Filtro de fechas
    if 'Fecha_Venta' in main_data.columns:
        date_min = main_data['Fecha_Venta'].min()
        date_max = main_data['Fecha_Venta'].max()
        
        if pd.notna(date_min) and pd.notna(date_max):
            date_range = st.date_input(
                "Rango de Fechas",
                value=(date_min, date_max),
                min_value=date_min,
                max_value=date_max
            )
        else:
            date_range = None
    else:
        date_range = None
    
    # Filtro de Categorías
    if 'Categoria' in main_data.columns:
        categorias = st.multiselect(
            "Categorías",
            options=sorted(main_data['Categoria'].dropna().unique()),
            default=None
        )
    else:
        categorias = None
    
    # Filtro de Ciudades
    if 'Ciudad' in main_data.columns:
        ciudades = st.multiselect(
            "Ciudades",
            options=sorted(main_data['Ciudad'].dropna().unique()),
            default=None
        )
    else:
        ciudades = None
    
    # Filtro de Canal
    if 'Canal' in main_data.columns:
        canal = st.multiselect(
            "Canal de Venta",
            options=sorted(main_data['Canal'].dropna().unique()),
            default=None
        )
    else:
        canal = None
    
    # Filtro de Bodegas
    if 'Bodega' in main_data.columns:
        bodegas = st.multiselect(
            "Bodegas",
            options=sorted(main_data['Bodega'].dropna().unique()),
            default=None
        )
    else:
        bodegas = None
    
    st.markdown("---")
    
    # Botón de descarga
    st.subheader("📥 Descargas")
    
    # Crear un reporte de calidad
    quality_data = []
    if inventario is not None:
        quality_data.append(calculate_health_score(inventario, 'Inventario'))
    if transacciones is not None:
        quality_data.append(calculate_health_score(transacciones, 'Transacciones'))
    if feedback is not None:
        quality_data.append(calculate_health_score(feedback, 'Feedback'))
    
    if quality_data:
        quality_report = pd.DataFrame(quality_data)
        
        csv_quality = quality_report.to_csv(index=False).encode('utf-8')
        
        st.download_button(
            label="📊 Reporte de Calidad",
            data=csv_quality,
            file_name=f"reporte_calidad_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    
    # Aplicar filtros
    filters = {}
    if categorias:
        filters['Categoria'] = categorias
    if ciudades:
        filters['Ciudad'] = ciudades
    if canal:
        filters['Canal'] = canal
    if bodegas:
        filters['Bodega'] = bodegas
    
    filtered_data = filter_data(main_data, filters)
    
    if 'Fecha_Venta' in filtered_data.columns and date_range is not None and len(date_range) == 2:
        filtered_data = filtered_data[
            (filtered_data['Fecha_Venta'] >= pd.to_datetime(date_range[0])) &
            (filtered_data['Fecha_Venta'] <= pd.to_datetime(date_range[1]))
        ]
    
    csv_filtered = filtered_data.to_csv(index=False).encode('utf-8')
    
    st.download_button(
        label="📁 Datos Filtrados",
        data=csv_filtered,
        file_name=f"datos_filtrados_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )
    
    st.markdown("---")
    st.caption(f"📅 Última actualización: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    st.caption(f"📊 Registros filtrados: {len(filtered_data):,} de {len(main_data):,}")

# ================================
# TABS PRINCIPALES
# ================================
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Auditoría de Calidad",
    "🔍 Exploración de Datos",
    "💰 Análisis Estratégico",
    "🤖 Recomendaciones IA"
])

# ================================
# TAB 1: AUDITORÍA DE CALIDAD
# ================================
with tab1:
    st.header("📊 Auditoría de Calidad de Datos")
    
    st.markdown("""
    Esta sección presenta el **Health Score** de cada dataset, calculado en base a:
    - **Completitud**: Porcentaje de datos sin valores nulos
    - **Unicidad**: Porcentaje de registros únicos (sin duplicados)
    """)
    
    # KPIs de calidad
    cols = []
    health_scores = []
    
    if inventario is not None:
        cols.append(st.columns(3)[0] if len(cols) == 0 else st.columns(3)[len(cols)])
        health_scores.append(calculate_health_score(inventario, 'Inventario'))
    
    if transacciones is not None:
        if len(cols) == 0:
            cols = st.columns(3)
        health_scores.append(calculate_health_score(transacciones, 'Transacciones'))
    
    if feedback is not None:
        if len(cols) == 0:
            cols = st.columns(3)
        health_scores.append(calculate_health_score(feedback, 'Feedback'))
    
    # Mostrar KPIs
    col_layout = st.columns(len(health_scores))
    
    for idx, health in enumerate(health_scores):
        with col_layout[idx]:
            st.markdown('<div class="kpi-container">', unsafe_allow_html=True)
            icon = "📦" if health['dataset'] == 'Inventario' else "🚚" if health['dataset'] == 'Transacciones' else "💬"
            st.metric(
                label=f"{icon} {health['dataset']}",
                value=f"{health['health_score']}%",
                delta=f"{health['total_rows']:,} registros"
            )
            st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Gráficos de velocímetro
    st.subheader("🎯 Health Score por Dataset")
    
    gauge_cols = st.columns(len(health_scores))
    
    for idx, health in enumerate(health_scores):
        with gauge_cols[idx]:
            fig = create_health_gauge(health['health_score'], health['dataset'])
            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Tabla detallada de métricas
    st.subheader("📋 Métricas Detalladas de Calidad")
    
    if health_scores:
        metrics_df = pd.DataFrame(health_scores)
        metrics_df = metrics_df[[
            'dataset', 'health_score', 'completeness', 'uniqueness',
            'total_rows', 'missing_values', 'duplicates'
        ]]
        metrics_df.columns = [
            'Dataset', 'Health Score (%)', 'Completitud (%)', 'Unicidad (%)',
            'Total Registros', 'Valores Faltantes', 'Duplicados'
        ]
        
        st.dataframe(metrics_df, use_container_width=True, hide_index=True)
    
    # Análisis de nulidad por columna
    st.markdown("---")
    st.subheader("🔍 Análisis de Valores Faltantes por Columna")
    
    available_datasets = []
    if inventario is not None:
        available_datasets.append("Inventario")
    if transacciones is not None:
        available_datasets.append("Transacciones")
    if feedback is not None:
        available_datasets.append("Feedback")
    
    if available_datasets:
        dataset_choice = st.selectbox(
            "Selecciona el dataset a analizar:",
            available_datasets
        )
        
        if dataset_choice == "Inventario":
            df_analysis = inventario
        elif dataset_choice == "Transacciones":
            df_analysis = transacciones
        else:
            df_analysis = feedback
        
        # Calcular porcentaje de nulos por columna
        null_percent = (df_analysis.isnull().sum() / len(df_analysis) * 100).sort_values(ascending=False)
        null_percent = null_percent[null_percent > 0]  # Solo columnas con nulos
        
        if len(null_percent) > 0:
            fig_null = px.bar(
                x=null_percent.values,
                y=null_percent.index,
                orientation='h',
                labels={'x': 'Porcentaje de Valores Faltantes (%)', 'y': 'Columna'},
                title=f"Valores Faltantes en {dataset_choice}",
                color=null_percent.values,
                color_continuous_scale='Reds'
            )
            fig_null.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig_null, use_container_width=True)
        else:
            st.success(f"✅ ¡Excelente! El dataset {dataset_choice} no tiene valores faltantes.")
    
    # Decisiones de limpieza documentadas
    st.markdown("---")
    st.subheader("📝 Decisiones de Limpieza Documentadas")
    
    st.markdown("""
    <div class="insight-box">
    <strong>💡 Instrucciones de Uso:</strong><br>
    En esta sección, documenta las decisiones que tomaste durante el proceso de limpieza:
    <ul>
        <li>¿Qué registros decidiste eliminar y por qué?</li>
        <li>¿Qué valores imputaste (media, mediana, moda)?</li>
        <li>¿Cómo trataste los outliers?</li>
        <li>¿Qué decisión tomaste con los SKUs fantasma?</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("📄 Ver Plantilla de Documentación"):
        st.markdown("""
        ### Decisiones de Limpieza - [Nombre del Dataset]
        
        **1. Valores Atípicos:**
        - **Detección:** [Descripción de cómo detectaste los outliers]
        - **Decisión:** [Qué hiciste con ellos: eliminar, cap ear, mantener]
        - **Justificación:** [Por qué tomaste esa decisión]
        
        **2. Valores Faltantes:**
        - **Columnas afectadas:** [Lista de columnas]
        - **Decisión:** [Imputación, eliminación, etc.]
        - **Método:** [Media, mediana, moda, forward fill, etc.]
        - **Justificación:** [Por qué elegiste ese método]
        
        **3. Duplicados:**
        - **Cantidad detectada:** [Número]
        - **Criterio:** [Qué columnas usaste para identificarlos]
        - **Decisión:** [Eliminar, mantener]
        
        **4. Transformaciones:**
        - **Variables creadas:** [Lista de nuevas columnas]
        - **Fórmulas aplicadas:** [Ej: Margen = (Precio - Costo) / Precio * 100]
        - **Propósito:** [Para qué análisis se usarán]
        
        **5. Resultado Final:**
        - **Registros originales:** [Número]
        - **Registros finales:** [Número]
        - **Tasa de retención:** [Porcentaje]
        """)

# ================================
# TAB 2: EXPLORACIÓN DE DATOS
# ================================
with tab2:
    st.header("🔍 Exploración de Datos")
    
    # Estadísticas descriptivas
    st.subheader("📈 Estadísticas Descriptivas")
    
    available_datasets_eda = ["Datos Filtrados"]
    if inventario is not None:
        available_datasets_eda.append("Inventario")
    if transacciones is not None:
        available_datasets_eda.append("Transacciones")
    if feedback is not None:
        available_datasets_eda.append("Feedback")
    
    dataset_eda = st.selectbox(
        "Selecciona el dataset para análisis:",
        available_datasets_eda,
        key="eda_dataset"
    )
    
    if dataset_eda == "Datos Filtrados":
        df_eda = filtered_data
    elif dataset_eda == "Inventario":
        df_eda = inventario
    elif dataset_eda == "Transacciones":
        df_eda = transacciones
    else:
        df_eda = feedback
    
    # Mostrar estadísticas
    st.write(f"**Dimensiones:** {df_eda.shape[0]} filas × {df_eda.shape[1]} columnas")
    
    # Tabs para diferentes tipos de variables
    stat_tab1, stat_tab2 = st.tabs(["Variables Numéricas", "Variables Categóricas"])
    
    with stat_tab1:
        numeric_cols = df_eda.select_dtypes(include=[np.number]).columns.tolist()
        if numeric_cols:
            st.dataframe(df_eda[numeric_cols].describe(), use_container_width=True)
        else:
            st.info("No hay variables numéricas en este dataset.")
    
    with stat_tab2:
        categorical_cols = df_eda.select_dtypes(include=['object']).columns.tolist()
        if categorical_cols:
            cat_summary = pd.DataFrame({
                'Columna': categorical_cols,
                'Valores Únicos': [df_eda[col].nunique() for col in categorical_cols],
                'Valor Más Frecuente': [df_eda[col].mode()[0] if len(df_eda[col].mode()) > 0 else 'N/A' for col in categorical_cols],
                'Frecuencia': [df_eda[col].value_counts().iloc[0] if len(df_eda[col]) > 0 else 0 for col in categorical_cols]
            })
            st.dataframe(cat_summary, use_container_width=True, hide_index=True)
        else:
            st.info("No hay variables categóricas en este dataset.")
    
    st.markdown("---")
    
    # Distribuciones
    st.subheader("📊 Distribuciones de Variables")
    
    col1, col2 = st.columns([2, 1])
    
    with col2:
        var_type = st.radio("Tipo de variable:", ["Numérica", "Categórica"])
        
        if var_type == "Numérica":
            available_vars = df_eda.select_dtypes(include=[np.number]).columns.tolist()
        else:
            available_vars = df_eda.select_dtypes(include=['object']).columns.tolist()
        
        if available_vars:
            selected_var = st.selectbox("Selecciona variable:", available_vars)
            
            if var_type == "Numérica":
                chart_type = st.radio("Tipo de gráfico:", ["Histograma", "Box Plot", "Violin Plot"])
    
    with col1:
        if available_vars:
            if var_type == "Numérica":
                if chart_type == "Histograma":
                    fig = px.histogram(
                        df_eda,
                        x=selected_var,
                        nbins=30,
                        title=f"Distribución de {selected_var}",
                        color_discrete_sequence=['#1E2761']
                    )
                    fig.update_layout(showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)
                
                elif chart_type == "Box Plot":
                    fig = px.box(
                        df_eda,
                        y=selected_var,
                        title=f"Box Plot de {selected_var}",
                        color_discrete_sequence=['#1E2761']
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                else:  # Violin Plot
                    fig = px.violin(
                        df_eda,
                        y=selected_var,
                        box=True,
                        title=f"Violin Plot de {selected_var}",
                        color_discrete_sequence=['#CADCFC']
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            else:  # Categórica
                value_counts = df_eda[selected_var].value_counts().head(15)
                fig = px.bar(
                    x=value_counts.index,
                    y=value_counts.values,
                    title=f"Distribución de {selected_var} (Top 15)",
                    labels={'x': selected_var, 'y': 'Frecuencia'},
                    color=value_counts.values,
                    color_continuous_scale='Blues'
                )
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(f"No hay variables {var_type.lower()}s disponibles en este dataset.")
    
    st.markdown("---")
    
    # Matriz de correlación
    st.subheader("🔗 Análisis de Correlaciones")
    
    numeric_cols = df_eda.select_dtypes(include=[np.number]).columns.tolist()
    
    if len(numeric_cols) >= 2:
        selected_cols = st.multiselect(
            "Selecciona variables para la matriz de correlación:",
            numeric_cols,
            default=numeric_cols[:min(6, len(numeric_cols))]
        )
        
        if len(selected_cols) >= 2:
            corr_matrix = df_eda[selected_cols].corr()
            
            fig = px.imshow(
                corr_matrix,
                text_auto='.2f',
                aspect='auto',
                color_continuous_scale='RdBu_r',
                title="Matriz de Correlación"
            )
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
            
            # Insights de correlaciones fuertes
            st.markdown("**🔍 Correlaciones más Fuertes:**")
            
            # Obtener pares de correlaciones
            corr_pairs = []
            for i in range(len(corr_matrix.columns)):
                for j in range(i+1, len(corr_matrix.columns)):
                    corr_pairs.append({
                        'Variable 1': corr_matrix.columns[i],
                        'Variable 2': corr_matrix.columns[j],
                        'Correlación': corr_matrix.iloc[i, j]
                    })
            
            corr_df = pd.DataFrame(corr_pairs)
            corr_df = corr_df.reindex(corr_df['Correlación'].abs().sort_values(ascending=False).index)
            corr_df = corr_df.head(10)
            
            st.dataframe(corr_df, use_container_width=True, hide_index=True)
    else:
        st.info("Se necesitan al menos 2 variables numéricas para calcular correlaciones.")

# ================================
# TAB 3: ANÁLISIS ESTRATÉGICO
# ================================
with tab3:
    st.header("💰 Análisis Estratégico - Preguntas de Alta Gerencia")
    
    st.markdown("""
    <div class="insight-box">
    <strong>💡 Nota:</strong> Esta sección requiere variables específicas en tus datos.
    Si alguna columna no existe, verás un mensaje de advertencia con las columnas requeridas.
    </div>
    """, unsafe_allow_html=True)
    
    # Sub-tabs para cada pregunta
    q1, q2, q3, q4, q5 = st.tabs([
        "💸 Fuga de Capital",
        "🚚 Crisis Logística",
        "👻 Venta Invisible",
        "😞 Diagnóstico Fidelidad",
        "⚠️ Riesgo Operativo"
    ])
    
    # PREGUNTA 1: Fuga de Capital
    with q1:
        st.subheader("💸 Pregunta 1: Fuga de Capital y Rentabilidad")
        
        st.markdown("""
        **Objetivo:** Localizar SKUs vendidos con margen negativo y determinar si representan 
        una pérdida aceptable por volumen o una falla crítica de precios.
        """)
        
        if 'Margen_Utilidad' in filtered_data.columns:
            # SKUs con margen negativo
            negative_margin = filtered_data[filtered_data['Margen_Utilidad'] < 0].copy()
            
            if len(negative_margin) > 0:
                # KPIs
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        "SKUs con Margen Negativo",
                        f"{negative_margin['SKU'].nunique():,}" if 'SKU' in negative_margin.columns else "N/A",
                        delta=f"{len(negative_margin):,} ventas"
                    )
                
                with col2:
                    if 'Precio_Venta' in negative_margin.columns:
                        total_loss = (negative_margin['Margen_Utilidad'] * negative_margin['Precio_Venta'] / 100).sum()
                        st.metric(
                            "Pérdida Total Estimada",
                            f"${abs(total_loss):,.2f}",
                            delta="Negativo",
                            delta_color="inverse"
                        )
                
                with col3:
                    if 'SKU' in filtered_data.columns:
                        pct_skus = (negative_margin['SKU'].nunique() / filtered_data['SKU'].nunique() * 100)
                        st.metric(
                            "% SKUs Afectados",
                            f"{pct_skus:.1f}%"
                        )
                
                with col4:
                    if 'Canal' in negative_margin.columns and 'Precio_Venta' in negative_margin.columns:
                        online_df = negative_margin[negative_margin['Canal'] == 'Online']
                        if len(online_df) > 0:
                            online_loss = (online_df['Margen_Utilidad'] * online_df['Precio_Venta'] / 100).sum()
                            st.metric(
                                "Pérdida Canal Online",
                                f"${abs(online_loss):,.2f}"
                            )
                
                st.markdown("---")
                
                # Gráfico: Top 10 SKUs con peor margen
                if 'SKU' in negative_margin.columns:
                    st.markdown("**📉 Top 10 SKUs con Peor Margen**")
                    
                    top_worst = negative_margin.groupby('SKU').agg({
                        'Margen_Utilidad': 'mean'
                    }).sort_values('Margen_Utilidad').head(10)
                    
                    fig = px.bar(
                        top_worst.reset_index(),
                        x='SKU',
                        y='Margen_Utilidad',
                        title="SKUs con Peor Margen de Utilidad",
                        color='Margen_Utilidad',
                        color_continuous_scale='Reds',
                        labels={'Margen_Utilidad': 'Margen (%)'}
                    )
                    fig.update_layout(showlegend=False, height=400)
                    st.plotly_chart(fig, use_container_width=True)
                
                # Recomendaciones
                st.markdown("---")
                st.markdown("""
                <div class="warning-box">
                <strong>⚠️ Recomendaciones Críticas:</strong><br><br>
                1. <strong>Revisión Inmediata de Precios:</strong> Ajustar precios de los SKUs con peor margen<br>
                2. <strong>Análisis de Costos:</strong> Verificar si los costos unitarios están correctamente registrados<br>
                3. <strong>Estrategia por Canal:</strong> Revisar política de descuentos por canal<br>
                4. <strong>Decisión de Descatalogación:</strong> Evaluar productos con margen negativo persistente
                </div>
                """, unsafe_allow_html=True)
                
            else:
                st.success("✅ ¡Excelente! No se detectaron SKUs con margen negativo en el período seleccionado.")
        
        else:
            st.warning("""
            ⚠️ **Columnas requeridas no encontradas:**
            - `Margen_Utilidad` (calculada como: (Precio_Venta - Costo_Unitario) / Precio_Venta * 100)
            
            **Tip:** Crea esta columna en tu proceso de limpieza de datos antes de cargar el archivo.
            """)
    
    # PREGUNTA 2: Crisis Logística
    with q2:
        st.subheader("🚚 Pregunta 2: Crisis Logística y Cuellos de Botella")
        
        st.markdown("""
        **Objetivo:** Identificar ciudades y bodegas donde la correlación entre Tiempo de Entrega 
        y NPS bajo es más fuerte.
        """)
        
        required_cols = ['Brecha_Entrega', 'NPS', 'Ciudad', 'Bodega']
        missing_cols = [col for col in required_cols if col not in filtered_data.columns]
        
        if not missing_cols:
            # Análisis por ciudad/bodega
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**📍 Análisis por Ciudad**")
                
                city_corr = filtered_data.groupby('Ciudad').apply(
                    lambda x: x['Brecha_Entrega'].corr(x['NPS']) if len(x) > 5 else np.nan
                ).sort_values()
                
                city_corr = city_corr.dropna().head(10)
                
                if len(city_corr) > 0:
                    fig = px.bar(
                        x=city_corr.values,
                        y=city_corr.index,
                        orientation='h',
                        title="Correlación Brecha de Entrega vs NPS por Ciudad",
                        labels={'x': 'Correlación', 'y': 'Ciudad'},
                        color=city_corr.values,
                        color_continuous_scale='RdYlGn_r'
                    )
                    fig.update_layout(showlegend=False, height=400)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No hay suficientes datos para calcular correlaciones por ciudad.")
            
            with col2:
                st.markdown("**🏭 Análisis por Bodega**")
                
                warehouse_corr = filtered_data.groupby('Bodega').apply(
                    lambda x: x['Brecha_Entrega'].corr(x['NPS']) if len(x) > 5 else np.nan
                ).sort_values()
                
                warehouse_corr = warehouse_corr.dropna().head(10)
                
                if len(warehouse_corr) > 0:
                    fig = px.bar(
                        x=warehouse_corr.values,
                        y=warehouse_corr.index,
                        orientation='h',
                        title="Correlación Brecha de Entrega vs NPS por Bodega",
                        labels={'x': 'Correlación', 'y': 'Bodega'},
                        color=warehouse_corr.values,
                        color_continuous_scale='RdYlGn_r'
                    )
                    fig.update_layout(showlegend=False, height=400)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No hay suficientes datos para calcular correlaciones por bodega.")
            
            # Recomendaciones
            st.markdown("---")
            st.markdown("""
            <div class="warning-box">
            <strong>🚨 Acciones Recomendadas:</strong><br><br>
            <ul>
                <li>Cambio de operador logístico en zonas críticas</li>
                <li>Auditoría de procesos de despacho</li>
                <li>Revisión de promesas de entrega</li>
                <li>Implementación de tracking en tiempo real</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)
        
        else:
            st.warning(f"""
            ⚠️ **Columnas requeridas no encontradas:**
            {', '.join([f'`{col}`' for col in missing_cols])}
            
            **Columnas necesarias para este análisis:**
            - `Brecha_Entrega`: Días de entrega real - Lead time prometido
            - `NPS`: Puntuación de satisfacción (0-10)
            - `Ciudad`: Ciudad de entrega
            - `Bodega`: Bodega de origen
            """)
    
    # PREGUNTA 3: Venta Invisible
    with q3:
        st.subheader("👻 Pregunta 3: Análisis de la Venta Invisible")
        
        st.markdown("""
        **Objetivo:** Cuantificar el impacto financiero de las ventas cuyos SKUs no están 
        en el maestro de inventario.
        """)
        
        if 'SKU_No_Match' in filtered_data.columns:
            invisible_sales = filtered_data[filtered_data['SKU_No_Match'] == True]
            total_sales = filtered_data
            
            # KPIs
            col1, col2, col3 = st.columns(3)
            
            with col1:
                invisible_count = len(invisible_sales)
                total_count = len(total_sales)
                pct_invisible = (invisible_count / total_count * 100) if total_count > 0 else 0
                
                st.metric(
                    "Ventas Sin Control",
                    f"{invisible_count:,}",
                    delta=f"{pct_invisible:.1f}% del total"
                )
            
            with col2:
                if 'Precio_Venta' in invisible_sales.columns:
                    invisible_revenue = invisible_sales['Precio_Venta'].sum()
                    total_revenue = total_sales['Precio_Venta'].sum()
                    pct_revenue = (invisible_revenue / total_revenue * 100) if total_revenue > 0 else 0
                    
                    st.metric(
                        "Ingresos en Riesgo",
                        f"${invisible_revenue:,.2f}",
                        delta=f"{pct_revenue:.1f}% del total"
                    )
            
            with col3:
                unique_skus = invisible_sales['SKU'].nunique() if 'SKU' in invisible_sales.columns else 0
                st.metric(
                    "SKUs No Catalogados",
                    f"{unique_skus:,}"
                )
            
            # Recomendaciones
            st.markdown("---")
            st.markdown("""
            <div class="warning-box">
            <strong>💰 Acciones Correctivas:</strong><br><br>
            <ul>
                <li>Catalogar urgentemente los SKUs no catalogados con mayor ingreso</li>
                <li>Implementar validación de SKU en punto de venta</li>
                <li>Sincronización diaria entre sistemas</li>
                <li>Dashboard de alertas para SKUs nuevos detectados</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)
        
        else:
            st.warning("""
            ⚠️ **Columnas requeridas no encontradas:**
            - `SKU_No_Match` (Flag booleano: True si el SKU no existe en inventario)
            
            **Tip:** Crea esta columna al hacer el merge entre transacciones e inventario.
            """)
    
    # PREGUNTA 4: Diagnóstico de Fidelidad
    with q4:
        st.subheader("😞 Pregunta 4: Diagnóstico de Fidelidad")
        
        st.markdown("""
        **Objetivo:** Identificar categorías con alta disponibilidad pero sentimiento negativo del cliente.
        """)
        
        required_cols_fid = ['Categoria', 'Existencias', 'NPS']
        missing_cols_fid = [col for col in required_cols_fid if col not in filtered_data.columns]
        
        if not missing_cols_fid:
            # Análisis por categoría
            category_analysis = filtered_data.groupby('Categoria').agg({
                'Existencias': 'mean',
                'NPS': 'mean'
            }).rename(columns={
                'Existencias': 'Stock_Promedio',
                'NPS': 'NPS_Promedio'
            })
            
            # Identificar paradoja: Alto stock + NPS bajo
            category_analysis['Paradoja'] = (
                (category_analysis['Stock_Promedio'] > category_analysis['Stock_Promedio'].median()) &
                (category_analysis['NPS_Promedio'] < 7)
            )
            
            paradox_categories = category_analysis[category_analysis['Paradoja'] == True]
            
            # Gráfico de dispersión
            st.markdown("**📊 Matriz: Stock vs Sentimiento del Cliente**")
            
            fig = px.scatter(
                category_analysis.reset_index(),
                x='Stock_Promedio',
                y='NPS_Promedio',
                color='Paradoja',
                hover_data=['Categoria'],
                title='Análisis de Categorías: Stock vs NPS',
                labels={'Stock_Promedio': 'Stock Promedio', 'NPS_Promedio': 'NPS Promedio'},
                color_discrete_map={True: '#F96167', False: '#97BC62'}
            )
            
            fig.add_hline(y=7, line_dash="dash", line_color="red", annotation_text="NPS Crítico")
            fig.add_vline(x=category_analysis['Stock_Promedio'].median(), line_dash="dash", 
                         line_color="gray", annotation_text="Stock Mediano")
            
            st.plotly_chart(fig, use_container_width=True)
            
            if len(paradox_categories) > 0:
                st.markdown("---")
                st.markdown("**⚠️ Categorías con Paradoja Detectada**")
                st.dataframe(paradox_categories, use_container_width=True)
            else:
                st.success("✅ No se detectaron categorías con la paradoja de alto stock y bajo NPS.")
        
        else:
            st.warning(f"""
            ⚠️ **Columnas requeridas no encontradas:**
            {', '.join([f'`{col}`' for col in missing_cols_fid])}
            
            **Columnas necesarias:**
            - `Categoria`: Categoría del producto
            - `Existencias`: Stock disponible
            - `NPS`: Puntuación de satisfacción
            """)
    
    # PREGUNTA 5: Riesgo Operativo
    with q5:
        st.subheader("⚠️ Pregunta 5: Storytelling de Riesgo Operativo")
        
        st.markdown("""
        **Objetivo:** Visualizar la relación entre antigüedad de última revisión del stock 
        y tasa de tickets de soporte.
        """)
        
        required_cols_risk = ['Edad_Inventario', 'Ratio_Soporte', 'Bodega']
        missing_cols_risk = [col for col in required_cols_risk if col not in filtered_data.columns]
        
        if not missing_cols_risk:
            # Análisis por bodega
            warehouse_risk = filtered_data.groupby('Bodega').agg({
                'Edad_Inventario': 'mean',
                'Ratio_Soporte': 'mean'
            }).rename(columns={
                'Edad_Inventario': 'Dias_Sin_Revision',
                'Ratio_Soporte': 'Tickets_Por_Venta'
            })
            
            warehouse_risk['Critica'] = warehouse_risk['Dias_Sin_Revision'] > 30
            critical_warehouses = warehouse_risk[warehouse_risk['Critica'] == True]
            
            # Gráfico de dispersión
            st.markdown("**📈 Relación: Antigüedad de Revisión vs Tickets de Soporte**")
            
            fig = px.scatter(
                warehouse_risk.reset_index(),
                x='Dias_Sin_Revision',
                y='Tickets_Por_Venta',
                color='Critica',
                hover_data=['Bodega'],
                title='Riesgo Operativo por Bodega',
                labels={
                    'Dias_Sin_Revision': 'Días desde Última Revisión',
                    'Tickets_Por_Venta': 'Ratio Tickets de Soporte'
                },
                color_discrete_map={True: '#F96167', False: '#97BC62'},
                trendline="ols"
            )
            
            fig.add_vline(x=30, line_dash="dash", line_color="red", 
                         annotation_text="Límite Crítico (30 días)")
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Correlación
            correlation = warehouse_risk['Dias_Sin_Revision'].corr(warehouse_risk['Tickets_Por_Venta'])
            
            st.metric("Correlación Detectada", f"{correlation:.3f}")
            
            if len(critical_warehouses) > 0:
                st.markdown("---")
                st.markdown("**🚨 Bodegas Operando 'A Ciegas'**")
                st.dataframe(critical_warehouses, use_container_width=True)
            
            # Recomendaciones
            st.markdown("---")
            st.markdown("""
            <div class="warning-box">
            <strong>🔧 Plan de Mejora Operativa:</strong><br><br>
            1. <strong>Acción Inmediata:</strong> Auditoría física en bodegas críticas<br>
            2. <strong>Mediano Plazo:</strong> Sistema de revisión automática cada 14 días<br>
            3. <strong>Transformación:</strong> Digitalización con RFID o códigos QR
            </div>
            """, unsafe_allow_html=True)
        
        else:
            st.warning(f"""
            ⚠️ **Columnas requeridas no encontradas:**
            {', '.join([f'`{col}`' for col in missing_cols_risk])}
            
            **Columnas necesarias:**
            - `Edad_Inventario`: Días desde última revisión
            - `Ratio_Soporte`: Tickets de soporte / total ventas
            - `Bodega`: Ubicación del inventario
            """)

# ================================
# TAB 4: RECOMENDACIONES IA
# ================================
with tab4:
    st.header("🤖 Recomendaciones de Inteligencia Artificial")
    
    st.markdown("""
    Esta sección está preparada para utilizar **IA Generativa** para analizar los datos 
    y generar recomendaciones estratégicas personalizadas.
    """)
    
    st.markdown("""
    <div class="insight-box">
    <strong>💡 Instrucciones de Integración:</strong><br><br>
    Para habilitar esta funcionalidad, necesitas:
    <ol>
        <li>Obtener una API Key de Groq (https://console.groq.com)</li>
        <li>Instalar: <code>pip install groq python-dotenv</code></li>
        <li>Crear archivo <code>.env</code> con: <code>GROQ_API_KEY=tu_api_key</code></li>
    </ol>
    </div>
    """, unsafe_allow_html=True)
    
    # Selector de análisis
    analysis_type = st.selectbox(
        "Selecciona el tipo de análisis:",
        [
            "Resumen General de Datos Filtrados",
            "Análisis de Rentabilidad",
            "Análisis de Satisfacción del Cliente",
            "Recomendaciones de Optimización Logística",
            "Estrategia de Gestión de Inventario"
        ]
    )
    
    # Área de texto para pregunta personalizada
    custom_query = st.text_area(
        "O escribe tu propia pregunta de negocio:",
        placeholder="Ejemplo: ¿Cuáles son las principales oportunidades de mejora basándote en los datos?"
    )
    
    if st.button("🚀 Generar Análisis con IA", type="primary"):
        st.markdown("---")
        
        with st.spinner("🤖 Analizando datos con IA..."):
            import time
            time.sleep(2)  # Simular procesamiento
            
            st.markdown("""
            <div class="success-box">
            <strong>🤖 Análisis Generado por IA (Ejemplo - Placeholder)</strong><br><br>
            
            <strong>1. DIAGNÓSTICO</strong><br>
            Los datos cargados muestran patrones interesantes en el desempeño del negocio.
            Basándome en los archivos que subiste, puedo identificar áreas clave de mejora
            en rentabilidad, satisfacción del cliente y eficiencia operativa.<br><br>
            
            <strong>2. ANÁLISIS</strong><br>
            Las variables más relevantes para el análisis han sido identificadas.
            Se recomienda prestar especial atención a las correlaciones encontradas
            entre las diferentes dimensiones del negocio.<br><br>
            
            <strong>3. RECOMENDACIONES</strong><br>
            Para implementar la integración con IA real, sigue las instrucciones en el
            expander de abajo.
            </div>
            """, unsafe_allow_html=True)
    
    # Código de integración
    with st.expander("👨‍💻 Ver Código de Integración con Groq"):
        st.code("""
# Instalación
# pip install groq python-dotenv

# Archivo .env
GROQ_API_KEY=tu_api_key_aqui

# Código de integración
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Preparar resumen de datos
data_summary = f'''
Dataset: {len(filtered_data)} registros
Columnas: {', '.join(filtered_data.columns)}

Estadísticas:
{filtered_data.describe().to_string()}
'''

# Prompt
prompt = f'''
Analiza estos datos de TechLogistics y genera recomendaciones:

{data_summary}

Pregunta: {custom_query or analysis_type}

Estructura tu respuesta en 3 partes:
1. DIAGNÓSTICO
2. ANÁLISIS DE CAUSA RAÍZ
3. RECOMENDACIONES ESTRATÉGICAS
'''

# Llamada a API
response = client.chat.completions.create(
    messages=[{"role": "user", "content": prompt}],
    model="llama-3.1-70b-versatile",
    temperature=0.7,
    max_tokens=1500
)

ai_response = response.choices[0].message.content
st.markdown(ai_response)
        """, language="python")

# ================================
# FOOTER
# ================================
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666; padding: 2rem;'>
        <p><strong>TechLogistics S.A.S. - Sistema de Soporte a la Decisión</strong></p>
        <p>Desarrollado por [Tu Nombre] | Universidad EAFIT | Fundamentos en Ciencia de Datos | 2026-1</p>
        <p>📧 Contacto: tu.email@eafit.edu.co</p>
    </div>
    """, unsafe_allow_html=True)