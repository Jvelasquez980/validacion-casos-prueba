"""
Dashboard Minimalista - TechLogistics
Análisis Simple de Datos
"""

import streamlit as st
import pandas as pd
import plotly.express as px

# 👉 NUEVO: importar auditoría del módulo
from data_cleaning import audit_quality

# 👉 Importar funciones de limpieza específicas
from limpieza_datos_transacciones import (
    corregir_nombres_ciudad_destino,
    corregir_canal_venta,
    corregir_valores_negativos_cantidad_vendida,
    reemplazar_outliers_tiempo_entrega_real,
    imputar_costo_envio,
    imputar_estado_envio
)

from limpieza_datos_inventario import (
    imputar_valores_columna_stock_actual,
    imputar_valores_columna_lead_time_dias,
    corregir_tipos_datos_punto_reorden,
    corregir_nombres_bodega_origen,
    limpiar_atipicos_costo_unitario,
    imputar_valores_columna_categoria
)

from limpieza_datos_feedback import (
    manejar_outliers_rating_producto,
    manejar_outliers_edad_cliente,
    imputar_valores_comentario_texto,
    imputar_valores_recomienda_marca
)

from integracion_datos import integrar_datos, crear_metricas_nuevas


# 👉 Usar Session State para mantener datos
if 'data_merged' not in st.session_state:
    st.session_state.data_merged = None
if 'data_with_metrics' not in st.session_state:
    st.session_state.data_with_metrics = None

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


# 👉 NUEVO: reglas invalid simples (robustas a columnas opcionales)
def build_invalid_rules_inventario():
    def stock_negative(df: pd.DataFrame):
        col = None
        for c in ["Stock_Actual", "Stock", "stock", "stock_actual"]:
            if c in df.columns:
                col = c
                break
        if col is None:
            return pd.Series([False] * len(df), index=df.index)
        return pd.to_numeric(df[col], errors="coerce") < 0

    return {"stock_negative": stock_negative}


def build_invalid_rules_transacciones():
    # Si existe una columna fecha, valida que no sea futura
    def future_sales(df: pd.DataFrame):
        # intenta varias opciones de nombre
        date_col = None
        for c in ["Fecha_Venta_dt", "Fecha_Venta", "fecha_venta", "Date", "date"]:
            if c in df.columns:
                date_col = c
                break
        if date_col is None:
            return pd.Series([False] * len(df), index=df.index)

        d = pd.to_datetime(df[date_col], errors="coerce", dayfirst=True)
        return d > pd.Timestamp.now()

    return {"future_sales": future_sales}


def build_invalid_rules_feedback():
    def age_impossible(df: pd.DataFrame):
        col = None
        for c in ["Edad_Cliente", "Edad", "age", "edad_cliente"]:
            if c in df.columns:
                col = c
                break
        if col is None:
            return pd.Series([False] * len(df), index=df.index)

        age = pd.to_numeric(df[col], errors="coerce")
        return (age < 10) | (age > 110)

    # NPS típico -100..100, pero si en tus datos es 0..10, esta regla no aplica.
    # La dejamos suave: solo se activa si hay valores fuera de [-100,100].
    def nps_out_of_range(df: pd.DataFrame):
        col = None
        for c in ["Satisfaccion_NPS", "NPS", "nps", "satisfaccion_nps"]:
            if c in df.columns:
                col = c
                break
        if col is None:
            return pd.Series([False] * len(df), index=df.index)

        nps = pd.to_numeric(df[col], errors="coerce")
        return (nps < -100) | (nps > 100)

    return {"age_impossible": age_impossible, "nps_out_of_range": nps_out_of_range}


# 👉 NUEVO: wrapper de auditoría robusto a nombres de columnas
def run_audit(df: pd.DataFrame, dataset_name: str, critical_candidates, numeric_candidates, invalid_rules):
    critical_cols = [c for c in critical_candidates if c in df.columns]
    numeric_cols = [c for c in numeric_candidates if c in df.columns]

    summary, nulls_table, outliers_table, excluded_rows_df = audit_quality(
        df=df,
        dataset_name=dataset_name,
        critical_cols=critical_cols,
        numeric_cols=numeric_cols,
        invalid_rules=invalid_rules
    )
    return {
        "summary": summary,
        "nulls": nulls_table,
        "outliers": outliers_table,
        "excluded": excluded_rows_df
    }


# Procesar si hay archivos
if inventario_file and transacciones_file and feedback_file:

    # Cargar datos
    inventario = pd.read_csv(inventario_file)
    transacciones = pd.read_csv(transacciones_file)
    feedback = pd.read_csv(feedback_file)

    # 👉 Si existen datos limpios en session_state, usarlos
    if 'inventario_clean' in st.session_state:
        inventario = st.session_state.inventario_clean
    if 'transacciones_clean' in st.session_state:
        transacciones = st.session_state.transacciones_clean
    if 'feedback_clean' in st.session_state:
        feedback = st.session_state.feedback_clean

    st.success(f"✅ Datos cargados: {len(inventario)} inv | {len(transacciones)} trx | {len(feedback)} fb")

    # 👉 NUEVA SECCIÓN: Limpieza de Datos
    st.markdown("---")
    st.header("🧹 Limpieza de Datos")
    
    # Crear tabs para opciones de limpieza
    clean_tab1, clean_tab2, clean_tab3 = st.tabs(["📦 Inventario", "🚚 Transacciones", "💬 Feedback"])
    
    with clean_tab1:
        st.subheader("Opciones de Limpieza - Inventario")
        
        col_opt1, col_opt2, col_opt3 = st.columns(3)
        
        with col_opt1:
            stock_replacement = st.selectbox(
                "Método para Stock_Actual",
                ["media", "mediana", "moda"],
                key="inv_stock"
            )
        
        with col_opt2:
            cost_replacement = st.selectbox(
                "Método para Costo_Unitario (atípicos)",
                ["Moda", "Mediana", "Promedio"],
                key="inv_cost"
            )
        
        with col_opt3:
            category_replacement = st.selectbox(
                "Método para Categoría (valores '???')",
                ["Mediana", "Moda", "Promedio"],
                key="inv_category"
            )
        
        if st.button("🔧 Limpiar Inventario", key="clean_inv"):
            try:
                # Orden correcto: normalizar → tipos → outliers → imputar
                inventario = corregir_nombres_bodega_origen(inventario)
                inventario = imputar_valores_columna_lead_time_dias(inventario)
                inventario = corregir_tipos_datos_punto_reorden(inventario)
                inventario = imputar_valores_columna_stock_actual(inventario, stock_replacement)
                # IMPORTANTE: Limpiar outliers de Costo ANTES de imputar Categoría
                inventario = limpiar_atipicos_costo_unitario(inventario, cost_replacement)
                # AHORA imputar Categoría (basándose en Costo limpio)
                inventario = imputar_valores_columna_categoria(inventario, category_replacement)
                # 👉 GUARDAR EN SESSION_STATE
                st.session_state.inventario_clean = inventario
                st.success("✅ Inventario limpiado exitosamente")
                st.info(f"Stock: {stock_replacement} | Costo: {cost_replacement} | Categoría: {category_replacement}")
            except Exception as e:
                st.error(f"❌ Error en limpieza de inventario: {str(e)}")
    
    with clean_tab2:
        st.subheader("Opciones de Limpieza - Transacciones")
        
        col_opt1, col_opt2, col_opt3 = st.columns(3)
        
        with col_opt1:
            tiempo_replacement = st.selectbox(
                "Método para Tiempo_Entrega_Real (outliers)",
                ["Mediana", "Media", "Limite", "Moda"],
                key="trx_tiempo"
            )
        
        with col_opt2:
            costo_replacement = st.selectbox(
                "Método para Costo_Envio (nulos)",
                ["Mediana", "Media", "Moda"],
                key="trx_costo"
            )
        
        with col_opt3:
            estado_replacement = st.selectbox(
                "Método para Estado_Envio (nulos)",
                ["Moda", "Mediana", "Media"],
                key="trx_estado"
            )
        
        if st.button("🔧 Limpiar Transacciones", key="clean_trx"):
            try:
                transacciones = corregir_nombres_ciudad_destino(transacciones)
                transacciones = corregir_canal_venta(transacciones)
                transacciones = corregir_valores_negativos_cantidad_vendida(transacciones)
                transacciones = reemplazar_outliers_tiempo_entrega_real(transacciones, tiempo_replacement)
                transacciones = imputar_costo_envio(transacciones, costo_replacement)
                transacciones = imputar_estado_envio(transacciones, estado_replacement)
                # 👉 GUARDAR EN SESSION_STATE
                st.session_state.transacciones_clean = transacciones
                st.success("✅ Transacciones limpias exitosamente")
                st.info(f"Tiempo: {tiempo_replacement} | Costo: {costo_replacement} | Estado: {estado_replacement}")
            except Exception as e:
                st.error(f"❌ Error en limpieza de transacciones: {str(e)}")
    
    with clean_tab3:
        st.subheader("Opciones de Limpieza - Feedback")
        
        col_opt1, col_opt2 = st.columns(2)
        
        with col_opt1:
            rating_replacement = st.selectbox(
                "Método para Rating_Producto (outliers)",
                ["Mediana", "Moda", "Media"],
                key="fb_rating"
            )
        
        with col_opt2:
            edad_replacement = st.selectbox(
                "Método para Edad_Cliente (outliers)",
                ["Mediana", "Moda", "Media"],
                key="fb_edad"
            )
        
        if st.button("🔧 Limpiar Feedback", key="clean_fb"):
            try:
                feedback = manejar_outliers_rating_producto(feedback, rating_replacement)
                feedback = manejar_outliers_edad_cliente(feedback, edad_replacement)
                feedback = imputar_valores_comentario_texto(feedback)
                feedback = imputar_valores_recomienda_marca(feedback)
                # 👉 GUARDAR EN SESSION_STATE
                st.session_state.feedback_clean = feedback
                st.success("✅ Feedback limpiado exitosamente")
                st.info(f"Rating: {rating_replacement} | Edad: {edad_replacement}")
            except Exception as e:
                st.error(f"❌ Error en limpieza de feedback: {str(e)}")

    st.markdown("---")
    st.header("📊 Merge de Datos")
    
    st.write("Realiza el merge de los datos limpios cuando estés listo.")
    
    if st.button("🔗 Realizar Merge", key="do_merge"):
        try:
            # 👉 USAR DATOS LIMPIOS si existen, sino usar originales
            trx_para_merge = st.session_state.get('transacciones_clean', transacciones)
            inv_para_merge = st.session_state.get('inventario_clean', inventario)
            fb_para_merge = st.session_state.get('feedback_clean', feedback)
            
            data = trx_para_merge.copy()

            # Merge con inventario
            if 'SKU_ID' in trx_para_merge.columns and 'SKU_ID' in inv_para_merge.columns:
                data = data.merge(inv_para_merge, on='SKU_ID', how='inner', suffixes=('', '_inv'))
            elif 'SKU' in trx_para_merge.columns and 'SKU' in inv_para_merge.columns:
                data = data.merge(inv_para_merge, on='SKU', how='inner', suffixes=('', '_inv'))

            # Merge con feedback
            if 'Transaccion_ID' in data.columns and 'Transaccion_ID' in fb_para_merge.columns:
                data = data.merge(fb_para_merge, on='Transaccion_ID', how='inner', suffixes=('', '_fb'))
            elif 'ID_Transaccion' in data.columns and 'ID_Transaccion' in fb_para_merge.columns:
                data = data.merge(fb_para_merge, on='ID_Transaccion', how='inner', suffixes=('', '_fb'))
            
            st.session_state.data_merged = data
            st.success(f"✅ Merge completado: {len(data):,} registros")
        except Exception as e:
            st.error(f"❌ Error en merge: {str(e)}")
    
    # Si hay datos merged, mostrar opción de crear métricas
    if st.session_state.data_merged is not None:
        st.markdown("---")
        st.header("📈 Métricas Derivadas")
        
        if st.button("📊 Crear Métricas Derivadas", key="create_metrics"):
            try:
                data_with_metrics = st.session_state.data_merged.copy()
                data_with_metrics = crear_metricas_nuevas(data_with_metrics)
                st.session_state.data_with_metrics = data_with_metrics
                st.success(f"✅ Métricas generadas exitosamente")
            except Exception as e:
                st.error(f"❌ Error en generación de métricas: {str(e)}")
        
        # Usar datos con métricas si existen, sino usar merged
        data = st.session_state.data_with_metrics if st.session_state.data_with_metrics is not None else st.session_state.data_merged
    else:
        data = None

    # Si no hay merge, crear dataframe vacío para evitar errores
    if data is None:
        data = pd.DataFrame()

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
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Calidad", "🔍 Exploración", "🔗 Merge", "💰 Análisis"])

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

        # Valores nulos (integrado)
        st.markdown("**Valores Nulos (Datos Integrados)**")
        st.dataframe(data.isnull().sum()[data.isnull().sum() > 0])

        st.markdown("---")
        st.subheader("🧪 Auditoría + Health Score")

        # 👉 Config candidatos (incluye variantes de nombres por si tu CSV usa otras etiquetas)
        inv_critical = ["SKU_ID", "SKU", "Costo_Unitario_USD", "Costo_Unitario", "Stock_Actual", "Stock"]
        inv_numeric = ["Costo_Unitario_USD", "Costo_Unitario", "Stock_Actual", "Stock", "Punto_Reorden", "Lead_Time_Dias"]

        trx_critical = ["Transaccion_ID", "ID_Transaccion", "SKU_ID", "SKU", "Fecha_Venta_dt", "Fecha_Venta",
                        "Tiempo_Entrega", "Cantidad_Vendida", "Precio_Venta_Final", "Precio_Venta"]
        trx_numeric = ["Tiempo_Entrega", "Cantidad_Vendida", "Precio_Venta_Final", "Precio_Venta", "Costo_Envio"]

        fb_critical = ["Transaccion_ID", "ID_Transaccion", "Satisfaccion_NPS", "NPS"]
        fb_numeric = ["Satisfaccion_NPS", "NPS", "Edad_Cliente", "Rating_Producto", "Rating_Logistica"]

        # Correr auditoría por dataset + integrado
        audit_inv = run_audit(inventario, "Inventario", inv_critical, inv_numeric, build_invalid_rules_inventario())
        audit_trx = run_audit(transacciones, "Transacciones", trx_critical, trx_numeric, build_invalid_rules_transacciones())
        audit_fb = run_audit(feedback, "Feedback", fb_critical, fb_numeric, build_invalid_rules_feedback())

        # Para integrado: usa críticos/números comunes
        integrated_critical = list(set(inv_critical + trx_critical + fb_critical))
        integrated_numeric = list(set(inv_numeric + trx_numeric + fb_numeric))
        audit_all = run_audit(data, "Integrado", integrated_critical, integrated_numeric, invalid_rules={})

        # KPIs Health Score
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Health Score - Inventario", f"{audit_inv['summary']['health_score']:.1f}")
        k2.metric("Health Score - Transacciones", f"{audit_trx['summary']['health_score']:.1f}")
        k3.metric("Health Score - Feedback", f"{audit_fb['summary']['health_score']:.1f}")
        k4.metric("Health Score - Integrado", f"{audit_all['summary']['health_score']:.1f}")

        # Detalles por dataset en tabs internas
        subtab1, subtab2, subtab3, subtab4 = st.tabs(["Inventario", "Transacciones", "Feedback", "Integrado"])

        def render_audit_block(audit_obj):
            s = audit_obj["summary"]

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("% Nulos global", f"{s['null_global_pct']:.2f}%")
            c2.metric("Duplicados", f"{s['dup_rows']}")
            c3.metric("Outliers (filas)", f"{s['outlier_rows_total']}")
            c4.metric("Invalids (filas)", f"{s['invalid_rows_total']}")

            st.markdown("**Nulidad por columna**")
            st.dataframe(audit_obj["nulls"])

            st.markdown("**Outliers por columna (IQR)**")
            st.dataframe(audit_obj["outliers"])

            with st.expander("Ver registros marcados (outliers/invalid)"):
                if audit_obj["excluded"].empty:
                    st.info("No hay registros marcados como excluidos.")
                else:
                    st.dataframe(audit_obj["excluded"])

        with subtab1:
            render_audit_block(audit_inv)

        with subtab2:
            render_audit_block(audit_trx)

        with subtab3:
            render_audit_block(audit_fb)

        with subtab4:
            render_audit_block(audit_all)

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

    # TAB 3: Merge (NUEVA PESTAÑA)
    with tab3:
        st.subheader("Visualización del Merge")
        
        if st.session_state.data_merged is None:
            st.info("👈 Realiza el merge en la sección anterior para ver los datos")
        else:
            st.success(f"✅ Datos merged: {len(st.session_state.data_merged):,} registros")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Filas Transacciones", len(transacciones))
            with col2:
                st.metric("Filas Merge", len(st.session_state.data_merged))
            
            st.markdown("**Vista Previa del Merge**")
            st.dataframe(st.session_state.data_merged.head(20))
            
            st.markdown("**Información del Merge**")
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Columnas:** {len(st.session_state.data_merged.columns)}")
            with col2:
                st.write(f"**Nulos totales:** {st.session_state.data_merged.isna().sum().sum()}")
            
            # Descargar merged
            csv = st.session_state.data_merged.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Descargar Datos Merged", csv, "datos_merged.csv", "text/csv")

    # TAB 4: Análisis (antes era TAB 3)
    with tab4:
        st.subheader("Análisis Estratégico")

        # Mostrar métricas derivadas si existen
        if 'Rating_Servicio' in data.columns:
            st.markdown("**📈 Métrica Integrada: Rating de Servicio**")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Rating Servicio Promedio", f"{data['Rating_Servicio'].mean():.2f}")
            with col2:
                rating_alto = len(data[data['Rating_Servicio'] >= 4])
                st.metric("Clientes Satisfechos (Rating >= 4)", f"{rating_alto:,}")
            with col3:
                rating_bajo = len(data[data['Rating_Servicio'] < 2])
                st.metric("Clientes Insatisfechos (Rating < 2)", f"{rating_bajo:,}")
            
            # Gráfico Rating Servicio
            fig = px.histogram(data, x='Rating_Servicio', nbins=20, title="Distribución Rating de Servicio")
            st.plotly_chart(fig, use_container_width=True)

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

        if 'Satisfaccion_NPS' in data.columns or 'NPS' in data.columns:
            nps_col = 'Satisfaccion_NPS' if 'Satisfaccion_NPS' in data.columns else 'NPS'
            st.markdown("**2. Satisfacción del Cliente**")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("NPS Promedio", f"{data[nps_col].mean():.2f}")
            with col2:
                detractores = len(data[data[nps_col] <= 6])
                st.metric("Detractores", f"{detractores:,}")
            with col3:
                promotores = len(data[data[nps_col] >= 9])
                st.metric("Promotores", f"{promotores:,}")

        # Descargar resultados
        st.markdown("---")
        csv = data.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Descargar Datos Integrados", csv, "datos_integrados.csv", "text/csv")

else:
    st.info("👆 Sube los 3 archivos CSV para comenzar el análisis")
