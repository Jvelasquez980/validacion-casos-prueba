import streamlit as st
import pandas as pd
from utils.data_loader import display_dataframe_info, load_csv_file
from utils.session_init import init_session_state
from utils.data_cleaning import limpiar_inventario, generar_audit_summary, calcular_health_score, contar_valores_invalidos

# Inicializar session state
init_session_state()

st.set_page_config(
    page_title="Inventario",
    page_icon="📦",
    layout="wide"
)

st.header("📦 Inventario")

# Obtener el archivo del session state
if st.session_state.get('inventario_file') is not None:
    try:
        df = load_csv_file(st.session_state.inventario_file)
        if df is not None:
            st.success(f"✅ Archivo cargado: {len(df)} registros")
            
            # Crear tabs para mostrar datos sin limpiar y limpiados
            tab1, tab2 = st.tabs(["📊 Datos Sin Limpiar", "🧹 Datos Limpiados"])
            
            with tab1:
                st.subheader("Datos Originales")
                
                # Health Score antes de limpieza
                st.markdown("### 📊 Métricas de Calidad - ANTES de Limpieza")
                col1, col2, col3, col4, col5 = st.columns(5)
                health_score_antes = calcular_health_score(df)
                valores_invalidos_antes = contar_valores_invalidos(df)
                
                with col1:
                    st.metric("Health Score", f"{health_score_antes:.1f}/100")
                with col2:
                    st.metric("Registros", len(df))
                with col3:
                    st.metric("Columnas", len(df.columns))
                with col4:
                    st.metric("Valores Nulos", int(df.isna().sum().sum()))
                with col5:
                    st.metric("❌ Valores Inválidos", valores_invalidos_antes)
                
                st.markdown("---")
                display_dataframe_info(df)
                
                # Análisis adicional
                st.subheader("Análisis Detallado")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Columnas disponibles:**")
                    st.write(df.columns.tolist())
                
                with col2:
                    st.write("**Tipos de datos:**")
                    st.write(df.dtypes)
                
                # Descargar archivo original
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Descargar Inventario Original (CSV)",
                    data=csv,
                    file_name="inventario_original.csv",
                    mime="text/csv"
                )
            
            with tab2:
                st.subheader("Datos Limpiados")
                try:
                    df_limpio = limpiar_inventario(df)
                    
                    # Health Score después de limpieza
                    st.markdown("### 📊 Métricas de Calidad - DESPUÉS de Limpieza")
                    col1, col2, col3, col4, col5 = st.columns(5)
                    health_score_despues = calcular_health_score(df_limpio)
                    valores_invalidos_despues = contar_valores_invalidos(df_limpio)
                    with col1:
                        st.metric("Health Score", f"{health_score_despues:.1f}/100")
                    with col2:
                        st.metric("Registros", len(df_limpio))
                    with col3:
                        st.metric("Columnas", len(df_limpio.columns))
                    with col4:
                        st.metric("Valores Nulos", int(df_limpio.isna().sum().sum()))
                    with col5:
                        st.metric("❌ Valores Inválidos", valores_invalidos_despues)
                    
                    st.markdown("---")
                    
                    # Comparación antes y después
                    st.markdown("### 📈 Comparación ANTES vs DESPUÉS")
                    audit = generar_audit_summary(df, df_limpio, "Inventario")
                    
                    col1, col2, col3, col4, col5 = st.columns(5)
                    with col1:
                        delta = health_score_despues - health_score_antes
                        st.metric(
                            "Mejora Health Score",
                            f"{health_score_despues:.1f}",
                            delta=f"{delta:+.1f}",
                            delta_color="inverse"
                        )
                    with col2:
                        st.metric("Registros Eliminados", f"{audit['registros_eliminados']} ({audit['pct_registros_perdidos']:.2f}%)")
                    with col3:
                        st.metric("Nulos Antes → Después", f"{audit['nulos_antes']} → {audit['nulos_despues']}")
                    with col4:
                        pct_mejora_nulos = ((audit['nulos_antes'] - audit['nulos_despues']) / audit['nulos_antes'] * 100) if audit['nulos_antes'] > 0 else 0
                        st.metric("Reducción de Nulos", f"{pct_mejora_nulos:.1f}%")
                    with col5:
                        st.metric("Valores Inválidos Eliminados", f"{audit['valores_invalidos_antes']} → {audit['valores_invalidos_despues']}")
                    
                    st.markdown("---")
                    
                    # ========== FILTRO SIMPLE ==========
                    st.subheader("🎯 Filtrar Datos")
                    
                    filtro = st.radio(
                        "Mostrar registros donde Stock_Actual es mayor que:",
                        ['Todos', 'Media', 'Mediana', 'Moda'],
                        horizontal=True
                    )
                    
                    # USAR VARIABLE NUEVA
                    df_filtrado = df_limpio.copy()
                    
                    if filtro == 'Media':
                        valor = df_limpio['Stock_Actual'].mean()
                        df_filtrado = df_filtrado[df_filtrado['Stock_Actual'] > valor]
                        st.info(f"📊 Mostrando {len(df_filtrado)} registros con Stock_Actual > {valor:.2f}")
                    elif filtro == 'Mediana':
                        valor = df_limpio['Stock_Actual'].median()
                        df_filtrado = df_filtrado[df_filtrado['Stock_Actual'] > valor]
                        st.info(f"📊 Mostrando {len(df_filtrado)} registros con Stock_Actual > {valor:.2f}")
                    elif filtro == 'Moda':
                        valor = df_limpio['Stock_Actual'].mode()[0]
                        df_filtrado = df_filtrado[df_filtrado['Stock_Actual'] > valor]
                        st.info(f"📊 Mostrando {len(df_filtrado)} registros con Stock_Actual > {valor:.2f}")
                    
                    st.markdown("---")
                    # ========== FIN FILTRO ==========
                    
                    # MOSTRAR df_filtrado en vez de df_limpio
                    display_dataframe_info(df_filtrado)
                    
                    # Mostrar cambios realizados
                    st.subheader("Cambios Realizados")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Registros originales", len(df))
                    with col2:
                        st.metric("Registros después de filtros", len(df_filtrado))
                    
                    # Descargar archivo filtrado
                    csv_limpio = df_filtrado.to_csv(index=False)
                    st.download_button(
                        label="📥 Descargar Inventario Filtrado (CSV)",
                        data=csv_limpio,
                        file_name="inventario_filtrado.csv",
                        mime="text/csv"
                    )
                except Exception as e:
                    st.error(f"❌ Error al limpiar datos: {e}")
    
    except Exception as e:
        st.error(f"❌ Error al procesar: {e}")
else:
    st.info("📤 Por favor, carga un archivo CSV de Inventario en la barra lateral")
