"""
Módulo de Pestañas - TechLogistics DSS
Contiene las funciones para renderizar cada pestaña del dashboard
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils import calculate_health_score, create_health_gauge


# ================================
# TAB 1: AUDITORÍA DE CALIDAD
# ================================

def render_quality_tab(inventario, transacciones, feedback):
    """Renderiza la pestaña de Auditoría de Calidad"""
    st.header("📊 Auditoría de Calidad de Datos")
    
    st.markdown("""
    Esta sección presenta el **Health Score** de cada dataset, calculado en base a:
    - **Completitud**: Porcentaje de datos sin valores nulos
    - **Unicidad**: Porcentaje de registros únicos (sin duplicados)
    """)
    
    # Calcular health scores
    health_scores = []
    if inventario is not None:
        health_scores.append(calculate_health_score(inventario, 'Inventario'))
    if transacciones is not None:
        health_scores.append(calculate_health_score(transacciones, 'Transacciones'))
    if feedback is not None:
        health_scores.append(calculate_health_score(feedback, 'Feedback'))
    
    # Mostrar KPIs
    col_layout = st.columns(len(health_scores))
    for idx, health in enumerate(health_scores):
        with col_layout[idx]:
            st.markdown('<div class="kpi-container">', unsafe_allow_html=True)
            icon = "📦" if health['dataset'] == 'Inventario' else "🚚" if health['dataset'] == 'Transacciones' else "💬"
            st.metric(
                label=f"{icon} {health['dataset']}",
                value=f"{health['health_score']}%",
                delta=f"{health['total_rows']:,} registros"
            )
            st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Gráficos de velocímetro
    st.subheader("🎯 Health Score por Dataset")
    gauge_cols = st.columns(len(health_scores))
    for idx, health in enumerate(health_scores):
        with gauge_cols[idx]:
            fig = create_health_gauge(health['health_score'], health['dataset'])
            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Tabla de métricas
    if health_scores:
        st.subheader("📋 Métricas Detalladas de Calidad")
        metrics_df = pd.DataFrame(health_scores)
        metrics_df = metrics_df[[
            'dataset', 'health_score', 'completeness', 'uniqueness',
            'total_rows', 'missing_values', 'duplicates'
        ]]
        metrics_df.columns = [
            'Dataset', 'Health Score (%)', 'Completitud (%)', 'Unicidad (%)',
            'Total Registros', 'Valores Faltantes', 'Duplicados'
        ]
        st.dataframe(metrics_df, use_container_width=True, hide_index=True)
    
    # Análisis de nulidad
    st.markdown("---")
    st.subheader("🔍 Análisis de Valores Faltantes por Columna")
    
    available_datasets = []
    dataset_map = {}
    if inventario is not None:
        available_datasets.append("Inventario")
        dataset_map["Inventario"] = inventario
    if transacciones is not None:
        available_datasets.append("Transacciones")
        dataset_map["Transacciones"] = transacciones
    if feedback is not None:
        available_datasets.append("Feedback")
        dataset_map["Feedback"] = feedback
    
    if available_datasets:
        dataset_choice = st.selectbox("Selecciona el dataset a analizar:", available_datasets)
        df_analysis = dataset_map[dataset_choice]
        
        null_percent = (df_analysis.isnull().sum() / len(df_analysis) * 100).sort_values(ascending=False)
        null_percent = null_percent[null_percent > 0]
        
        if len(null_percent) > 0:
            fig_null = px.bar(
                x=null_percent.values,
                y=null_percent.index,
                orientation='h',
                labels={'x': 'Porcentaje de Valores Faltantes (%)', 'y': 'Columna'},
                title=f"Valores Faltantes en {dataset_choice}",
                color=null_percent.values,
                color_continuous_scale='Reds'
            )
            fig_null.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig_null, use_container_width=True)
        else:
            st.success(f"✅ ¡Excelente! El dataset {dataset_choice} no tiene valores faltantes.")


# ================================
# TAB 2: EXPLORACIÓN DE DATOS
# ================================

def render_exploration_tab(filtered_data, inventario, transacciones, feedback):
    """Renderiza la pestaña de Exploración de Datos"""
    st.header("🔍 Exploración de Datos")
    
    # Selector de dataset
    available_datasets = ["Datos Filtrados"]
    dataset_map = {"Datos Filtrados": filtered_data}
    
    if inventario is not None:
        available_datasets.append("Inventario")
        dataset_map["Inventario"] = inventario
    if transacciones is not None:
        available_datasets.append("Transacciones")
        dataset_map["Transacciones"] = transacciones
    if feedback is not None:
        available_datasets.append("Feedback")
        dataset_map["Feedback"] = feedback
    
    dataset_eda = st.selectbox("Selecciona el dataset para análisis:", available_datasets, key="eda_dataset")
    df_eda = dataset_map[dataset_eda]
    
    st.write(f"**Dimensiones:** {df_eda.shape[0]} filas × {df_eda.shape[1]} columnas")
    
    # Estadísticas descriptivas
    st.subheader("📈 Estadísticas Descriptivas")
    stat_tab1, stat_tab2 = st.tabs(["Variables Numéricas", "Variables Categóricas"])
    
    with stat_tab1:
        numeric_cols = df_eda.select_dtypes(include=[np.number]).columns.tolist()
        if numeric_cols:
            st.dataframe(df_eda[numeric_cols].describe(), use_container_width=True)
        else:
            st.info("No hay variables numéricas en este dataset.")
    
    with stat_tab2:
        categorical_cols = df_eda.select_dtypes(include=['object']).columns.tolist()
        if categorical_cols:
            cat_summary = pd.DataFrame({
                'Columna': categorical_cols,
                'Valores Únicos': [df_eda[col].nunique() for col in categorical_cols],
                'Valor Más Frecuente': [df_eda[col].mode()[0] if len(df_eda[col].mode()) > 0 else 'N/A' for col in categorical_cols],
                'Frecuencia': [df_eda[col].value_counts().iloc[0] if len(df_eda[col]) > 0 else 0 for col in categorical_cols]
            })
            st.dataframe(cat_summary, use_container_width=True, hide_index=True)
        else:
            st.info("No hay variables categóricas en este dataset.")
    
    # Distribuciones
    st.markdown("---")
    st.subheader("📊 Distribuciones de Variables")
    
    col1, col2 = st.columns([2, 1])
    
    with col2:
        var_type = st.radio("Tipo de variable:", ["Numérica", "Categórica"])
        
        if var_type == "Numérica":
            available_vars = df_eda.select_dtypes(include=[np.number]).columns.tolist()
        else:
            available_vars = df_eda.select_dtypes(include=['object']).columns.tolist()
        
        if available_vars:
            selected_var = st.selectbox("Selecciona variable:", available_vars)
            if var_type == "Numérica":
                chart_type = st.radio("Tipo de gráfico:", ["Histograma", "Box Plot", "Violin Plot"])
    
    with col1:
        if available_vars:
            if var_type == "Numérica":
                if chart_type == "Histograma":
                    fig = px.histogram(df_eda, x=selected_var, nbins=30, title=f"Distribución de {selected_var}",
                                     color_discrete_sequence=['#1E2761'])
                elif chart_type == "Box Plot":
                    fig = px.box(df_eda, y=selected_var, title=f"Box Plot de {selected_var}",
                               color_discrete_sequence=['#1E2761'])
                else:
                    fig = px.violin(df_eda, y=selected_var, box=True, title=f"Violin Plot de {selected_var}",
                                  color_discrete_sequence=['#CADCFC'])
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
            else:
                value_counts = df_eda[selected_var].value_counts().head(15)
                fig = px.bar(x=value_counts.index, y=value_counts.values,
                           title=f"Distribución de {selected_var} (Top 15)",
                           labels={'x': selected_var, 'y': 'Frecuencia'},
                           color=value_counts.values, color_continuous_scale='Blues')
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(f"No hay variables {var_type.lower()}s disponibles en este dataset.")
    
    # Correlaciones
    st.markdown("---")
    st.subheader("🔗 Análisis de Correlaciones")
    
    numeric_cols = df_eda.select_dtypes(include=[np.number]).columns.tolist()
    
    if len(numeric_cols) >= 2:
        selected_cols = st.multiselect(
            "Selecciona variables para la matriz de correlación:",
            numeric_cols,
            default=numeric_cols[:min(6, len(numeric_cols))]
        )
        
        if len(selected_cols) >= 2:
            corr_matrix = df_eda[selected_cols].corr()
            fig = px.imshow(corr_matrix, text_auto='.2f', aspect='auto',
                          color_continuous_scale='RdBu_r', title="Matriz de Correlación")
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Se necesitan al menos 2 variables numéricas para calcular correlaciones.")


# ================================
# TAB 3: ANÁLISIS ESTRATÉGICO
# ================================

def render_strategic_tab(filtered_data):
    """Renderiza la pestaña de Análisis Estratégico"""
    st.header("💰 Análisis Estratégico - Preguntas de Alta Gerencia")
    
    st.markdown("""
    <div class="insight-box">
    <strong>💡 Nota:</strong> Esta sección requiere variables específicas en tus datos.
    Si alguna columna no existe, verás un mensaje de advertencia con las columnas requeridas.
    </div>
    """, unsafe_allow_html=True)
    
    q1, q2, q3, q4, q5 = st.tabs([
        "💸 Fuga de Capital",
        "🚚 Crisis Logística",
        "👻 Venta Invisible",
        "😞 Diagnóstico Fidelidad",
        "⚠️ Riesgo Operativo"
    ])
    
    # Importar las funciones específicas de cada análisis
    from tabs_strategic import (
        render_capital_leak,
        render_logistics_crisis,
        render_invisible_sales,
        render_loyalty_diagnosis,
        render_operational_risk
    )
    
    with q1:
        render_capital_leak(filtered_data)
    
    with q2:
        render_logistics_crisis(filtered_data)
    
    with q3:
        render_invisible_sales(filtered_data)
    
    with q4:
        render_loyalty_diagnosis(filtered_data)
    
    with q5:
        render_operational_risk(filtered_data)


# ================================
# TAB 4: RECOMENDACIONES IA
# ================================

def render_ai_tab(filtered_data):
    """Renderiza la pestaña de Recomendaciones con IA"""
    st.header("🤖 Recomendaciones de Inteligencia Artificial")
    
    # Importar la función de IA
    from tabs_ai import render_ai_recommendations
    render_ai_recommendations(filtered_data)