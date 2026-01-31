import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path

# Configuración de la página
st.set_page_config(
    page_title="Dashboard de Análisis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal
st.title("📊 Dashboard de Análisis de Datos")
st.markdown("---")

# Sidebar
st.sidebar.header("Configuración")
dataset_option = st.sidebar.selectbox(
    "Selecciona el dataset:",
    ["Feedback Clientes", "Inventario Central", "Transacciones Logística"]
)

# Función para cargar datos
@st.cache_data
def load_data(dataset_name):
    data_path = Path("datasets")
    if dataset_name == "Feedback Clientes":
        df = pd.read_csv(data_path / "feedback_clientes_v2.csv")
    elif dataset_name == "Inventario Central":
        df = pd.read_csv(data_path / "inventario_central_v2.csv")
    else:  # Transacciones Logística
        df = pd.read_csv(data_path / "transacciones_logistica_v2.csv")
    return df

# Cargar datos
try:
    df = load_data(dataset_option)
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total de Registros",
            value=f"{len(df):,}"
        )
    
    with col2:
        st.metric(
            label="Columnas",
            value=len(df.columns)
        )
    
    with col3:
        st.metric(
            label="Valores Nulos",
            value=f"{df.isnull().sum().sum():,}"
        )
    
    with col4:
        st.metric(
            label="Duplicados",
            value=f"{df.duplicated().sum():,}"
        )
    
    st.markdown("---")
    
    # Tabs para diferentes vistas
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Datos", "📈 Estadísticas", "🔍 Información", "📊 Visualizaciones"])
    
    with tab1:
        st.subheader("Vista de Datos")
        st.dataframe(df, width='stretch', height=400)
        
        # Opción de descarga
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Descargar CSV",
            data=csv,
            file_name=f"{dataset_option.lower().replace(' ', '_')}.csv",
            mime="text/csv"
        )
    
    with tab2:
        st.subheader("Estadísticas Descriptivas")
        st.dataframe(df.describe(), width='stretch')
    
    with tab3:
        st.subheader("Información del Dataset")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Tipos de Datos:**")
            types_df = pd.DataFrame({
                'Columna': df.dtypes.index,
                'Tipo': df.dtypes.values.astype(str)
            })
            st.dataframe(types_df, width='stretch')
        
        with col2:
            st.write("**Valores Nulos por Columna:**")
            nulls_df = pd.DataFrame({
                'Columna': df.columns,
                'Nulos': df.isnull().sum().values,
                '% Nulos': (df.isnull().sum().values / len(df) * 100).round(2)
            })
            st.dataframe(nulls_df, width='stretch')
    
    with tab4:
        st.subheader("Visualizaciones")
        
        # Seleccionar columnas numéricas
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if numeric_cols:
            col1, col2 = st.columns(2)
            
            with col1:
                selected_col = st.selectbox("Selecciona una columna numérica:", numeric_cols)
            
            if selected_col:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Histograma**")
                    st.bar_chart(df[selected_col].value_counts().head(20))
                
                with col2:
                    st.write("**Distribución**")
                    st.line_chart(df[selected_col].sort_values().reset_index(drop=True))
        else:
            st.info("No hay columnas numéricas disponibles para visualizar.")

except FileNotFoundError:
    st.error(f"⚠️ No se pudo encontrar el archivo del dataset: {dataset_option}")
except Exception as e:
    st.error(f"⚠️ Error al cargar los datos: {str(e)}")

# Footer
st.markdown("---")
st.markdown("Dashboard creado con Streamlit 🎈")
