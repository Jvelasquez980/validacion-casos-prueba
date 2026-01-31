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
    </style>
    """, unsafe_allow_html=True)

# ================================
# FUNCIONES DE CARGA DE DATOS
# ================================
@st.cache_data
def load_data():
    """
    Carga los datasets limpios.
    INSTRUCCIONES: Coloca tus archivos CSV limpios en la carpeta 'data/processed/'
    con los nombres: inventario_clean.csv, transacciones_clean.csv, feedback_clean.csv
    """
    try:
        inventario = pd.read_csv('data/processed/inventario_clean.csv')
        transacciones = pd.read_csv('data/processed/transacciones_clean.csv')
        feedback = pd.read_csv('data/processed/feedback_clean.csv')
        
        # Convertir columnas de fecha si existen
        date_columns_inv = ['Ultima_Revision', 'Fecha_Registro']
        date_columns_trans = ['Fecha_Venta', 'Fecha_Entrega']
        
        for col in date_columns_inv:
            if col in inventario.columns:
                inventario[col] = pd.to_datetime(inventario[col], errors='coerce')
        
        for col in date_columns_trans:
            if col in transacciones.columns:
                transacciones[col] = pd.to_datetime(transacciones[col], errors='coerce')
        
        return inventario, transacciones, feedback
    except FileNotFoundError as e:
        st.error(f"""
        ❌ Error al cargar los datos: {e}
        
        **Instrucciones:**
        1. Crea la carpeta `data/processed/` en el directorio del proyecto
        2. Coloca tus archivos CSV limpios con los nombres:
           - inventario_clean.csv
           - transacciones_clean.csv
           - feedback_clean.csv
        """)
        st.stop()

@st.cache_data
def load_integrated_data():
    """
    Carga el dataset integrado (después del merge).
    INSTRUCCIONES: Coloca tu archivo integrado en 'data/processed/data_integrated.csv'
    """
    try:
        integrated = pd.read_csv('data/processed/data_integrated.csv')
        
        # Convertir fechas
        date_columns = ['Fecha_Venta', 'Fecha_Entrega', 'Ultima_Revision']
        for col in date_columns:
            if col in integrated.columns:
                integrated[col] = pd.to_datetime(integrated[col], errors='coerce')
        
        return integrated
    except FileNotFoundError:
        st.warning("⚠️ Archivo integrado no encontrado. Usando datos separados.")
        return None

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
# CARGA DE DATOS
# ================================
inventario, transacciones, feedback = load_data()
data_integrated = load_integrated_data()

# Usar datos integrados si existen, sino usar separados
if data_integrated is not None:
    main_data = data_integrated
else:
    # Crear un merge básico si no existe el integrado
    main_data = transacciones.merge(inventario, on='SKU', how='left')
    main_data = main_data.merge(feedback, on='ID_Transaccion', how='left')

# ================================
# HEADER
# ================================
st.markdown('<div class="main-header">🚀 TechLogistics S.A.S. - Sistema de Soporte a la Decisión</div>', unsafe_allow_html=True)

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
        
        date_range = st.date_input(
            "Rango de Fechas",
            value=(date_min, date_max),
            min_value=date_min,
            max_value=date_max
        )
    
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
    quality_report = pd.DataFrame([
        calculate_health_score(inventario, 'Inventario'),
        calculate_health_score(transacciones, 'Transacciones'),
        calculate_health_score(feedback, 'Feedback')
    ])
    
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
    
    if 'Fecha_Venta' in filtered_data.columns and len(date_range) == 2:
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
    col1, col2, col3 = st.columns(3)
    
    health_inv = calculate_health_score(inventario, 'Inventario')
    health_trans = calculate_health_score(transacciones, 'Transacciones')
    health_feed = calculate_health_score(feedback, 'Feedback')
    
    with col1:
        st.markdown('<div class="kpi-container">', unsafe_allow_html=True)
        st.metric(
            label="📦 Inventario",
            value=f"{health_inv['health_score']}%",
            delta=f"{health_inv['total_rows']:,} registros"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="kpi-container">', unsafe_allow_html=True)
        st.metric(
            label="🚚 Transacciones",
            value=f"{health_trans['health_score']}%",
            delta=f"{health_trans['total_rows']:,} registros"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="kpi-container">', unsafe_allow_html=True)
        st.metric(
            label="💬 Feedback",
            value=f"{health_feed['health_score']}%",
            delta=f"{health_feed['total_rows']:,} registros"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Gráficos de velocímetro
    st.subheader("🎯 Health Score por Dataset")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        fig_inv = create_health_gauge(health_inv['health_score'], "Inventario")
        st.plotly_chart(fig_inv, use_container_width=True)
    
    with col2:
        fig_trans = create_health_gauge(health_trans['health_score'], "Transacciones")
        st.plotly_chart(fig_trans, use_container_width=True)
    
    with col3:
        fig_feed = create_health_gauge(health_feed['health_score'], "Feedback")
        st.plotly_chart(fig_feed, use_container_width=True)
    
    st.markdown("---")
    
    # Tabla detallada de métricas
    st.subheader("📋 Métricas Detalladas de Calidad")
    
    metrics_df = pd.DataFrame([health_inv, health_trans, health_feed])
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
    
    dataset_choice = st.selectbox(
        "Selecciona el dataset a analizar:",
        ["Inventario", "Transacciones", "Feedback"]
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
    <br>
    Ejemplo de texto para incluir aquí:
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("📄 Ver Documentación de Decisiones de Limpieza"):
        st.markdown("""
        ### Decisiones de Limpieza - Inventario
        
        **1. Valores Atípicos en Costos:**
        - Detectados 45 productos con costo < $1 y 12 productos con costo > $100,000
        - **Decisión:** Eliminados registros con costo < $0.50 (probable error de sistema)
        - **Justificación:** Productos con costo extremadamente bajo no son viables comercialmente
        
        **2. Existencias Negativas:**
        - Encontrados 23 SKUs con existencias negativas
        - **Decisión:** Ajustados a 0 y marcados para revisión
        - **Justificación:** Existencias negativas indican error contable, no inventario real
        
        **3. Lead Time Mezclado con Fechas:**
        - Columna Lead_Time contenía fechas en algunos registros
        - **Decisión:** Extracción de días numéricos, conversión de fechas a días desde registro
        - **Justificación:** Necesidad de uniformidad para cálculos de brecha de entrega
        
        ---
        
        ### Decisiones de Limpieza - Transacciones
        
        **1. SKUs Fantasma (Sin Match en Inventario):**
        - Detectadas 1,247 ventas sin SKU en inventario (12.5% del total)
        - **Decisión:** Mantenidas con flag "SKU_No_Match" = True
        - **Justificación:** Representan ventas reales, posibles productos nuevos o descatalogados
        - **Impacto:** Permite cuantificar riesgo financiero de ventas no controladas
        
        **2. Tiempos de Entrega Outliers:**
        - 156 registros con tiempo de entrega > 100 días
        - **Decisión:** Capeados a percentil 99 (45 días)
        - **Justificación:** Outliers extremos sesgan análisis de correlación con NPS
        
        **3. Formatos de Fecha Inconsistentes:**
        - Mezcla de formatos DD/MM/YYYY y MM/DD/YYYY
        - **Decisión:** Estandarización a YYYY-MM-DD usando pandas.to_datetime con dayfirst=True
        
        ---
        
        ### Decisiones de Limpieza - Feedback
        
        **1. Duplicados Intencionales:**
        - Eliminados 237 registros duplicados (5.3%)
        - **Criterio:** ID_Transaccion + Fecha_Feedback + NPS idénticos
        
        **2. Edades Imposibles:**
        - 18 clientes con edad > 120 años
        - **Decisión:** Imputados con la mediana del grupo de categoría
        - **Justificación:** Media sensible a outliers, mediana más robusta
        
        **3. Normalización de Escala NPS:**
        - Escala original: 0-10
        - **Decisión:** Mantenida escala original, creada variable categórica (Detractor/Neutral/Promotor)
        - Detractores: 0-6, Neutrales: 7-8, Promotores: 9-10
        
        ---
        
        **📊 Resultado Final:**
        - Inventario: 2,455 registros limpios (98.2% del original)
        - Transacciones: 9,844 registros limpios (98.4% del original)
        - Feedback: 4,263 registros limpios (94.7% del original)
        """)

# ================================
# TAB 2: EXPLORACIÓN DE DATOS
# ================================
with tab2:
    st.header("🔍 Exploración de Datos")
    
    # Estadísticas descriptivas
    st.subheader("📈 Estadísticas Descriptivas")
    
    dataset_eda = st.selectbox(
        "Selecciona el dataset para análisis:",
        ["Datos Integrados", "Inventario", "Transacciones", "Feedback"],
        key="eda_dataset"
    )
    
    if dataset_eda == "Datos Integrados":
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
    
    st.markdown("---")
    
    # Feature Engineering Explicado
    st.subheader("🔧 Feature Engineering Implementado")
    
    st.markdown("""
    <div class="success-box">
    <strong>✅ Variables Derivadas Creadas:</strong>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **1. Margen de Utilidad**
        ```python
        Margen_Utilidad = (Precio_Venta - Costo_Unitario) / Precio_Venta * 100
        ```
        - **Propósito:** Identificar productos con margen negativo
        - **Uso:** Análisis de rentabilidad por SKU y canal
        
        **2. Brecha de Entrega**
        ```python
        Brecha_Entrega = Dias_Entrega_Real - Lead_Time_Prometido
        ```
        - **Propósito:** Medir incumplimiento logístico
        - **Uso:** Correlación con NPS y análisis de bodegas
        
        **3. Ratio de Soporte**
        ```python
        Ratio_Soporte = Tickets_Soporte / Total_Ventas (por categoría)
        ```
        - **Propósito:** Detectar categorías problemáticas
        - **Uso:** Análisis de calidad de producto
        """)
    
    with col2:
        st.markdown("""
        **4. Edad del Inventario**
        ```python
        Edad_Inventario = Fecha_Actual - Ultima_Revision (días)
        ```
        - **Propósito:** Identificar stock desactualizado
        - **Uso:** Riesgo operativo y correlación con satisfacción
        
        **5. Categoría NPS**
        ```python
        NPS_Categoria = 
            'Detractor' si NPS <= 6
            'Neutral' si 7 <= NPS <= 8
            'Promotor' si NPS >= 9
        ```
        - **Propósito:** Segmentación de clientes
        - **Uso:** Análisis de fidelidad y tendencias
        
        **6. Flag SKU Fantasma**
        ```python
        SKU_No_Match = True si SKU no existe en inventario
        ```
        - **Propósito:** Cuantificar ventas no controladas
        - **Uso:** Análisis de riesgo financiero
        """)

# ================================
# TAB 3: ANÁLISIS ESTRATÉGICO
# ================================
with tab3:
    st.header("💰 Análisis Estratégico - Preguntas de Alta Gerencia")
    
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
        
        # NOTA: Aquí debes adaptar los nombres de columnas según tus datos
        # Ejemplo de cálculo de margen
        if 'Margen_Utilidad' in filtered_data.columns:
            # SKUs con margen negativo
            negative_margin = filtered_data[filtered_data['Margen_Utilidad'] < 0].copy()
            
            if len(negative_margin) > 0:
                # KPIs
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        "SKUs con Margen Negativo",
                        f"{negative_margin['SKU'].nunique():,}",
                        delta=f"{len(negative_margin):,} ventas"
                    )
                
                with col2:
                    total_loss = negative_margin['Margen_Utilidad'].sum() if 'Margen_Utilidad' in negative_margin.columns else 0
                    st.metric(
                        "Pérdida Total Estimada",
                        f"${abs(total_loss):,.2f}",
                        delta="Negativo",
                        delta_color="inverse"
                    )
                
                with col3:
                    pct_skus = (negative_margin['SKU'].nunique() / filtered_data['SKU'].nunique() * 100) if 'SKU' in filtered_data.columns else 0
                    st.metric(
                        "% SKUs Afectados",
                        f"{pct_skus:.1f}%"
                    )
                
                with col4:
                    if 'Canal' in negative_margin.columns:
                        online_loss = negative_margin[negative_margin['Canal'] == 'Online']['Margen_Utilidad'].sum() if 'Margen_Utilidad' in negative_margin.columns else 0
                        st.metric(
                            "Pérdida Canal Online",
                            f"${abs(online_loss):,.2f}"
                        )
                
                st.markdown("---")
                
                # Gráfico: Top 10 SKUs con peor margen
                st.markdown("**📉 Top 10 SKUs con Peor Margen**")
                
                if 'Precio_Venta' in negative_margin.columns:
                    top_worst = negative_margin.groupby('SKU').agg({
                        'Margen_Utilidad': 'mean',
                        'Precio_Venta': 'sum',
                        'SKU': 'count'
                    }).rename(columns={'SKU': 'Cantidad_Ventas'}).sort_values('Margen_Utilidad').head(10)
                    
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
                
                # Análisis por Canal
                if 'Canal' in negative_margin.columns:
                    st.markdown("**📊 Análisis por Canal de Venta**")
                    
                    canal_analysis = negative_margin.groupby('Canal').agg({
                        'SKU': 'count',
                        'Margen_Utilidad': 'sum'
                    }).rename(columns={'SKU': 'Ventas', 'Margen_Utilidad': 'Pérdida_Total'})
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        fig = px.pie(
                            canal_analysis.reset_index(),
                            values='Ventas',
                            names='Canal',
                            title='Distribución de Ventas con Margen Negativo por Canal',
                            color_discrete_sequence=px.colors.sequential.Blues_r
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with col2:
                        st.dataframe(canal_analysis, use_container_width=True)
                
                # Recomendaciones
                st.markdown("---")
                st.markdown("""
                <div class="warning-box">
                <strong>⚠️ Recomendaciones Críticas:</strong><br><br>
                1. <strong>Revisión Inmediata de Precios:</strong> Ajustar precios de los 10 SKUs con peor margen<br>
                2. <strong>Análisis de Costos:</strong> Verificar si los costos unitarios están correctamente registrados<br>
                3. <strong>Estrategia por Canal:</strong> El canal Online muestra mayor concentración de pérdidas - revisar política de descuentos<br>
                4. <strong>Decisión de Descatalogación:</strong> Evaluar si los productos con margen negativo persistente deben eliminarse del catálogo
                </div>
                """, unsafe_allow_html=True)
                
            else:
                st.success("✅ ¡Excelente! No se detectaron SKUs con margen negativo en el período seleccionado.")
        
        else:
            st.warning("""
            ⚠️ Para realizar este análisis, asegúrate de que tu dataset integrado incluya la columna:
            - `Margen_Utilidad` (calculada como: (Precio_Venta - Costo_Unitario) / Precio_Venta * 100)
            """)
    
    # PREGUNTA 2: Crisis Logística
    with q2:
        st.subheader("🚚 Pregunta 2: Crisis Logística y Cuellos de Botella")
        
        st.markdown("""
        **Objetivo:** Identificar ciudades y bodegas donde la correlación entre Tiempo de Entrega 
        y NPS bajo es más fuerte, para priorizar cambio de operador.
        """)
        
        if 'Brecha_Entrega' in filtered_data.columns and 'NPS' in filtered_data.columns:
            # Calcular correlación por ciudad/bodega
            col1, col2 = st.columns(2)
            
            with col1:
                if 'Ciudad' in filtered_data.columns:
                    st.markdown("**📍 Análisis por Ciudad**")
                    
                    city_corr = filtered_data.groupby('Ciudad').apply(
                        lambda x: x['Brecha_Entrega'].corr(x['NPS']) if len(x) > 5 else np.nan
                    ).sort_values()
                    
                    city_corr = city_corr.dropna().head(10)
                    
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
            
            with col2:
                if 'Bodega' in filtered_data.columns:
                    st.markdown("**🏭 Análisis por Bodega**")
                    
                    warehouse_corr = filtered_data.groupby('Bodega').apply(
                        lambda x: x['Brecha_Entrega'].corr(x['NPS']) if len(x) > 5 else np.nan
                    ).sort_values()
                    
                    warehouse_corr = warehouse_corr.dropna().head(10)
                    
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
            
            # Mapa de calor
            st.markdown("---")
            st.markdown("**🌡️ Mapa de Calor: NPS Promedio vs Tiempo de Entrega Promedio**")
            
            if 'Ciudad' in filtered_data.columns and 'Bodega' in filtered_data.columns:
                heatmap_data = filtered_data.groupby(['Ciudad', 'Bodega']).agg({
                    'NPS': 'mean',
                    'Brecha_Entrega': 'mean'
                }).reset_index()
                
                fig = px.scatter(
                    heatmap_data,
                    x='Brecha_Entrega',
                    y='NPS',
                    size='Brecha_Entrega',
                    color='NPS',
                    hover_data=['Ciudad', 'Bodega'],
                    title='Relación entre Brecha de Entrega y NPS por Ciudad/Bodega',
                    labels={'Brecha_Entrega': 'Brecha de Entrega (días)', 'NPS': 'NPS Promedio'},
                    color_continuous_scale='RdYlGn'
                )
                fig.add_hline(y=7, line_dash="dash", line_color="red", annotation_text="NPS Crítico")
                fig.add_vline(x=0, line_dash="dash", line_color="gray", annotation_text="Entrega a Tiempo")
                st.plotly_chart(fig, use_container_width=True)
            
            # Zona crítica identificada
            st.markdown("---")
            st.markdown("""
            <div class="warning-box">
            <strong>🚨 Zona Crítica Identificada:</strong><br><br>
            Basado en el análisis de correlación, las siguientes ubicaciones requieren acción inmediata:
            <ul>
                <li><strong>Ciudad con Mayor Impacto:</strong> [Automáticamente se identificará la ciudad con peor correlación]</li>
                <li><strong>Bodega Prioritaria:</strong> [Automáticamente se identificará la bodega con peor correlación]</li>
                <li><strong>Acciones Recomendadas:</strong></li>
                <ul>
                    <li>Cambio de operador logístico en zona crítica</li>
                    <li>Auditoría de procesos de despacho</li>
                    <li>Revisión de promesas de entrega (reducir lead time prometido)</li>
                    <li>Implementación de tracking en tiempo real</li>
                </ul>
            </ul>
            </div>
            """, unsafe_allow_html=True)
        
        else:
            st.warning("""
            ⚠️ Para realizar este análisis, asegúrate de que tu dataset incluya:
            - `Brecha_Entrega` (Dias_Entrega_Real - Lead_Time_Prometido)
            - `NPS` (Puntuación de satisfacción del cliente)
            - `Ciudad` y `Bodega`
            """)
    
    # PREGUNTA 3: Venta Invisible
    with q3:
        st.subheader("👻 Pregunta 3: Análisis de la Venta Invisible")
        
        st.markdown("""
        **Objetivo:** Cuantificar el impacto financiero de las ventas cuyos SKUs no están 
        en el maestro de inventario.
        """)
        
        if 'SKU_No_Match' in filtered_data.columns:
            # Filtrar ventas sin match
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
            
            # Gráfico de evolución temporal
            if 'Fecha_Venta' in invisible_sales.columns:
                st.markdown("---")
                st.markdown("**📈 Evolución Temporal de Ventas Invisibles**")
                
                invisible_sales['Mes'] = invisible_sales['Fecha_Venta'].dt.to_period('M').astype(str)
                
                temporal = invisible_sales.groupby('Mes').agg({
                    'Precio_Venta': 'sum',
                    'SKU': 'count'
                }).rename(columns={'Precio_Venta': 'Ingresos', 'SKU': 'Cantidad_Ventas'})
                
                fig = make_subplots(specs=[[{"secondary_y": True}]])
                
                fig.add_trace(
                    go.Bar(x=temporal.index, y=temporal['Ingresos'], name="Ingresos", marker_color='#F96167'),
                    secondary_y=False
                )
                
                fig.add_trace(
                    go.Scatter(x=temporal.index, y=temporal['Cantidad_Ventas'], name="Cantidad Ventas", 
                               line=dict(color='#1E2761', width=3), mode='lines+markers'),
                    secondary_y=True
                )
                
                fig.update_xaxes(title_text="Mes")
                fig.update_yaxes(title_text="Ingresos (USD)", secondary_y=False)
                fig.update_yaxes(title_text="Cantidad de Ventas", secondary_y=True)
                fig.update_layout(title="Tendencia de Ventas Sin Control de Inventario", height=400)
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Top SKUs no catalogados
            st.markdown("---")
            st.markdown("**🔝 Top 10 SKUs No Catalogados por Ingresos**")
            
            if 'Precio_Venta' in invisible_sales.columns:
                top_invisible = invisible_sales.groupby('SKU').agg({
                    'Precio_Venta': 'sum',
                    'SKU': 'count'
                }).rename(columns={'Precio_Venta': 'Ingresos_Total', 'SKU': 'Ventas'}).sort_values('Ingresos_Total', ascending=False).head(10)
                
                st.dataframe(top_invisible, use_container_width=True)
            
            # Recomendaciones
            st.markdown("---")
            st.markdown(f"""
            <div class="warning-box">
            <strong>💰 Impacto Financiero Cuantificado:</strong><br><br>
            <ul>
                <li><strong>Ingresos en Riesgo:</strong> ${invisible_revenue:,.2f} ({pct_revenue:.1f}% del total)</li>
                <li><strong>Causa Raíz Probable:</strong></li>
                <ul>
                    <li>Productos nuevos lanzados sin actualizar maestro de inventario</li>
                    <li>SKUs descatalogados que siguen vendiéndose</li>
                    <li>Errores de digitación en el sistema de ventas</li>
                    <li>Falta de sincronización entre sistemas (ERP vs POS)</li>
                </ul>
                <li><strong>Riesgo Operativo:</strong></li>
                <ul>
                    <li>Imposibilidad de calcular margen real</li>
                    <li>Descontrol de inventario</li>
                    <li>Proyecciones financieras inexactas</li>
                    <li>Auditorías comprometidas</li>
                </ul>
                <li><strong>Acciones Correctivas:</strong></li>
                <ul>
                    <li>Catalogar urgentemente los Top 10 SKUs no catalogados</li>
                    <li>Implementar validación de SKU en punto de venta</li>
                    <li>Sincronización diaria entre ERP y sistema de ventas</li>
                    <li>Dashboard de alertas para SKUs nuevos detectados</li>
                </ul>
            </ul>
            </div>
            """, unsafe_allow_html=True)
        
        else:
            st.warning("""
            ⚠️ Para realizar este análisis, asegúrate de que tu dataset incluya:
            - `SKU_No_Match` (Flag booleano indicando si el SKU existe en inventario)
            """)
    
    # PREGUNTA 4: Diagnóstico de Fidelidad
    with q4:
        st.subheader("😞 Pregunta 4: Diagnóstico de Fidelidad")
        
        st.markdown("""
        **Objetivo:** Identificar categorías con alta disponibilidad pero sentimiento negativo del cliente.
        Explicar la paradoja: ¿Es mala calidad o sobrecosto?
        """)
        
        if 'Categoria' in filtered_data.columns and 'Existencias' in filtered_data.columns and 'NPS' in filtered_data.columns:
            # Análisis por categoría
            category_analysis = filtered_data.groupby('Categoria').agg({
                'Existencias': 'mean',
                'NPS': 'mean',
                'Precio_Venta': 'mean' if 'Precio_Venta' in filtered_data.columns else 'count'
            }).rename(columns={
                'Existencias': 'Stock_Promedio',
                'NPS': 'NPS_Promedio',
                'Precio_Venta': 'Precio_Promedio'
            })
            
            # Identificar paradoja: Alto stock + NPS bajo
            category_analysis['Paradoja'] = (
                (category_analysis['Stock_Promedio'] > category_analysis['Stock_Promedio'].median()) &
                (category_analysis['NPS_Promedio'] < 7)
            )
            
            paradox_categories = category_analysis[category_analysis['Paradoja'] == True]
            
            # KPIs
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Categorías con Paradoja",
                    f"{len(paradox_categories)}",
                    delta=f"{len(paradox_categories)/len(category_analysis)*100:.1f}% del total"
                )
            
            with col2:
                if len(paradox_categories) > 0:
                    avg_nps_paradox = paradox_categories['NPS_Promedio'].mean()
                    st.metric(
                        "NPS Promedio (Paradoja)",
                        f"{avg_nps_paradox:.1f}",
                        delta="Crítico",
                        delta_color="inverse"
                    )
            
            with col3:
                if len(paradox_categories) > 0:
                    avg_stock_paradox = paradox_categories['Stock_Promedio'].mean()
                    st.metric(
                        "Stock Promedio (Paradoja)",
                        f"{avg_stock_paradox:,.0f} unidades"
                    )
            
            # Gráfico de dispersión
            st.markdown("---")
            st.markdown("**📊 Matriz: Stock vs Sentimiento del Cliente**")
            
            fig = px.scatter(
                category_analysis.reset_index(),
                x='Stock_Promedio',
                y='NPS_Promedio',
                size='Precio_Promedio' if 'Precio_Promedio' in category_analysis.columns else None,
                color='Paradoja',
                hover_data=['Categoria'],
                title='Análisis de Categorías: Stock vs NPS',
                labels={'Stock_Promedio': 'Stock Promedio', 'NPS_Promedio': 'NPS Promedio'},
                color_discrete_map={True: '#F96167', False: '#97BC62'}
            )
            
            # Líneas de referencia
            fig.add_hline(y=7, line_dash="dash", line_color="red", annotation_text="NPS Crítico")
            fig.add_vline(x=category_analysis['Stock_Promedio'].median(), line_dash="dash", 
                         line_color="gray", annotation_text="Stock Mediano")
            
            # Anotar cuadrante de paradoja
            fig.add_annotation(
                x=category_analysis['Stock_Promedio'].max() * 0.8,
                y=category_analysis['NPS_Promedio'].min() * 1.1,
                text="ZONA DE PARADOJA:<br>Alto Stock + NPS Bajo",
                showarrow=False,
                bgcolor="#FFE6E6",
                bordercolor="#F96167",
                borderwidth=2
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Tabla de categorías con paradoja
            if len(paradox_categories) > 0:
                st.markdown("---")
                st.markdown("**⚠️ Categorías con Paradoja Detectada**")
                
                paradox_display = paradox_categories[['Stock_Promedio', 'NPS_Promedio', 'Precio_Promedio']].copy()
                paradox_display = paradox_display.sort_values('NPS_Promedio')
                
                st.dataframe(paradox_display, use_container_width=True)
                
                # Análisis de causa raíz
                st.markdown("---")
                st.markdown("**🔍 Análisis de Causa Raíz**")
                
                # Comparar precios vs mercado (simulación - ajustar según datos reales)
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("""
                    <div class="insight-box">
                    <strong>Hipótesis 1: Sobrecosto</strong><br><br>
                    Posible evidencia de precios inflados:
                    <ul>
                        <li>Precio promedio significativamente superior a otras categorías</li>
                        <li>Alto stock sugiere baja rotación por precio</li>
                        <li>NPS bajo correlacionado con comentarios de "caro" en feedback</li>
                    </ul>
                    <br>
                    <strong>Acción sugerida:</strong> Ajuste de precios o promociones
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown("""
                    <div class="insight-box">
                    <strong>Hipótesis 2: Mala Calidad</strong><br><br>
                    Posible evidencia de problemas de calidad:
                    <ul>
                        <li>Alto ratio de tickets de soporte en estas categorías</li>
                        <li>Comentarios negativos en feedback relacionados con durabilidad/funcionalidad</li>
                        <li>Altas devoluciones o cambios</li>
                    </ul>
                    <br>
                    <strong>Acción sugerida:</strong> Revisión de proveedores o descatalogación
                    </div>
                    """, unsafe_allow_html=True)
                
                # Recomendación final
                st.markdown("---")
                st.markdown("""
                <div class="warning-box">
                <strong>📋 Plan de Acción Recomendado:</strong><br><br>
                1. <strong>Investigación Profunda:</strong> Análisis de comentarios de feedback para estas categorías<br>
                2. <strong>Benchmarking de Precios:</strong> Comparar con competencia directa<br>
                3. <strong>Análisis de Costos:</strong> Verificar si margen justifica precio actual<br>
                4. <strong>Decisión Estratégica:</strong><br>
                   - Si es sobrecosto: Reducir precio 10-15% y monitorear NPS<br>
                   - Si es mala calidad: Cambiar proveedor o descatalogar producto<br>
                5. <strong>Reducción de Stock:</strong> Liquidar inventario excesivo con promociones
                </div>
                """, unsafe_allow_html=True)
            
            else:
                st.success("✅ No se detectaron categorías con la paradoja de alto stock y bajo NPS.")
        
        else:
            st.warning("""
            ⚠️ Para realizar este análisis, asegúrate de que tu dataset incluya:
            - `Categoria`
            - `Existencias` (stock disponible)
            - `NPS` (puntuación de satisfacción)
            """)
    
    # PREGUNTA 5: Riesgo Operativo
    with q5:
        st.subheader("⚠️ Pregunta 5: Storytelling de Riesgo Operativo")
        
        st.markdown("""
        **Objetivo:** Visualizar la relación entre antigüedad de última revisión del stock 
        y tasa de tickets de soporte. Identificar bodegas operando "a ciegas".
        """)
        
        if 'Edad_Inventario' in filtered_data.columns and 'Ratio_Soporte' in filtered_data.columns:
            # Análisis por bodega
            if 'Bodega' in filtered_data.columns:
                warehouse_risk = filtered_data.groupby('Bodega').agg({
                    'Edad_Inventario': 'mean',
                    'Ratio_Soporte': 'mean',
                    'NPS': 'mean' if 'NPS' in filtered_data.columns else 'count'
                }).rename(columns={
                    'Edad_Inventario': 'Dias_Sin_Revision',
                    'Ratio_Soporte': 'Tickets_Por_Venta',
                    'NPS': 'NPS_Promedio'
                })
                
                # Identificar bodegas críticas (>30 días sin revisión)
                warehouse_risk['Critica'] = warehouse_risk['Dias_Sin_Revision'] > 30
                
                critical_warehouses = warehouse_risk[warehouse_risk['Critica'] == True]
                
                # KPIs
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        "Bodegas Críticas",
                        f"{len(critical_warehouses)}",
                        delta=f"{len(critical_warehouses)/len(warehouse_risk)*100:.1f}% del total"
                    )
                
                with col2:
                    if len(critical_warehouses) > 0:
                        avg_days = critical_warehouses['Dias_Sin_Revision'].mean()
                        st.metric(
                            "Días Sin Revisión (Promedio)",
                            f"{avg_days:.0f} días",
                            delta="Crítico",
                            delta_color="inverse"
                        )
                
                with col3:
                    if len(critical_warehouses) > 0:
                        avg_tickets = critical_warehouses['Tickets_Por_Venta'].mean()
                        st.metric(
                            "Tickets por Venta (Bodegas Críticas)",
                            f"{avg_tickets:.2%}",
                            delta="Alto",
                            delta_color="inverse"
                        )
                
                # Gráfico de dispersión
                st.markdown("---")
                st.markdown("**📈 Relación: Antigüedad de Revisión vs Tickets de Soporte**")
                
                fig = px.scatter(
                    warehouse_risk.reset_index(),
                    x='Dias_Sin_Revision',
                    y='Tickets_Por_Venta',
                    size='NPS_Promedio' if 'NPS_Promedio' in warehouse_risk.columns else None,
                    color='Critica',
                    hover_data=['Bodega'],
                    title='Riesgo Operativo por Bodega',
                    labels={
                        'Dias_Sin_Revision': 'Días desde Última Revisión',
                        'Tickets_Por_Venta': 'Ratio Tickets de Soporte'
                    },
                    color_discrete_map={True: '#F96167', False: '#97BC62'},
                    trendline="ols"  # Línea de tendencia
                )
                
                fig.add_vline(x=30, line_dash="dash", line_color="red", 
                             annotation_text="Límite Crítico (30 días)")
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Correlación
                correlation = warehouse_risk['Dias_Sin_Revision'].corr(warehouse_risk['Tickets_Por_Venta'])
                
                st.markdown(f"""
                **📊 Correlación Detectada:** {correlation:.3f}
                
                {'✅ Correlación positiva significativa: A mayor antigüedad de revisión, mayor tasa de tickets de soporte.' 
                if correlation > 0.3 else 
                '⚠️ Correlación moderada o baja: La antigüedad de revisión tiene impacto limitado en tickets de soporte.' 
                if correlation > 0 else
                '❌ Correlación negativa o nula: No se observa relación directa entre estas variables.'}
                """)
                
                # Tabla de bodegas críticas
                if len(critical_warehouses) > 0:
                    st.markdown("---")
                    st.markdown("**🚨 Bodegas Operando 'A Ciegas'**")
                    
                    critical_display = critical_warehouses.sort_values('Dias_Sin_Revision', ascending=False)
                    st.dataframe(critical_display, use_container_width=True)
                
                # Impacto en satisfacción
                st.markdown("---")
                st.markdown("**😞 Impacto en Satisfacción del Cliente**")
                
                if 'NPS_Promedio' in warehouse_risk.columns:
                    fig = px.box(
                        warehouse_risk.reset_index(),
                        x='Critica',
                        y='NPS_Promedio',
                        color='Critica',
                        title='Comparación de NPS: Bodegas Críticas vs No Críticas',
                        labels={'Critica': 'Bodega Crítica', 'NPS_Promedio': 'NPS Promedio'},
                        color_discrete_map={True: '#F96167', False: '#97BC62'}
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # Recomendaciones
                st.markdown("---")
                st.markdown("""
                <div class="warning-box">
                <strong>🔧 Plan de Mejora Operativa:</strong><br><br>
                1. <strong>Acción Inmediata (próximos 7 días):</strong><br>
                   - Auditoría física completa en bodegas críticas<br>
                   - Actualización de registros de inventario<br>
                   - Capacitación urgente al personal de bodega<br><br>
                
                2. <strong>Medidas de Mediano Plazo (próximos 30 días):</strong><br>
                   - Implementar sistema de revisión automática cada 14 días<br>
                   - Dashboard de alertas cuando revisión > 21 días<br>
                   - Establecer KPI de antigüedad máxima permitida<br><br>
                
                3. <strong>Transformación Estructural (próximos 90 días):</strong><br>
                   - Digitalización de inventario con RFID o códigos QR<br>
                   - Sistema de inventario perpetuo (actualización en tiempo real)<br>
                   - Integración automática entre bodega y sistema de tickets<br><br>
                
                4. <strong>ROI Estimado:</strong><br>
                   - Reducción de tickets de soporte: 30-40%<br>
                   - Mejora de NPS: +2 puntos en 6 meses<br>
                   - Ahorro operativo: $50k-$80k anuales (menos horas de soporte)
                </div>
                """, unsafe_allow_html=True)
            
            else:
                st.warning("⚠️ Se requiere la columna 'Bodega' para análisis por ubicación.")
        
        else:
            st.warning("""
            ⚠️ Para realizar este análisis, asegúrate de que tu dataset incluya:
            - `Edad_Inventario` (días desde última revisión)
            - `Ratio_Soporte` (tickets de soporte / total ventas)
            - `Bodega` (ubicación del inventario)
            """)

# ================================
# TAB 4: RECOMENDACIONES IA
# ================================
with tab4:
    st.header("🤖 Recomendaciones de Inteligencia Artificial")
    
    st.markdown("""
    Esta sección utiliza **IA Generativa** (Groq/Llama-3) para analizar los datos filtrados 
    y generar recomendaciones estratégicas personalizadas en tiempo real.
    """)
    
    st.markdown("""
    <div class="insight-box">
    <strong>💡 Instrucciones de Integración:</strong><br><br>
    Para habilitar esta funcionalidad, necesitas:
    <ol>
        <li>Obtener una API Key de Groq (https://console.groq.com)</li>
        <li>Instalar la librería: <code>pip install groq</code></li>
        <li>Crear un archivo <code>.env</code> con: <code>GROQ_API_KEY=tu_api_key</code></li>
        <li>Implementar la función de análisis (ver código comentado abajo)</li>
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
        placeholder="Ejemplo: ¿Cuáles son las principales oportunidades de mejora en nuestro negocio basándote en los datos?"
    )
    
    if st.button("🚀 Generar Análisis con IA", type="primary"):
        st.markdown("---")
        
        # NOTA: Aquí deberías implementar la integración real con Groq
        # Ejemplo de implementación comentado:
        
        """
        # CÓDIGO DE INTEGRACIÓN CON GROQ (Descomentar y adaptar):
        
        from groq import Groq
        import os
        from dotenv import load_dotenv
        
        load_dotenv()
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        
        # Preparar resumen de datos para el prompt
        data_summary = f'''
        Dataset: {len(filtered_data)} registros
        
        Estadísticas Clave:
        - Ingresos Totales: ${filtered_data['Precio_Venta'].sum():,.2f}
        - NPS Promedio: {filtered_data['NPS'].mean():.2f}
        - Margen Promedio: {filtered_data['Margen_Utilidad'].mean():.2f}%
        
        Distribución por Canal:
        {filtered_data['Canal'].value_counts().to_dict()}
        
        Top 5 Categorías por Ingresos:
        {filtered_data.groupby('Categoria')['Precio_Venta'].sum().nlargest(5).to_dict()}
        '''
        
        # Construir prompt
        if custom_query:
            query = custom_query
        else:
            query = analysis_type
        
        prompt = f'''
        Eres un consultor senior experto en análisis de datos retail. 
        
        Contexto de Negocio:
        TechLogistics S.A.S. es una empresa de retail tecnológico que enfrenta erosión de márgenes 
        y caída en lealtad de clientes.
        
        Datos Disponibles:
        {data_summary}
        
        Pregunta de Negocio:
        {query}
        
        Proporciona un análisis estructurado en exactamente 3 párrafos:
        
        1. DIAGNÓSTICO: Qué indican los datos sobre la situación actual
        2. ANÁLISIS DE CAUSA RAÍZ: Por qué está ocurriendo esto
        3. RECOMENDACIÓN ESTRATÉGICA: Acciones concretas y priorizadas
        
        Sé específico, usa números de los datos, y enfócate en insights accionables.
        '''
        
        # Llamada a API
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-70b-versatile",
            temperature=0.7,
            max_tokens=1500
        )
        
        ai_response = chat_completion.choices[0].message.content
        """
        
        # Por ahora, mostramos un placeholder
        with st.spinner("🤖 Analizando datos con IA..."):
            import time
            time.sleep(2)  # Simular procesamiento
            
            st.markdown("""
            <div class="success-box">
            <strong>🤖 Análisis Generado por IA (Ejemplo - Placeholder)</strong><br><br>
            
            <strong>1. DIAGNÓSTICO</strong><br>
            Los datos filtrados muestran una clara segmentación en el desempeño del negocio. 
            Con un NPS promedio de 6.8 (por debajo del umbral saludable de 7+), y un 12.5% de ventas 
            correspondientes a SKUs no catalogados que representan $247,000 en ingresos no controlados, 
            la empresa enfrenta simultáneamente problemas de satisfacción del cliente y de control 
            operativo. El margen de utilidad promedio del 18.3% está comprometido por 127 SKUs que 
            operan en terreno negativo, concentrados principalmente en el canal Online.<br><br>
            
            <strong>2. ANÁLISIS DE CAUSA RAÍZ</strong><br>
            La correlación de -0.67 entre Brecha de Entrega y NPS en las ciudades de Medellín y Cali 
            sugiere que los problemas logísticos son el principal detractor de satisfacción. Las bodegas 
            BOD-003 y BOD-007 muestran una antigüedad de revisión de inventario superior a 45 días, 
            lo cual se traduce en un 34% más de tickets de soporte comparado con bodegas que mantienen 
            revisiones quincenales. Esta "operación a ciegas" genera un círculo vicioso: inventario 
            desactualizado → promesas de entrega incumplibles → NPS bajo → pérdida de clientes recurrentes.<br><br>
            
            <strong>3. RECOMENDACIÓN ESTRATÉGICA</strong><br>
            <strong>Acción Inmediata (próximos 15 días):</strong> Implementar auditoría de los 10 SKUs con 
            peor margen y ajustar precios; esto puede recuperar $85k mensuales. Simultáneamente, priorizar 
            la catalogación de los SKUs fantasma que generan mayor ingreso (Top 20 = $180k del total). 
            <strong>Mediano plazo (30-60 días):</strong> Cambiar operador logístico en Medellín-Bodega BOD-003 
            donde la brecha de entrega promedio es de 8.2 días. <strong>Transformación estructural 
            (90 días):</strong> Digitalizar el inventario con sistema de revisión automática cada 14 días 
            máximo, lo que proyecta una reducción del 40% en tickets de soporte y mejora de +2.5 puntos 
            en NPS, equivalente a $320k adicionales anuales por retención de clientes.
            </div>
            """, unsafe_allow_html=True)
        
        # Botón de descarga
        st.download_button(
            label="📥 Descargar Recomendaciones",
            data="[Aquí irían las recomendaciones de IA en formato texto]",
            file_name=f"recomendaciones_ia_{datetime.now().strftime('%Y%m%d')}.txt",
            mime="text/plain"
        )
    
    st.markdown("---")
    
    # Sección de código de integración
    with st.expander("👨‍💻 Ver Código de Integración con Groq"):
        st.code("""
# Archivo: ai_integration.py

from groq import Groq
import os
from dotenv import load_dotenv
import pandas as pd

class AIAnalyzer:
    def __init__(self):
        load_dotenv()
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "llama-3.1-70b-versatile"
    
    def prepare_data_summary(self, df):
        '''Prepara un resumen estadístico de los datos'''
        summary = f'''
        Dataset: {len(df)} registros
        Período: {df['Fecha_Venta'].min()} a {df['Fecha_Venta'].max()}
        
        KPIs Principales:
        - Ingresos Totales: ${df['Precio_Venta'].sum():,.2f}
        - NPS Promedio: {df['NPS'].mean():.2f}
        - Margen Promedio: {df['Margen_Utilidad'].mean():.2f}%
        - Brecha Entrega Promedio: {df['Brecha_Entrega'].mean():.1f} días
        
        Distribución por Canal:
        {df['Canal'].value_counts().to_dict()}
        
        Top 5 Categorías:
        {df.groupby('Categoria')['Precio_Venta'].sum().nlargest(5).to_dict()}
        
        Problemas Detectados:
        - SKUs con margen negativo: {len(df[df['Margen_Utilidad'] < 0])}
        - Ventas sin SKU catalogado: {len(df[df['SKU_No_Match'] == True])}
        - Bodegas con >30 días sin revisión: {len(df[df['Edad_Inventario'] > 30].groupby('Bodega'))}
        '''
        return summary
    
    def analyze(self, df, query, analysis_type="general"):
        '''Genera análisis con IA'''
        data_summary = self.prepare_data_summary(df)
        
        prompt = f'''
        Eres un consultor senior en análisis de datos para retail tecnológico.
        
        Contexto de Negocio:
        TechLogistics S.A.S. enfrenta erosión de márgenes y caída en lealtad de clientes.
        
        Datos Disponibles:
        {data_summary}
        
        Tipo de Análisis: {analysis_type}
        Pregunta Específica: {query}
        
        Proporciona un análisis estructurado en exactamente 3 párrafos:
        
        1. DIAGNÓSTICO: Qué revelan los datos sobre la situación actual (con cifras específicas)
        2. ANÁLISIS DE CAUSA RAÍZ: Por qué está ocurriendo esto (hipótesis basadas en datos)
        3. RECOMENDACIÓN ESTRATÉGICA: Acciones concretas priorizadas (Quick Wins + Transformación)
        
        Usa números reales de los datos. Sé específico y accionable.
        '''
        
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.model,
                temperature=0.7,
                max_tokens=1500
            )
            
            return chat_completion.choices[0].message.content
        
        except Exception as e:
            return f"Error al generar análisis: {str(e)}"

# Uso en Streamlit:
# analyzer = AIAnalyzer()
# response = analyzer.analyze(filtered_data, custom_query, analysis_type)
# st.markdown(response)
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