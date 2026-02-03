"""
Dashboard Minimalista - TechLogistics
Análisis Simple de Datos
"""

import streamlit as st
import pandas as pd
import plotly.express as px

# 👉 NUEVO: importar auditoría del módulo
from data_cleaning import audit_quality


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
