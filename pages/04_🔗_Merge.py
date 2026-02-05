import streamlit as st
import pandas as pd
from utils.data_loader import display_dataframe_info, load_csv_file
from utils.session_init import init_session_state
from utils.data_cleaning import limpiar_inventario, limpiar_feedback, limpiar_transacciones, calcular_health_score, generar_audit_summary, contar_valores_invalidos
from utils.data_integration import integrar_datos, crear_metricas_nuevas

# Inicializar session state
init_session_state()

st.set_page_config(
    page_title="Merge",
    page_icon="🔗",
    layout="wide"
)

st.header("🔗 Fusionar Archivos")

# Advertencia importante
st.warning("⚠️ **Importante**: El merge se realiza OBLIGATORIAMENTE con datos limpios")

# Verificar que todos los archivos están cargados
if st.session_state.get('inventario_file') is not None and st.session_state.get('feedback_file') is not None and st.session_state.get('transacciones_file') is not None:
    try:
        # Cargar los tres archivos
        df_inventario_raw = load_csv_file(st.session_state.inventario_file)
        df_feedback_raw = load_csv_file(st.session_state.feedback_file)
        df_transacciones_raw = load_csv_file(st.session_state.transacciones_file)
        
        if df_inventario_raw is not None and df_feedback_raw is not None and df_transacciones_raw is not None:
            st.success("✅ Los tres archivos están cargados correctamente")
            
            # LIMPIAR OBLIGATORIAMENTE
            st.info("🧹 Limpiando datos automáticamente...")
            df_inventario = limpiar_inventario(df_inventario_raw)
            df_feedback = limpiar_feedback(df_feedback_raw)
            df_transacciones = limpiar_transacciones(df_transacciones_raw)
            
            # Mostrar comparación de health scores ANTES y DESPUÉS para cada dataset
            st.markdown("---")
            st.subheader("🏥 Salud de Datos - ANTES vs DESPUÉS de Limpieza")
            
            tab_inv, tab_feed, tab_trans = st.tabs(["📦 Inventario", "💬 Feedback", "💳 Transacciones"])
            
            with tab_inv:
                audit_inv = generar_audit_summary(df_inventario_raw, df_inventario, "Inventario")
                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    delta = audit_inv['health_score_despues'] - audit_inv['health_score_antes']
                    st.metric(
                        "Mejora Health Score",
                        f"{audit_inv['health_score_despues']:.1f}",
                        delta=f"{delta:+.1f}",
                        delta_color="inverse"
                    )
                with col2:
                    st.metric("Registros Eliminados", f"{audit_inv['registros_eliminados']} ({audit_inv['pct_registros_perdidos']:.2f}%)")
                with col3:
                    st.metric("Nulos Antes → Después", f"{audit_inv['nulos_antes']} → {audit_inv['nulos_despues']}")
                with col4:
                    pct_mejora = ((audit_inv['nulos_antes'] - audit_inv['nulos_despues']) / audit_inv['nulos_antes'] * 100) if audit_inv['nulos_antes'] > 0 else 0
                    st.metric("Reducción de Nulos", f"{pct_mejora:.1f}%")
                with col5:
                    st.metric("Valores Inválidos Eliminados", f"{audit_inv['valores_invalidos_antes']} → {audit_inv['valores_invalidos_despues']}")
            
            with tab_feed:
                audit_feed = generar_audit_summary(df_feedback_raw, df_feedback, "Feedback")
                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    delta = audit_feed['health_score_despues'] - audit_feed['health_score_antes']
                    st.metric(
                        "Mejora Health Score",
                        f"{audit_feed['health_score_despues']:.1f}",
                        delta=f"{delta:+.1f}",
                        delta_color="inverse"
                    )
                with col2:
                    st.metric("Registros Eliminados", f"{audit_feed['registros_eliminados']} ({audit_feed['pct_registros_perdidos']:.2f}%)")
                with col3:
                    st.metric("Nulos Antes → Después", f"{audit_feed['nulos_antes']} → {audit_feed['nulos_despues']}")
                with col4:
                    pct_mejora = ((audit_feed['nulos_antes'] - audit_feed['nulos_despues']) / audit_feed['nulos_antes'] * 100) if audit_feed['nulos_antes'] > 0 else 0
                    st.metric("Reducción de Nulos", f"{pct_mejora:.1f}%")
                with col5:
                    st.metric("Valores Inválidos Eliminados", f"{audit_feed['valores_invalidos_antes']} → {audit_feed['valores_invalidos_despues']}")
            
            with tab_trans:
                audit_trans = generar_audit_summary(df_transacciones_raw, df_transacciones, "Transacciones")
                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    delta = audit_trans['health_score_despues'] - audit_trans['health_score_antes']
                    st.metric(
                        "Mejora Health Score",
                        f"{audit_trans['health_score_despues']:.1f}",
                        delta=f"{delta:+.1f}",
                        delta_color="inverse"
                    )
                with col2:
                    st.metric("Registros Eliminados", f"{audit_trans['registros_eliminados']} ({audit_trans['pct_registros_perdidos']:.2f}%)")
                with col3:
                    st.metric("Nulos Antes → Después", f"{audit_trans['nulos_antes']} → {audit_trans['nulos_despues']}")
                with col4:
                    pct_mejora = ((audit_trans['nulos_antes'] - audit_trans['nulos_despues']) / audit_trans['nulos_antes'] * 100) if audit_trans['nulos_antes'] > 0 else 0
                    st.metric("Reducción de Nulos", f"{pct_mejora:.1f}%")
                with col5:
                    st.metric("Valores Inválidos Eliminados", f"{audit_trans['valores_invalidos_antes']} → {audit_trans['valores_invalidos_despues']}")
            
            st.markdown("---")
            
            # Mostrar información de cada archivo limpiado
            st.subheader("Estado de los Datos Limpiados")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Registros Inventario", len(df_inventario))
            with col2:
                st.metric("Registros Feedback", len(df_feedback))
            with col3:
                st.metric("Registros Transacciones", len(df_transacciones))
            
            st.markdown("---")
            st.subheader("Vista Previa de los Datos Limpios")
            
            tab1, tab2, tab3 = st.tabs(["Inventario", "Feedback", "Transacciones"])
            
            with tab1:
                st.write(df_inventario.head())
            
            with tab2:
                st.write(df_feedback.head())
            
            with tab3:
                st.write(df_transacciones.head())
            
            st.markdown("---")
            
            # Botón para realizar el merge
            if st.button("Ejecutar Integración de Datos"):
                with st.spinner("🔄 Integrando datos..."):
                    try:
                        # Verificar columnas disponibles
                        st.info("📋 Verificando columnas disponibles...")
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            trans_cols = df_transacciones.columns.tolist()
                            st.write(f"**Transacciones**: {len(trans_cols)} cols")
                        
                        with col2:
                            feed_cols = df_feedback.columns.tolist()
                            st.write(f"**Feedback**: {len(feed_cols)} cols")
                        
                        with col3:
                            inv_cols = df_inventario.columns.tolist()
                            st.write(f"**Inventario**: {len(inv_cols)} cols")
                        
                        # Usar la función integrar_datos
                        df_integrado = integrar_datos(df_transacciones, df_feedback, df_inventario)
                        
                        # Crear métricas nuevas
                        df_integrado = crear_metricas_nuevas(df_integrado)
                        
                        st.success(f"✅ Integración completada exitosamente - {len(df_integrado)} registros")
                        
                        # Mostrar health score del merge
                        st.markdown("---")
                        st.subheader("🏥 Salud del Merge Final")
                        health_merge = calcular_health_score(df_integrado)
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Health Score Merge", f"{health_merge:.1f}/100")
                        with col2:
                            st.metric("Registros Integrados", len(df_integrado))
                        with col3:
                            st.metric("Columnas Totales", len(df_integrado.columns))
                        with col4:
                            st.metric("Valores Nulos", int(df_integrado.isna().sum().sum()))
                        
                        st.markdown("---")
                        
                        st.subheader("Resultado de la Integración")
                        st.write(df_integrado)
                        
                        # Mostrar información de las nuevas columnas
                        st.subheader("Métricas Creadas")
                        cols_info = []
                        if 'Rating_Servicio' in df_integrado.columns:
                            cols_info.append("✅ **Rating_Servicio**: Combinación normalizada de Rating_Producto y Rating_Logistica")
                        if 'Margen' in df_integrado.columns:
                            cols_info.append("✅ **Margen**: Porcentaje de margen de ganancia por producto")
                        
                        if cols_info:
                            for info in cols_info:
                                st.info(info)
                        
                        # Mostrar estadísticas de nuevas métricas
                        if 'Rating_Servicio' in df_integrado.columns:
                            st.subheader("Estadísticas de Rating_Servicio")
                            st.write(df_integrado['Rating_Servicio'].describe())
                        
                        if 'Margen' in df_integrado.columns:
                            st.subheader("📊 Análisis de Márgenes y Ganancias")
                            
                            # Calcular ganancia neta
                            ganancia_neta = df_integrado['Margen'].sum()
                            margen_promedio = df_integrado['Margen'].mean()
                            margen_maximo = df_integrado['Margen'].max()
                            margen_minimo = df_integrado['Margen'].min()
                            
                            # Mostrar métricas principales
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                st.metric("💰 Ganancia Neta Total", f"${ganancia_neta:,.2f}")
                            with col2:
                                st.metric("📈 Margen Promedio", f"{margen_promedio:.2f}%")
                            with col3:
                                st.metric("⬆️ Margen Máximo", f"{margen_maximo:.2f}%")
                            with col4:
                                st.metric("⬇️ Margen Mínimo", f"{margen_minimo:.2f}%")
                            
                            # Mostrar estadísticas completas
                            st.subheader("Estadísticas Detalladas de Márgenes")
                            st.write(df_integrado['Margen'].describe())
                        
                        # Descargar resultado
                        csv = df_integrado.to_csv(index=False)
                        st.download_button(
                            label="📥 Descargar Datos Integrados (CSV)",
                            data=csv,
                            file_name="datos_integrados.csv",
                            mime="text/csv"
                        )
                    except Exception as e:
                        st.error(f"❌ Error durante la integración: {e}")
                        st.info(f"**Columnas encontradas:**")
                        
                        # Mostrar columnas disponibles
                        with st.expander("📊 Detalle de columnas"):
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.write("**Transacciones:**")
                                st.write(df_transacciones.columns.tolist())
                            with col2:
                                st.write("**Feedback:**")
                                st.write(df_feedback.columns.tolist())
                            with col3:
                                st.write("**Inventario:**")
                                st.write(df_inventario.columns.tolist())
    
    except Exception as e:
        st.error(f"❌ Error al procesar: {e}")
else:
    files_loaded = [
        st.session_state.get('inventario_file') is not None,
        st.session_state.get('feedback_file') is not None,
        st.session_state.get('transacciones_file') is not None
    ]
    missing = 3 - sum(files_loaded)
    st.warning(f"⚠️ Faltan {missing} archivo(s) por cargar. Por favor, carga los 3 archivos CSV en la barra lateral")
    
    st.info("""
    **Para usar esta funcionalidad necesitas:**
    - 📦 Inventario CSV
    - 💬 Feedback CSV
    - 💳 Transacciones CSV
    
    **Columnas requeridas para la integración:**
    - Transaccion_ID (en Feedback y Transacciones)
    - SKU_ID (en Inventario y Transacciones)
    """)
