import streamlit as st
import io
from utils.session_init import init_session_state

# Inicializar session state
init_session_state()

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
    
    inventario_upload = st.file_uploader(
        "Inventario CSV",
        type="csv",
        key="inventario_upload"
    )
    if inventario_upload is not None:
        st.session_state.inventario_file = inventario_upload.getvalue()
        st.session_state.inventario_name = inventario_upload.name
    
    feedback_upload = st.file_uploader(
        "Feedback CSV",
        type="csv",
        key="feedback_upload"
    )
    if feedback_upload is not None:
        st.session_state.feedback_file = feedback_upload.getvalue()
        st.session_state.feedback_name = feedback_upload.name
    
    transacciones_upload = st.file_uploader(
        "Transacciones CSV",
        type="csv",
        key="transacciones_upload"
    )
    if transacciones_upload is not None:
        st.session_state.transacciones_file = transacciones_upload.getvalue()
        st.session_state.transacciones_name = transacciones_upload.name
    
    # Mostrar estado de carga
    st.markdown("---")
    st.subheader("Estado de Carga")
    col1, col2, col3 = st.columns(3)
    with col1:
        status_inv = "✅" if st.session_state.inventario_file is not None else "❌"
        st.write(f"{status_inv} Inventario")
    with col2:
        status_feed = "✅" if st.session_state.feedback_file is not None else "❌"
        st.write(f"{status_feed} Feedback")
    with col3:
        status_trans = "✅" if st.session_state.transacciones_file is not None else "❌"
        st.write(f"{status_trans} Transacciones")

# Contenido principal
st.header("Bienvenido a Validación de Casos de Prueba")
st.write("""
Esta aplicación te permite:
- 📦 Revisar datos de Inventario
- 💬 Analizar Feedback de Clientes
- 💳 Examinar Transacciones
- 🔗 Fusionar los tres archivos

**Carga los archivos CSV en la barra lateral para comenzar.**
""")

col1, col2, col3 = st.columns(3)
with col1:
    st.info("📦 Inventario", icon="ℹ️")
with col2:
    st.info("💬 Feedback", icon="ℹ️")
with col3:
    st.info("💳 Transacciones", icon="ℹ️")

st.markdown("---")
st.markdown("© 2026 - Validación de Casos de Prueba")
