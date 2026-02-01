"""
TechLogistics S.A.S. - Sistema de Soporte a la Decisión (DSS)
Dashboard Streamlit Modular
Autor: [Tu Nombre]
Universidad EAFIT - 2026-1
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Importar módulos personalizados
from utils import (
    load_uploaded_file, process_dates, safe_merge, filter_data,
    detect_date_columns, detect_categorical_columns,
    calculate_health_score, get_custom_css
)
from tabs import (
    render_quality_tab,
    render_exploration_tab,
    render_strategic_tab,
    render_ai_tab
)

# ================================
# CONFIGURACIÓN DE PÁGINA
# ================================
st.set_page_config(
    page_title="TechLogistics DSS",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Aplicar estilos CSS
st.markdown(get_custom_css(), unsafe_allow_html=True)

# ================================
# HEADER
# ================================
st.markdown('<div class="main-header">🚀 TechLogistics S.A.S. - Sistema de Soporte a la Decisión</div>', unsafe_allow_html=True)

# ================================
# CARGA DE ARCHIVOS
# ================================
st.markdown('<div class="upload-section">', unsafe_allow_html=True)
st.header("📂 Carga de Datos")
st.markdown("**Instrucciones:** Sube tus archivos CSV limpios. Los archivos deben contener las columnas esperadas para el análisis.")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("📦 Inventario")
    inventario_file = st.file_uploader("Sube el archivo de inventario", type=['csv'], key='inventario',
                                       help="Debe contener: SKU, Categoria, Existencias, Costo_Unitario, etc.")

with col2:
    st.subheader("🚚 Transacciones")
    transacciones_file = st.file_uploader("Sube el archivo de transacciones", type=['csv'], key='transacciones',
                                          help="Debe contener: ID_Transaccion, SKU, Fecha_Venta, Precio_Venta, etc.")

with col3:
    st.subheader("💬 Feedback")
    feedback_file = st.file_uploader("Sube el archivo de feedback", type=['csv'], key='feedback',
                                     help="Debe contener: ID_Transaccion, NPS, Comentarios, etc.")

st.markdown('</div>', unsafe_allow_html=True)

# Cargar archivos
inventario = load_uploaded_file(inventario_file)
transacciones = load_uploaded_file(transacciones_file)
feedback = load_uploaded_file(feedback_file)

# Verificar que al menos un archivo fue cargado
if inventario is None and transacciones is None and feedback is None:
    st.warning("⚠️ Por favor, sube al menos un archivo CSV para comenzar el análisis.")
    st.stop()

# Procesar fechas
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

# ================================
# MOSTRAR COLUMNAS
# ================================
with st.expander("📋 Ver columnas de los archivos cargados", expanded=False):
    if transacciones is not None:
        st.write(f"**🚚 Transacciones ({len(transacciones)} filas):**")
        st.code(', '.join(transacciones.columns.tolist()))
    if inventario is not None:
        st.write(f"**📦 Inventario ({len(inventario)} filas):**")
        st.code(', '.join(inventario.columns.tolist()))
    if feedback is not None:
        st.write(f"**💬 Feedback ({len(feedback)} filas):**")
        st.code(', '.join(feedback.columns.tolist()))

# ================================
# INTEGRAR DATASETS
# ================================
main_data = None

if transacciones is not None:
    main_data = transacciones.copy()
    if inventario is not None:
        main_data, _ = safe_merge(main_data, inventario, 'SKU', 'Transacciones', 'Inventario')
    if feedback is not None:
        main_data, _ = safe_merge(main_data, feedback, 'ID_Transaccion', 'Transacciones', 'Feedback')
elif inventario is not None:
    main_data = inventario.copy()
    st.info(f"📊 Usando datos de inventario: {len(main_data)} registros")
elif feedback is not None:
    main_data = feedback.copy()
    st.info(f"📊 Usando datos de feedback: {len(main_data)} registros")

if main_data is not None:
    st.info(f"📊 Dataset principal: {len(main_data)} registros × {len(main_data.columns)} columnas")

# ================================
# SIDEBAR - FILTROS
# ================================
with st.sidebar:
    st.image("https://via.placeholder.com/200x80/1E2761/FFFFFF?text=TechLogistics", use_container_width=True)
    st.markdown("---")
    st.header("🎛️ Filtros Globales")
    
    # Filtros de fecha
    date_columns = detect_date_columns(main_data)
    date_range = None
    date_filter_col = None
    
    if date_columns:
        selected_date_col = st.selectbox("Filtrar por fecha:", ['Ninguno'] + date_columns)
        if selected_date_col != 'Ninguno':
            main_data[selected_date_col] = pd.to_datetime(main_data[selected_date_col], errors='coerce')
            date_min = main_data[selected_date_col].min()
            date_max = main_data[selected_date_col].max()
            
            if pd.notna(date_min) and pd.notna(date_max):
                date_range = st.date_input(f"Rango de {selected_date_col}", value=(date_min, date_max),
                                          min_value=date_min, max_value=date_max)
                date_filter_col = selected_date_col
    
    # Filtros categóricos
    categorical_cols = detect_categorical_columns(main_data)
    
    if categorical_cols:
        st.subheader("Filtros Disponibles")
        filters = {}
        for col in categorical_cols[:5]:
            unique_values = sorted(main_data[col].dropna().unique())
            selected = st.multiselect(f"📌 {col}", options=unique_values, default=None, key=f"filter_{col}")
            if selected:
                filters[col] = selected
    else:
        filters = {}
    
    st.markdown("---")
    
    # Descargas
    st.subheader("📥 Descargas")
    
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
        st.download_button("📊 Reporte de Calidad", data=csv_quality,
                          file_name=f"reporte_calidad_{datetime.now().strftime('%Y%m%d')}.csv",
                          mime="text/csv")
    
    # Aplicar filtros
    filtered_data = filter_data(main_data, filters)
    
    if date_range is not None and len(date_range) == 2 and date_filter_col is not None:
        filtered_data = filtered_data[
            (filtered_data[date_filter_col] >= pd.to_datetime(date_range[0])) &
            (filtered_data[date_filter_col] <= pd.to_datetime(date_range[1]))
        ]
    
    csv_filtered = filtered_data.to_csv(index=False).encode('utf-8')
    st.download_button("📁 Datos Filtrados", data=csv_filtered,
                      file_name=f"datos_filtrados_{datetime.now().strftime('%Y%m%d')}.csv",
                      mime="text/csv")
    
    st.markdown("---")
    st.caption(f"📅 Última actualización: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    st.caption(f"📊 Registros: {len(filtered_data):,} de {len(main_data):,}")

# ================================
# TABS PRINCIPALES
# ================================
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Auditoría de Calidad",
    "🔍 Exploración de Datos",
    "💰 Análisis Estratégico",
    "🤖 Recomendaciones IA"
])

with tab1:
    render_quality_tab(inventario, transacciones, feedback)

with tab2:
    render_exploration_tab(filtered_data, inventario, transacciones, feedback)

with tab3:
    render_strategic_tab(filtered_data)

with tab4:
    render_ai_tab(filtered_data)

# ================================
# FOOTER
# ================================
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666; padding: 2rem;'>
        <p><strong>TechLogistics S.A.S. - Sistema de Soporte a la Decisión</strong></p>
        <p>Desarrollado por [Tu Nombre] | Universidad EAFIT | 2026-1</p>
        <p>📧 Contacto: tu.email@eafit.edu.co</p>
    </div>
    """, unsafe_allow_html=True)