"""
Dashboard Minimalista - TechLogistics
Análisis Simple de Datos
"""

import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración
st.set_page_config(page_title="TechLogistics - Análisis", layout="wide")

# Título
st.title("📊 TechLogistics - Sistema de Análisis")

# Instrucciones
st.markdown("""
Sube tus archivos CSV limpios para realizar el análisis.
""")

# Subir archivos
st.header("📁 Cargar Datos")

col1, col2, col3 = st.columns(3)

with col1:
    inventario_file = st.file_uploader("Inventario CSV", type=['csv'])
    
with col2:
    transacciones_file = st.file_uploader("Transacciones CSV", type=['csv'])
    
with col3:
    feedback_file = st.file_uploader("Feedback CSV", type=['csv'])

# Procesar si hay archivos
if inventario_file and transacciones_file and feedback_file:
    
    # Cargar datos
    inventario = pd.read_csv(inventario_file)
    transacciones = pd.read_csv(transacciones_file)
    feedback = pd.read_csv(feedback_file)
    
    # Intentar merge si existen las columnas clave
    data = transacciones.copy()
    
    # Merge con inventario
    if 'SKU' in transacciones.columns and 'SKU' in inventario.columns:
        data = data.merge(inventario, on='SKU', how='left', suffixes=('', '_inv'))
    
    # Merge con feedback
    if 'ID_Transaccion' in data.columns and 'ID_Transaccion' in feedback.columns:
        data = data.merge(feedback, on='ID_Transaccion', how='left', suffixes=('', '_feed'))
    
    st.success(f"✅ Datos cargados: {len(data):,} registros")
    
    # Mostrar columnas disponibles
    with st.expander("📋 Ver columnas disponibles"):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write("**Inventario:**", list(inventario.columns))
        with col2:
            st.write("**Transacciones:**", list(transacciones.columns))
        with col3:
            st.write("**Feedback:**", list(feedback.columns))
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["📊 Calidad", "🔍 Exploración", "💰 Análisis"])
    
    # TAB 1: Calidad
    with tab1:
        st.subheader("Métricas de Calidad")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Inventario", f"{len(inventario):,}", f"{inventario.columns.size} columnas")
        with col2:
            st.metric("Transacciones", f"{len(transacciones):,}", f"{transacciones.columns.size} columnas")
        with col3:
            st.metric("Feedback", f"{len(feedback):,}", f"{feedback.columns.size} columnas")
        
        # Valores nulos
        st.markdown("**Valores Nulos**")
        st.dataframe(data.isnull().sum()[data.isnull().sum() > 0])
    
    # TAB 2: Exploración
    with tab2:
        st.subheader("Exploración de Datos")
        
        # Mostrar datos
        st.dataframe(data.head(20))
        
        # Estadísticas
        st.markdown("**Estadísticas Descriptivas**")
        st.dataframe(data.describe())
        
        # Gráfico simple
        if 'Categoria' in data.columns:
            st.markdown("**Distribución por Categoría**")
            fig = px.bar(data['Categoria'].value_counts())
            st.plotly_chart(fig, use_container_width=True)
    
    # TAB 3: Análisis
    with tab3:
        st.subheader("Análisis Estratégico")
        
        # Calcular métricas básicas
        if 'Precio_Venta' in data.columns and 'Costo_Unitario' in data.columns:
            data['Margen'] = (data['Precio_Venta'] - data['Costo_Unitario']) / data['Precio_Venta'] * 100
            
            st.markdown("**1. Márgenes de Utilidad**")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Margen Promedio", f"{data['Margen'].mean():.2f}%")
            with col2:
                neg_margin = len(data[data['Margen'] < 0])
                st.metric("SKUs Margen Negativo", f"{neg_margin:,}")
            
            # Gráfico
            fig = px.histogram(data, x='Margen', nbins=50)
            st.plotly_chart(fig, use_container_width=True)
        
        if 'NPS' in data.columns:
            st.markdown("**2. Satisfacción del Cliente**")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("NPS Promedio", f"{data['NPS'].mean():.2f}")
            with col2:
                detractores = len(data[data['NPS'] <= 6])
                st.metric("Detractores", f"{detractores:,}")
            with col3:
                promotores = len(data[data['NPS'] >= 9])
                st.metric("Promotores", f"{promotores:,}")
        
        # Descargar resultados
        st.markdown("---")
        csv = data.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Descargar Datos Integrados", csv, "datos_integrados.csv", "text/csv")

else:
    st.info("👆 Sube los 3 archivos CSV para comenzar el análisis")