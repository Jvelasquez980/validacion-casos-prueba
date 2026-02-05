import streamlit as st


def init_session_state():
    """Inicializa el session state con todas las variables necesarias"""
    if 'inventario_file' not in st.session_state:
        st.session_state.inventario_file = None
    if 'inventario_name' not in st.session_state:
        st.session_state.inventario_name = None
    if 'feedback_file' not in st.session_state:
        st.session_state.feedback_file = None
    if 'feedback_name' not in st.session_state:
        st.session_state.feedback_name = None
    if 'transacciones_file' not in st.session_state:
        st.session_state.transacciones_file = None
    if 'transacciones_name' not in st.session_state:
        st.session_state.transacciones_name = None
