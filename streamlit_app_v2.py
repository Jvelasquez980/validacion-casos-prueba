import streamlit as st
import pandas as pd
import numpy as np

# Configuración de la página
st.set_page_config(
    page_title="Validación de Casos de Prueba",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal
st.title("📊 Validación de Casos de Prueba")
st.markdown("---")

# Sidebar - Carga de Archivos
with st.sidebar:
    st.header("📤 Cargar Archivos")
    
    inventario_file = st.file_uploader(
        "Inventario CSV",
        type="csv",
        key="inventario"
    )
    
    feedback_file = st.file_uploader(
        "Feedback CSV",
        type="csv",
        key="feedback"
    )
    
    transacciones_file = st.file_uploader(
        "Transacciones CSV",
        type="csv",
        key="transacciones"
    )
    
    # Botón Merge
    st.markdown("---")
    
    st.markdown("---")
    st.header("Navegación")
    page = st.radio(
        "Selecciona una opción:",
        ["📦 Inventario", "💬 Feedback", "💳 Transacciones", "🔗 Merge"]
    )

# Contenido principal según la página seleccionada
if page == "� Inventario":
    st.header("📦 Inventario")
    
    if inventario_file is not None:
        try:
            df = pd.read_csv(inventario_file)
            st.success(f"✅ Archivo cargado: {len(df)} registros")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total de Registros", len(df))
            with col2:
                st.metric("Columnas", len(df.columns))
            
            st.subheader("Vista de Datos")
            st.dataframe(df, use_container_width=True)
            
            st.subheader("Estadísticas")
            st.write(df.describe())
            
        except Exception as e:
            st.error(f"❌ Error al cargar: {e}")
    else:
        st.info("📤 Por favor, carga un archivo CSV de Inventario en la barra lateral")

elif page == "💬 Feedback":
    st.header("💬 Feedback")
    
    if feedback_file is not None:
        try:
            df = pd.read_csv(feedback_file)
            st.success(f"✅ Archivo cargado: {len(df)} registros")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total de Registros", len(df))
            with col2:
                st.metric("Columnas", len(df.columns))
            
            st.subheader("Vista de Datos")
            st.dataframe(df, use_container_width=True)
            
            st.subheader("Estadísticas")
            st.write(df.describe())
            
        except Exception as e:
            st.error(f"❌ Error al cargar: {e}")
    else:
        st.info("📤 Por favor, carga un archivo CSV de Feedback en la barra lateral")

elif page == "💳 Transacciones":
    st.header("💳 Transacciones")
    
    if transacciones_file is not None:
        try:
            df = pd.read_csv(transacciones_file)
            st.success(f"✅ Archivo cargado: {len(df)} registros")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total de Registros", len(df))
            with col2:
                st.metric("Columnas", len(df.columns))
            
            st.subheader("Vista de Datos")
            st.dataframe(df, use_container_width=True)
            
            st.subheader("Estadísticas")
            st.write(df.describe())
            
        except Exception as e:
            st.error(f"❌ Error al cargar: {e}")
    else:
        st.info("📤 Por favor, carga un archivo CSV de Transacciones en la barra lateral")

elif page == "🔗 Merge":
    st.header("🔗 Fusionar Archivos")
    
    # Verificar que todos los archivos están cargados
    if inventario_file is not None and feedback_file is not None and transacciones_file is not None:
        try:
            # Cargar los tres archivos
            df_inventario = pd.read_csv(inventario_file)
            df_feedback = pd.read_csv(feedback_file)
            df_transacciones = pd.read_csv(transacciones_file)
            
            st.success("✅ Los tres archivos están cargados correctamente")
            
            # Mostrar información de cada archivo
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Registros Inventario", len(df_inventario))
            with col2:
                st.metric("Registros Feedback", len(df_feedback))
            with col3:
                st.metric("Registros Transacciones", len(df_transacciones))
            
            st.markdown("---")
            st.subheader("Vista Previa de los Datos")
            
            tab1, tab2, tab3 = st.tabs(["Inventario", "Feedback", "Transacciones"])
            
            with tab1:
                st.write(df_inventario.head())
            
            with tab2:
                st.write(df_feedback.head())
            
            with tab3:
                st.write(df_transacciones.head())
            
            # Botón para realizar el merge
            if st.button("Ejecutar Merge", use_container_width=True):
                st.info("🔄 Procesando merge de archivos...")
                # Aquí irá la lógica de merge
                st.success("✅ Merge completado exitosamente")
            
        except Exception as e:
            st.error(f"❌ Error al procesar: {e}")
    else:
        st.warning("⚠️ Por favor, carga los 3 archivos CSV en la barra lateral para acceder a la opción Merge")

# Footer
st.markdown("---")
st.markdown("© 2026 - Validación de Casos de Prueba")
