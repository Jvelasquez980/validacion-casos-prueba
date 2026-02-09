import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import time
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
                        
                        # ==========================================
                        # SECCIÓN DE GRÁFICAS ANALÍTICAS INTEGRADAS
                        # ==========================================
                        st.markdown("---")
                        st.header("📊 ANÁLISIS INTEGRADO - 10 CATEGORÍAS")
                        
                        # Preparación de datos
                        df_dash = df_integrado.copy()
                        df_dash['Fecha_Venta'] = pd.to_datetime(df_dash['Fecha_Venta'], errors='coerce')
                        df_dash['Revenue'] = df_dash['Cantidad_Vendida'] * df_dash['Precio_Venta_Final']
                        
                        # Colores estandarizados
                        color_canal = {'Físico': '#3498db', 'Online': '#e74c3c'}
                        color_estado = {'Entregado': '#2ecc71', 'En_Transito': '#3498db', 'Perdido': '#e74c3c', 'Retrasado': '#f39c12'}
                        
                        # ==========================================
                        # 1. KPIs PRINCIPALES Y TOP PERFORMERS
                        # ==========================================
                        st.markdown("### 1️⃣ KPIs Principales - Revenue & Profitability")
                        
                        revenue_total = df_dash['Revenue'].sum()
                        ganancia_total = df_dash['Margen'].sum()
                        margen_pct = (ganancia_total / revenue_total * 100) if revenue_total > 0 else 0
                        aov = df_dash['Revenue'].mean()
                        
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            fig_revenue = go.Figure(go.Indicator(
                                mode="gauge+number+delta",
                                value=revenue_total,
                                title={'text': "Revenue Total"},
                                domain={'x': [0, 1], 'y': [0, 1]},
                                gauge={'axis': {'range': [0, revenue_total * 1.2]},
                                       'bar': {'color': '#3498db'},
                                       'steps': [
                                           {'range': [0, revenue_total * 0.5], 'color': '#ecf0f1'},
                                           {'range': [revenue_total * 0.5, revenue_total], 'color': '#d5dbdb'}
                                       ],
                                       'threshold': {'line': {'color': 'red', 'width': 4},
                                                    'thickness': 0.75,
                                                    'value': revenue_total * 1.1}
                                }
                            ))
                            fig_revenue.update_layout(height=300, font=dict(size=12))
                            st.plotly_chart(fig_revenue, use_container_width=True)
                        
                        with col2:
                            fig_ganancia = go.Figure(go.Indicator(
                                mode="gauge+number+delta",
                                value=ganancia_total,
                                title={'text': "Ganancia Neta"},
                                domain={'x': [0, 1], 'y': [0, 1]},
                                gauge={'axis': {'range': [0, ganancia_total * 1.2]},
                                       'bar': {'color': '#2ecc71'},
                                       'steps': [
                                           {'range': [0, ganancia_total * 0.5], 'color': '#ecf0f1'},
                                           {'range': [ganancia_total * 0.5, ganancia_total], 'color': '#d5dbdb'}
                                       ]
                                }
                            ))
                            fig_ganancia.update_layout(height=300, font=dict(size=12))
                            st.plotly_chart(fig_ganancia, use_container_width=True)
                        
                        with col3:
                            fig_margen = go.Figure(go.Indicator(
                                mode="gauge+number",
                                value=margen_pct,
                                title={'text': "Margen %"},
                                domain={'x': [0, 1], 'y': [0, 1]},
                                gauge={'axis': {'range': [0, 100]},
                                       'bar': {'color': '#f39c12'},
                                       'steps': [
                                           {'range': [0, 25], 'color': '#ecf0f1'},
                                           {'range': [25, 50], 'color': '#d5dbdb'}
                                       ],
                                       'threshold': {'line': {'color': 'red', 'width': 4},
                                                    'thickness': 0.75,
                                                    'value': 80}
                                },
                                number={'valueformat': '.1f', 'suffix': ' %'}
                            ))
                            fig_margen.update_layout(height=300, font=dict(size=12))
                            st.plotly_chart(fig_margen, use_container_width=True)
                        
                        with col4:
                            fig_aov = go.Figure(go.Indicator(
                                mode="number",
                                value=aov,
                                title={'text': "AOV (Promedio)<br><sub>$</sub>"},
                                domain={'x': [0, 1], 'y': [0, 1]},
                                number={'valueformat': ',.2f'}
                            ))
                            fig_aov.update_layout(height=300, font=dict(size=12))
                            st.plotly_chart(fig_aov, use_container_width=True)
                        
                        st.markdown("---")
                        
                        # Top 10 Productos por Revenue
                        st.markdown("### 2️⃣ Top Performers")
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            top_productos_rev = df_dash.groupby('SKU_ID').agg({
                                'Revenue': 'sum',
                                'Margen': 'sum',
                                'Cantidad_Vendida': 'sum'
                            }).sort_values('Revenue', ascending=False).head(10)
                            
                            fig_prod_rev = px.bar(
                                x=top_productos_rev['Revenue'].values,
                                y=top_productos_rev.index.astype(str),
                                orientation='h',
                                title='💰 Top 10 Productos por Revenue',
                                labels={'x': 'Revenue ($)', 'y': 'SKU_ID'},
                                color=top_productos_rev['Revenue'].values,
                                color_continuous_scale='Blues'
                            )
                            fig_prod_rev.update_layout(height=400, showlegend=False)
                            st.plotly_chart(fig_prod_rev, use_container_width=True)
                        
                        with col2:
                            top_ciudades = df_dash.groupby('Ciudad_Destino')['Revenue'].sum().sort_values(ascending=False).head(10)
                            
                            fig_ciudades = px.bar(
                                x=top_ciudades.values,
                                y=top_ciudades.index,
                                orientation='h',
                                title='🏙️ Top 10 Ciudades por Revenue',
                                labels={'x': 'Revenue ($)', 'y': 'Ciudad'},
                                color=top_ciudades.values,
                                color_continuous_scale='Viridis'
                            )
                            fig_ciudades.update_layout(height=400, showlegend=False)
                            st.plotly_chart(fig_ciudades, use_container_width=True)
                        
                        with col3:
                            canal_rentabilidad = df_dash.groupby('Canal_Venta').agg({
                                'Revenue': 'sum',
                                'Margen': 'sum'
                            })
                            canal_rentabilidad['Margen_Pct'] = (canal_rentabilidad['Margen'] / canal_rentabilidad['Revenue'] * 100)
                            
                            fig_canal_rent = px.bar(
                                x=canal_rentabilidad.index,
                                y=canal_rentabilidad['Margen_Pct'],
                                title='📈 Rentabilidad por Canal (%)',
                                labels={'x': 'Canal', 'y': 'Margen %'},
                                color=canal_rentabilidad['Margen_Pct'],
                                color_continuous_scale='RdYlGn',
                                text=canal_rentabilidad['Margen_Pct'].round(1)
                            )
                            fig_canal_rent.update_traces(textposition='auto')
                            fig_canal_rent.update_layout(height=400, showlegend=False)
                            st.plotly_chart(fig_canal_rent, use_container_width=True)
                        
                        st.markdown("---")
                        
                        # ==========================================
                        # 3. CORRELACIONES MULTIVARIADAS
                        # ==========================================
                        st.markdown("### 3️⃣ Análisis de Correlaciones")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # Rating vs Revenue
                            fig_rating_rev = px.scatter(
                                df_dash,
                                x='Rating_Producto',
                                y='Revenue',
                                color='Canal_Venta',
                                size='Cantidad_Vendida',
                                title='⭐ Rating Producto vs Revenue',
                                labels={'Rating_Producto': 'Rating Producto', 'Revenue': 'Revenue ($)'},
                                color_discrete_map=color_canal,
                                opacity=0.6,
                                hover_data={'Cantidad_Vendida': ':.0f', 'Margen': ':.2f'}
                            )
                            fig_rating_rev.update_layout(height=400)
                            st.plotly_chart(fig_rating_rev, use_container_width=True)
                        
                        with col2:
                            # Stock vs Cantidad Vendida
                            stock_qty = df_dash.groupby('SKU_ID').agg({
                                'Stock_Actual': 'first',
                                'Cantidad_Vendida': 'sum',
                                'Categoria': 'first'
                            }).reset_index()
                            
                            fig_stock_qty = px.scatter(
                                stock_qty,
                                x='Stock_Actual',
                                y='Cantidad_Vendida',
                                color='Categoria',
                                title='📦 Stock Actual vs Cantidad Vendida',
                                labels={'Stock_Actual': 'Stock Actual', 'Cantidad_Vendida': 'Cantidad Vendida'},
                                size='Stock_Actual',
                                opacity=0.6,
                                color_continuous_scale='Plasma'
                            )
                            fig_stock_qty.update_layout(height=400)
                            st.plotly_chart(fig_stock_qty, use_container_width=True)
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # NPS vs Revenue
                            nps_rev = df_dash[['Satisfaccion_NPS', 'Revenue', 'Rating_Producto', 'Canal_Venta']].copy()
                            nps_rev['NPS_Scaled'] = (nps_rev['Satisfaccion_NPS'] + 100) / 2
                            
                            fig_nps_rev = px.scatter(
                                nps_rev,
                                x='Satisfaccion_NPS',
                                y='Revenue',
                                size='NPS_Scaled',
                                color='Rating_Producto',
                                title='📊 NPS vs Revenue',
                                labels={'Satisfaccion_NPS': 'NPS Score', 'Revenue': 'Revenue ($)'},
                                color_continuous_scale='RdYlGn',
                                opacity=0.6
                            )
                            fig_nps_rev.update_layout(height=400)
                            st.plotly_chart(fig_nps_rev, use_container_width=True)
                        
                        with col2:
                            # Costo vs Margen
                            fig_costo_margen = px.scatter(
                                df_dash,
                                x='Costo_Envio',
                                y='Margen',
                                color='Estado_Envio',
                                title='💳 Costo Envío vs Margen',
                                labels={'Costo_Envio': 'Costo Envío ($)', 'Margen': 'Margen ($)'},
                                color_discrete_map=color_estado,
                                opacity=0.6,
                                size='Cantidad_Vendida'
                            )
                            fig_costo_margen.update_layout(height=400)
                            st.plotly_chart(fig_costo_margen, use_container_width=True)
                        
                        st.markdown("---")
                        
                        # ==========================================
                        # 4. ANÁLISIS POR CATEGORÍA
                        # ==========================================
                        st.markdown("### 4️⃣ Análisis por Categoría")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            cat_analysis = df_dash.groupby('Categoria').agg({
                                'Revenue': 'sum',
                                'Margen': 'sum',
                                'Cantidad_Vendida': 'sum',
                                'Rating_Producto': 'mean'
                            }).sort_values('Revenue', ascending=False)
                            
                            fig_cat_rev = px.bar(
                                x=cat_analysis.index,
                                y=cat_analysis['Revenue'],
                                title='💰 Revenue por Categoría',
                                labels={'x': 'Categoría', 'y': 'Revenue ($)'},
                                color=cat_analysis['Revenue'],
                                color_continuous_scale='Blues',
                                text=cat_analysis['Revenue'].round(0)
                            )
                            fig_cat_rev.update_traces(textposition='auto')
                            fig_cat_rev.update_layout(height=400, showlegend=False, xaxis_tickangle=-45)
                            st.plotly_chart(fig_cat_rev, use_container_width=True)
                        
                        with col2:
                            fig_cat_margen = px.bar(
                                x=cat_analysis.index,
                                y=cat_analysis['Margen'],
                                title='📈 Ganancia por Categoría',
                                labels={'x': 'Categoría', 'y': 'Ganancia ($)'},
                                color=cat_analysis['Margen'],
                                color_continuous_scale='Greens',
                                text=cat_analysis['Margen'].round(0)
                            )
                            fig_cat_margen.update_traces(textposition='auto')
                            fig_cat_margen.update_layout(height=400, showlegend=False, xaxis_tickangle=-45)
                            st.plotly_chart(fig_cat_margen, use_container_width=True)
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            fig_cat_rating = px.bar(
                                x=cat_analysis.index,
                                y=cat_analysis['Rating_Producto'],
                                title='⭐ Rating Promedio por Categoría',
                                labels={'x': 'Categoría', 'y': 'Rating Promedio'},
                                color=cat_analysis['Rating_Producto'],
                                color_continuous_scale='RdYlGn',
                                text=cat_analysis['Rating_Producto'].round(2)
                            )
                            fig_cat_rating.update_traces(textposition='auto')
                            fig_cat_rating.update_layout(height=400, showlegend=False, xaxis_tickangle=-45)
                            st.plotly_chart(fig_cat_rating, use_container_width=True)
                        
                        with col2:
                            cat_margen_pct = (cat_analysis['Margen'] / cat_analysis['Revenue'] * 100).sort_values(ascending=False)
                            fig_cat_margen_pct = px.bar(
                                x=cat_margen_pct.index,
                                y=cat_margen_pct.values,
                                title='📊 Margen % por Categoría',
                                labels={'x': 'Categoría', 'y': 'Margen %'},
                                color=cat_margen_pct.values,
                                color_continuous_scale='RdYlGn',
                                text=cat_margen_pct.round(1)
                            )
                            fig_cat_margen_pct.update_traces(textposition='auto')
                            fig_cat_margen_pct.update_layout(height=400, showlegend=False, xaxis_tickangle=-45)
                            st.plotly_chart(fig_cat_margen_pct, use_container_width=True)
                        
                        st.markdown("---")
                        
                        # ==========================================
                        # 5. ANÁLISIS POR CANAL
                        # ==========================================
                        st.markdown("### 5️⃣ Análisis por Canal de Venta")
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            canal_dist = df_dash['Canal_Venta'].value_counts()
                            fig_canal_dist = px.pie(
                                values=canal_dist.values,
                                names=canal_dist.index,
                                title='📊 Distribución por Canal',
                                color_discrete_map=color_canal,
                                labels={'value': 'Transacciones'}
                            )
                            fig_canal_dist.update_layout(height=350)
                            st.plotly_chart(fig_canal_dist, use_container_width=True)
                        
                        with col2:
                            canal_rev = df_dash.groupby('Canal_Venta')['Revenue'].sum()
                            fig_canal_rev_pie = px.pie(
                                values=canal_rev.values,
                                names=canal_rev.index,
                                title='💰 Revenue por Canal',
                                color_discrete_map=color_canal,
                                labels={'value': 'Revenue ($)'}
                            )
                            fig_canal_rev_pie.update_layout(height=350)
                            st.plotly_chart(fig_canal_rev_pie, use_container_width=True)
                        
                        with col3:
                            canal_nps = df_dash.groupby('Canal_Venta')['Satisfaccion_NPS'].mean()
                            fig_canal_nps = px.bar(
                                x=canal_nps.index,
                                y=canal_nps.values,
                                title='📈 NPS Promedio por Canal',
                                labels={'x': 'Canal', 'y': 'NPS'},
                                color=canal_nps.values,
                                color_continuous_scale='RdYlGn',
                                text=canal_nps.round(1)
                            )
                            fig_canal_nps.update_traces(textposition='auto')
                            fig_canal_nps.update_layout(height=350, showlegend=False)
                            st.plotly_chart(fig_canal_nps, use_container_width=True)
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            canal_costo = df_dash.groupby('Canal_Venta')['Costo_Envio'].mean().sort_values(ascending=False)
                            fig_canal_costo = px.bar(
                                x=canal_costo.index,
                                y=canal_costo.values,
                                title='💳 Costo Promedio Envío por Canal',
                                labels={'x': 'Canal', 'y': 'Costo Promedio ($)'},
                                color=canal_costo.values,
                                color_continuous_scale='Oranges',
                                text=canal_costo.round(2)
                            )
                            fig_canal_costo.update_traces(textposition='auto')
                            fig_canal_costo.update_layout(height=350, showlegend=False)
                            st.plotly_chart(fig_canal_costo, use_container_width=True)
                        
                        with col2:
                            canal_margen = df_dash.groupby('Canal_Venta')['Margen'].mean().sort_values(ascending=False)
                            fig_canal_margen = px.bar(
                                x=canal_margen.index,
                                y=canal_margen.values,
                                title='📊 Margen Promedio por Canal',
                                labels={'x': 'Canal', 'y': 'Margen Promedio ($)'},
                                color=canal_margen.values,
                                color_continuous_scale='Greens',
                                text=canal_margen.round(2)
                            )
                            fig_canal_margen.update_traces(textposition='auto')
                            fig_canal_margen.update_layout(height=350, showlegend=False)
                            st.plotly_chart(fig_canal_margen, use_container_width=True)
                        
                        st.markdown("---")
                        
                        # ==========================================
                        # 6. ANÁLISIS GEOGRÁFICO
                        # ==========================================
                        st.markdown("### 6️⃣ Análisis Geográfico")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            geo_rev = df_dash.groupby('Ciudad_Destino')['Revenue'].sum().sort_values(ascending=False).head(15)
                            fig_geo_rev = px.bar(
                                y=geo_rev.index,
                                x=geo_rev.values,
                                orientation='h',
                                title='💰 Top 15 Ciudades por Revenue',
                                labels={'x': 'Revenue ($)', 'y': 'Ciudad'},
                                color=geo_rev.values,
                                color_continuous_scale='Blues'
                            )
                            fig_geo_rev.update_layout(height=450, showlegend=False)
                            st.plotly_chart(fig_geo_rev, use_container_width=True)
                        
                        with col2:
                            geo_entregas = pd.crosstab(df_dash['Ciudad_Destino'], df_dash['Estado_Envio']).head(15)
                            fig_geo_entregas = px.bar(
                                geo_entregas,
                                title='📦 Entregas por Estado por Ciudad (Top 15)',
                                labels={'value': 'Entregas', 'Ciudad_Destino': 'Ciudad'},
                                barmode='stack',
                                color_discrete_map=color_estado
                            )
                            fig_geo_entregas.update_layout(height=450, xaxis_tickangle=-45)
                            st.plotly_chart(fig_geo_entregas, use_container_width=True)
                        
                        # Heatmap Ciudad vs Categoría
                        geo_cat_heat = pd.crosstab(
                            df_dash['Ciudad_Destino'],
                            df_dash['Categoria'],
                            values=df_dash['Revenue'],
                            aggfunc='sum'
                        ).fillna(0)
                        
                        # Top 15 ciudades
                        top_ciudades_list = df_dash['Ciudad_Destino'].value_counts().head(15).index
                        geo_cat_heat = geo_cat_heat.loc[top_ciudades_list]
                        
                        fig_geo_heat = px.imshow(
                            geo_cat_heat,
                            title='🔥 Heatmap: Revenue por Ciudad-Categoría (Top 15 Ciudades)',
                            color_continuous_scale='YlOrRd',
                            labels={'x': 'Categoría', 'y': 'Ciudad', 'color': 'Revenue ($)'},
                            aspect='auto'
                        )
                        fig_geo_heat.update_layout(height=450)
                        st.plotly_chart(fig_geo_heat, use_container_width=True)
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            geo_rating = df_dash.groupby('Ciudad_Destino')['Rating_Producto'].mean().sort_values(ascending=False).head(10)
                            fig_geo_rating = px.bar(
                                x=geo_rating.values,
                                y=geo_rating.index,
                                orientation='h',
                                title='⭐ Rating Promedio por Ciudad (Top 10)',
                                labels={'x': 'Rating Promedio', 'y': 'Ciudad'},
                                color=geo_rating.values,
                                color_continuous_scale='RdYlGn'
                            )
                            fig_geo_rating.update_layout(height=350, showlegend=False)
                            st.plotly_chart(fig_geo_rating, use_container_width=True)
                        
                        with col2:
                            geo_entrega_pct = df_dash[df_dash['Estado_Envio'] == 'Entregado'].groupby('Ciudad_Destino').size() / df_dash.groupby('Ciudad_Destino').size() * 100
                            geo_entrega_pct = geo_entrega_pct.sort_values(ascending=False).head(10)
                            fig_geo_entrega_pct = px.bar(
                                x=geo_entrega_pct.values,
                                y=geo_entrega_pct.index,
                                orientation='h',
                                title='✅ % Entregas Exitosas por Ciudad (Top 10)',
                                labels={'x': '% Entregas', 'y': 'Ciudad'},
                                color=geo_entrega_pct.values,
                                color_continuous_scale='Greens',
                                text=geo_entrega_pct.round(1)
                            )
                            fig_geo_entrega_pct.update_traces(textposition='auto')
                            fig_geo_entrega_pct.update_layout(height=350, showlegend=False)
                            st.plotly_chart(fig_geo_entrega_pct, use_container_width=True)
                        
                        st.markdown("---")
                        
                        # ==========================================
                        # 7. ANÁLISIS TEMPORAL Y ESTADO
                        # ==========================================
                        st.markdown("### 7️⃣ Análisis Temporal & Estado de Entregas")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # Timeline Revenue Acumulado
                            timeline_rev = df_dash.groupby(df_dash['Fecha_Venta'].dt.date)['Revenue'].sum().reset_index()
                            timeline_rev['Revenue_Acumulado'] = timeline_rev['Revenue'].cumsum()
                            
                            fig_timeline_rev = px.line(
                                timeline_rev,
                                x='Fecha_Venta',
                                y='Revenue_Acumulado',
                                title='📈 Revenue Acumulado en el Tiempo',
                                labels={'Fecha_Venta': 'Fecha', 'Revenue_Acumulado': 'Revenue Acumulado ($)'},
                                markers=True,
                                line_shape='linear'
                            )
                            fig_timeline_rev.update_traces(line=dict(color='#3498db', width=3), marker=dict(size=5))
                            fig_timeline_rev.update_layout(height=350, hovermode='x unified')
                            st.plotly_chart(fig_timeline_rev, use_container_width=True)
                        
                        with col2:
                            # Timeline Ganancia Acumulada
                            timeline_gan = df_dash.groupby(df_dash['Fecha_Venta'].dt.date)['Margen'].sum().reset_index()
                            timeline_gan['Ganancia_Acumulada'] = timeline_gan['Margen'].cumsum()
                            
                            fig_timeline_gan = px.line(
                                timeline_gan,
                                x='Fecha_Venta',
                                y='Ganancia_Acumulada',
                                title='💰 Ganancia Acumulada en el Tiempo',
                                labels={'Fecha_Venta': 'Fecha', 'Ganancia_Acumulada': 'Ganancia Acumulada ($)'},
                                markers=True,
                                line_shape='linear'
                            )
                            fig_timeline_gan.update_traces(line=dict(color='#2ecc71', width=3), marker=dict(size=5))
                            fig_timeline_gan.update_layout(height=350, hovermode='x unified')
                            st.plotly_chart(fig_timeline_gan, use_container_width=True)
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # % Entregas por estado
                            estado_dist = df_dash['Estado_Envio'].value_counts()
                            estado_pct = (estado_dist / estado_dist.sum() * 100)
                            fig_estado_pct = px.pie(
                                values=estado_dist.values,
                                names=estado_dist.index,
                                title='📊 Distribución de Estado de Entregas',
                                color_discrete_map=color_estado,
                                labels={'value': 'Transacciones'}
                            )
                            fig_estado_pct.update_layout(height=350)
                            st.plotly_chart(fig_estado_pct, use_container_width=True)
                        
                        with col2:
                            # Tickets vs Revenue por estado
                            estado_metricas = df_dash.groupby('Estado_Envio').agg({
                                'Revenue': 'sum',
                                'Rating_Producto': 'mean',
                                'Transaccion_ID': 'count'
                            }).round(2)
                            
                            fig_estado_rev = px.bar(
                                x=estado_metricas.index,
                                y=estado_metricas['Revenue'],
                                title='💰 Revenue por Estado',
                                labels={'x': 'Estado', 'y': 'Revenue ($)'},
                                color=estado_metricas['Revenue'],
                                color_discrete_map={estado: color_estado.get(estado, '#95a5a6') for estado in estado_metricas.index},
                                text=estado_metricas['Revenue'].round(0)
                            )
                            fig_estado_rev.update_traces(textposition='auto')
                            fig_estado_rev.update_layout(height=350, showlegend=False)
                            st.plotly_chart(fig_estado_rev, use_container_width=True)
                        
                        st.markdown("---")
                        
                        # ==========================================
                        # 8. VISUALIZACIONES JERÁRQUICAS
                        # ==========================================
                        st.markdown("### 8️⃣ Visualizaciones Jerárquicas")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # Treemap: Revenue por Categoría y Ciudad
                            treemap_data = df_dash.groupby(['Categoria', 'Ciudad_Destino'])['Revenue'].sum().reset_index()
                            
                            # Simplificado para Treemap
                            fig_treemap = px.treemap(
                                treemap_data.head(50),
                                path=['Categoria', 'Ciudad_Destino'],
                                values='Revenue',
                                title='🌳 Treemap: Revenue Categoría → Ciudad',
                                color='Revenue',
                                color_continuous_scale='Blues'
                            )
                            fig_treemap.update_layout(height=400)
                            st.plotly_chart(fig_treemap, use_container_width=True)
                        
                        with col2:
                            # Sunburst: Revenue por Canal → Categoría
                            sunburst_data = df_dash.groupby(['Canal_Venta', 'Categoria'])['Revenue'].sum().reset_index()
                            sunburst_data = pd.concat([
                                pd.DataFrame({'Canal_Venta': sunburst_data['Canal_Venta'].unique(), 'Categoria': '', 'Revenue': sunburst_data.groupby('Canal_Venta')['Revenue'].sum().values}),
                                sunburst_data
                            ], ignore_index=True)
                            
                            fig_sunburst = go.Figure(go.Sunburst(
                                labels=list(sunburst_data['Canal_Venta'].unique()) + list(sunburst_data[sunburst_data['Categoria'] != '']['Categoria'].unique()),
                                parents=[''] * len(sunburst_data['Canal_Venta'].unique()) + list(sunburst_data[sunburst_data['Categoria'] != '']['Canal_Venta'].values),
                                values=list(sunburst_data[sunburst_data['Categoria'] == '']['Revenue'].values) + list(sunburst_data[sunburst_data['Categoria'] != '']['Revenue'].values),
                                marker=dict(
                                    colorscale='RdBu',
                                    cmid=0
                                )
                            ))
                            fig_sunburst.update_layout(height=400, title='☀️ Sunburst: Revenue Canal → Categoría')
                            st.plotly_chart(fig_sunburst, use_container_width=True)
                        
                        st.markdown("---")
                        
                        # ==========================================
                        # 9. SALUD DEL INVENTARIO VS VENTAS
                        # ==========================================
                        st.markdown("### 9️⃣ Salud del Inventario vs Ventas")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            inv_ventas = df_dash.groupby('SKU_ID').agg({
                                'Stock_Actual': 'first',
                                'Cantidad_Vendida': 'sum',
                                'Revenue': 'sum',
                                'Categoria': 'first'
                            }).reset_index().head(30)
                            
                            fig_inv_ventas = px.scatter(
                                inv_ventas,
                                x='Stock_Actual',
                                y='Cantidad_Vendida',
                                size='Revenue',
                                color='Categoria',
                                title='📦 Stock vs Cantidad Vendida (Top 30 SKUs)',
                                labels={'Stock_Actual': 'Stock Actual', 'Cantidad_Vendida': 'Cantidad Vendida'},
                                opacity=0.7,
                                hover_data={'Revenue': ':.0f'}
                            )
                            fig_inv_ventas.update_layout(height=400)
                            st.plotly_chart(fig_inv_ventas, use_container_width=True)
                        
                        with col2:
                            # Rotación por categoría
                            rotacion = df_dash.groupby('Categoria').agg({
                                'Cantidad_Vendida': 'sum',
                                'Stock_Actual': 'first'
                            })
                            rotacion['Rotacion'] = rotacion['Cantidad_Vendida'] / (rotacion['Stock_Actual'] + 1)
                            rotacion = rotacion.sort_values('Rotacion', ascending=False)
                            
                            fig_rotacion = px.bar(
                                x=rotacion.index,
                                y=rotacion['Rotacion'],
                                title='🔄 Rotación de Inventario por Categoría',
                                labels={'x': 'Categoría', 'y': 'Índice de Rotación'},
                                color=rotacion['Rotacion'],
                                color_continuous_scale='Plasma',
                                text=rotacion['Rotacion'].round(2)
                            )
                            fig_rotacion.update_traces(textposition='auto')
                            fig_rotacion.update_layout(height=400, showlegend=False, xaxis_tickangle=-45)
                            st.plotly_chart(fig_rotacion, use_container_width=True)
                        
                        # Matriz Categoría vs Estado Envío
                        matriz_cat_estado = pd.crosstab(df_dash['Categoria'], df_dash['Estado_Envio'])
                        fig_matriz = px.imshow(
                            matriz_cat_estado,
                            title='🔥 Matriz: Categoría vs Estado de Envío',
                            color_continuous_scale='RdYlGn_r',
                            labels={'x': 'Estado Envío', 'y': 'Categoría', 'color': 'Cantidad'},
                            aspect='auto'
                        )
                        fig_matriz.update_layout(height=350)
                        st.plotly_chart(fig_matriz, use_container_width=True)
                        
                        st.markdown("---")
                        
                        # ==========================================
                        # 10. DASHBOARD EJECUTIVO - KPIs MATRIZ
                        # ==========================================
                        st.markdown("### 🔟 Dashboard Ejecutivo - Matriz de KPIs")
                        
                        # Crear matriz de KPIs por Canal, Categoría y Ciudad
                        st.subheader("📊 KPIs por Canal de Venta")
                        canal_kpis = df_dash.groupby('Canal_Venta').agg({
                            'Revenue': 'sum',
                            'Margen': 'sum',
                            'Cantidad_Vendida': 'sum',
                            'Rating_Producto': 'mean',
                            'Satisfaccion_NPS': 'mean'
                        }).round(2)
                        canal_kpis['Margen_Pct'] = (canal_kpis['Margen'] / canal_kpis['Revenue'] * 100).round(1)
                        canal_kpis = canal_kpis.rename(columns={
                            'Revenue': '💰 Revenue',
                            'Margen': '💵 Ganancia',
                            'Cantidad_Vendida': '📦 Cantidad',
                            'Rating_Producto': '⭐ Rating',
                            'Satisfaccion_NPS': '📊 NPS',
                            'Margen_Pct': '📈 Margen %'
                        })
                        st.dataframe(canal_kpis, use_container_width=True)
                        
                        st.subheader("📊 Top KPIs por Categoría")
                        cat_kpis = df_dash.groupby('Categoria').agg({
                            'Revenue': 'sum',
                            'Margen': 'sum',
                            'Cantidad_Vendida': 'sum',
                            'Rating_Producto': 'mean',
                            'Satisfaccion_NPS': 'mean'
                        }).round(2).sort_values('Revenue', ascending=False).head(10)
                        cat_kpis['Margen_Pct'] = (cat_kpis['Margen'] / cat_kpis['Revenue'] * 100).round(1)
                        cat_kpis = cat_kpis.rename(columns={
                            'Revenue': '💰 Revenue',
                            'Margen': '💵 Ganancia',
                            'Cantidad_Vendida': '📦 Cantidad',
                            'Rating_Producto': '⭐ Rating',
                            'Satisfaccion_NPS': '📊 NPS',
                            'Margen_Pct': '📈 Margen %'
                        })
                        st.dataframe(cat_kpis, use_container_width=True)
                        
                        st.subheader("📊 Top KPIs por Ciudad")
                        ciudad_kpis = df_dash.groupby('Ciudad_Destino').agg({
                            'Revenue': 'sum',
                            'Margen': 'sum',
                            'Cantidad_Vendida': 'sum',
                            'Rating_Producto': 'mean',
                            'Satisfaccion_NPS': 'mean'
                        }).round(2).sort_values('Revenue', ascending=False).head(10)
                        ciudad_kpis['Margen_Pct'] = (ciudad_kpis['Margen'] / ciudad_kpis['Revenue'] * 100).round(1)
                        ciudad_kpis = ciudad_kpis.rename(columns={
                            'Revenue': '💰 Revenue',
                            'Margen': '💵 Ganancia',
                            'Cantidad_Vendida': '📦 Cantidad',
                            'Rating_Producto': '⭐ Rating',
                            'Satisfaccion_NPS': '📊 NPS',
                            'Margen_Pct': '📈 Margen %'
                        })
                        st.dataframe(ciudad_kpis, use_container_width=True)
                        
                        st.markdown("---")
                        
                        # Descargar resultado
                        csv = df_integrado.to_csv(index=False)
                        st.download_button(
                            label="📥 Descargar Datos Integrados (CSV)",
                            data=csv,
                            file_name="datos_integrados.csv",
                            mime="text/csv"
                        )
                        
                        # ==========================================
                        # ANÁLISIS CON IA - GROQ
                        # ==========================================
                        st.markdown("---")
                        st.markdown("""
                        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                    padding: 2rem; 
                                    border-radius: 15px; 
                                    text-align: center;
                                    margin: 2rem 0;'>
                            <h2 style='color: white; margin: 0; font-size: 2rem;'>🤖 Análisis Estratégico con IA</h2>
                            <p style='color: rgba(255,255,255,0.9); margin-top: 0.5rem; font-size: 1.1rem;'>
                                Genera recomendaciones estratégicas integradas con Llama 3.3
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Container para el input de API Key
                        with st.container():
                            st.markdown("#### 🔑 Configuración")
                            col1, col2 = st.columns([4, 1])
                            
                            with col1:
                                groq_api_key = st.text_input(
                                    "API Key de Groq",
                                    type="password",
                                    placeholder="Ingresa tu API key aquí...",
                                    help="Tu API key se mantiene privada y no se almacena",
                                    label_visibility="collapsed",
                                    key="groq_key_merge"
                                )
                            
                            with col2:
                                st.markdown("""
                                <a href='https://console.groq.com/keys' target='_blank'>
                                    <button style='
                                        background: #4CAF50;
                                        color: white;
                                        border: none;
                                        padding: 0.5rem 1rem;
                                        border-radius: 8px;
                                        cursor: pointer;
                                        font-weight: bold;
                                        margin-top: 0.5rem;
                                        width: 100%;
                                    '>
                                        🔗 Obtener Key
                                    </button>
                                </a>
                                """, unsafe_allow_html=True)
                        
                        st.markdown("<br>", unsafe_allow_html=True)
                        
                        # Botón principal con mejor diseño
                        col1, col2, col3 = st.columns([1, 2, 1])
                        with col2:
                            generar_analisis = st.button(
                                "✨ Generar Reporte con Llama 3.3",
                                type="primary",
                                use_container_width=True,
                                disabled=not groq_api_key,
                                key="btn_generar_merge"
                            )
                        
                        if generar_analisis:
                            if not groq_api_key:
                                st.error("⚠️ Por favor ingresa tu API Key de Groq")
                            else:
                                # Barra de progreso animada
                                progress_bar = st.progress(0)
                                status_text = st.empty()
                                
                                try:
                                    from groq import Groq
                                    
                                    # Simular progreso
                                    for i in range(20):
                                        progress_bar.progress(i * 5)
                                        status_text.text(f"🔄 Conectando con Llama 3.3... {i*5}%")
                                        time.sleep(0.05)
                                    
                                    client = Groq(api_key=groq_api_key)
                                    
                                    # Preparar resumen del MERGE integrado
                                    resumen = f"""
Análisis Integrado - Data Validation & Integration Report

Total de Registros Integrados: {len(df_dash)}
Fecha de Análisis: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}

📊 MÉTRICAS FINANCIERAS:
- Revenue Total: ${df_dash['Revenue'].sum():,.2f}
- Ganancia Neta: ${df_dash['Margen'].sum():,.2f}
- Margen de Ganancia: {(df_dash['Margen'].sum()/df_dash['Revenue'].sum()*100):.1f}%
- AOV (Average Order Value): ${df_dash['Revenue'].mean():,.2f}

📦 ANÁLISIS DE INVENTARIO:
- Stock Promedio: {df_dash['Stock_Actual'].mean():.0f} unidades
- Cantidad Vendida Total: {df_dash['Cantidad_Vendida'].sum():.0f} unidades
- Top Categorías: {', '.join(df_dash['Categoria'].value_counts().head(3).index.tolist())}
- Rotación Promedio: {(df_dash['Cantidad_Vendida'].sum() / (df_dash['Stock_Actual'].mean() + 1)):.2f}x

⭐ SATISFACCIÓN DEL CLIENTE:
- Rating Promedio Producto: {df_dash['Rating_Producto'].mean():.2f}/5
- Rating Promedio Logística: {df_dash['Rating_Logistica'].mean():.2f}/5
- NPS Promedio: {df_dash['Satisfaccion_NPS'].mean():.1f}
- Rating Servicio: {df_dash['Rating_Servicio'].mean():.2f}/5

🚚 ANÁLISIS LOGÍSTICO (Entregas):
- Estado Principal: {df_dash['Estado_Envio'].value_counts().index[0]} ({(df_dash['Estado_Envio'].value_counts().iloc[0]/len(df_dash)*100):.1f}%)
- Costo Envío Promedio: ${df_dash['Costo_Envio'].mean():.2f}
- Tiempo Entregar Promedio: {df_dash['Tiempo_Entrega'].mean():.1f} días
- Entregas Exitosas: {(df_dash['Estado_Envio'] == 'Entregado').sum()} ({((df_dash['Estado_Envio'] == 'Entregado').sum()/len(df_dash)*100):.1f}%)

🏘️ DISTRIBUCIÓN GEOGRÁFICA:
- Top Ciudades: {', '.join(df_dash['Ciudad_Destino'].value_counts().head(3).index.tolist())}
- Ciudades Únicas: {df_dash['Ciudad_Destino'].nunique()}

💻 ANÁLISIS DE CANALES:
- Canal Físico: {(df_dash['Canal_Venta'] == 'Físico').sum()} transacciones ({((df_dash['Canal_Venta'] == 'Físico').sum()/len(df_dash)*100):.1f}%)
- Canal Online: {(df_dash['Canal_Venta'] == 'Online').sum()} transacciones ({((df_dash['Canal_Venta'] == 'Online').sum()/len(df_dash)*100):.1f}%)
- Revenue Físico: ${df_dash[df_dash['Canal_Venta'] == 'Físico']['Revenue'].sum():,.2f}
- Revenue Online: ${df_dash[df_dash['Canal_Venta'] == 'Online']['Revenue'].sum():,.2f}

🏥 SALUD DE DATOS:
- Health Score Integrado: {calcular_health_score(df_integrado):.1f}/100
- Valores Nulos: {int(df_integrado.isna().sum().sum())}
- Columnas Totales: {len(df_integrado.columns)}
"""
                                    
                                    status_text.text("🧠 Analizando datos integrados...")
                                    progress_bar.progress(60)
                                    
                                    response = client.chat.completions.create(
                                        model="llama-3.3-70b-versatile",
                                        messages=[{
                                            "role": "user",
                                            "content": f"""Eres un consultor estratégico senior especializado en análisis de datos integrados, logística y e-commerce.

Analiza estos datos integrados de validación y limpieza:

{resumen}

Genera exactamente 3 párrafos de recomendaciones estratégicas accionables y específicas.

Formato requerido:
- Párrafo 1: Análisis ejecutivo del desempeño integrado (salud operativa, rentabilidad, satisfacción)
- Párrafo 2: Recomendación táctica inmediata para optimizar la integración (corto plazo, 1-3 meses)
- Párrafo 3: Recomendación estratégica para escalar el negocio (mediano-largo plazo, 3-12 meses)

Escribe los 3 párrafos separados por línea en blanco, sin títulos ni numeración."""
                                        }],
                                        temperature=0.7,
                                        max_tokens=1500
                                    )
                                    
                                    status_text.text("✍️ Generando recomendaciones...")
                                    progress_bar.progress(90)
                                    
                                    recomendaciones = response.choices[0].message.content
                                    
                                    progress_bar.progress(100)
                                    time.sleep(0.3)
                                    status_text.empty()
                                    progress_bar.empty()
                                    
                                    # Mostrar resultados con diseño mejorado
                                    st.markdown("""
                                    <div style='background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
                                                padding: 1rem;
                                                border-radius: 10px;
                                                text-align: center;
                                                margin: 1rem 0;'>
                                        <h3 style='color: white; margin: 0;'>✅ Análisis Completado</h3>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    
                                    # Card para las recomendaciones
                                    st.markdown("""
                                    <div style='background: #f8f9fa;
                                                border-left: 5px solid #667eea;
                                                padding: 1.5rem;
                                                border-radius: 10px;
                                                margin: 1rem 0;
                                                box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
                                        <h3 style='color: #333; margin-top: 0;'>📋 Recomendaciones Estratégicas - Merge Integrado</h3>
                                    """, unsafe_allow_html=True)
                                    
                                    # Dividir en párrafos y mostrar con iconos
                                    parrafos = recomendaciones.split('\n\n')
                                    iconos = ['🎯', '⚡', '🚀']
                                    
                                    for i, parrafo in enumerate(parrafos[:3]):
                                        if parrafo.strip():
                                            st.markdown(f"""
                                            <div style='margin: 1.5rem 0;'>
                                                <div style='display: flex; align-items: start;'>
                                                    <div style='font-size: 2rem; margin-right: 1rem;'>{iconos[i]}</div>
                                                    <div style='flex: 1;'>
                                                        <p style='color: #555; line-height: 1.8; margin: 0; font-size: 1.05rem;'>
                                                            {parrafo.strip()}
                                                        </p>
                                                    </div>
                                                </div>
                                            </div>
                                            """, unsafe_allow_html=True)
                                    
                                    st.markdown("</div>", unsafe_allow_html=True)
                                    
                                    # Botones de acción
                                    col1, col2, col3 = st.columns(3)
                                    
                                    with col1:
                                        st.download_button(
                                            "📥 Descargar Reporte",
                                            recomendaciones,
                                            file_name=f"recomendaciones_merge_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.txt",
                                            mime="text/plain",
                                            use_container_width=True,
                                            key="download_merge"
                                        )
                                    
                                    with col2:
                                        if st.button("📋 Copiar al Portapapeles", use_container_width=True, key="copy_merge"):
                                            st.code(recomendaciones, language=None)
                                            st.success("✅ Texto listo para copiar")
                                    
                                    with col3:
                                        if st.button("🔄 Generar Nuevo Análisis", use_container_width=True, key="refresh_merge"):
                                            st.rerun()
                                    
                                    # Disclaimer
                                    st.markdown("""
                                    <div style='background: #fff3cd;
                                                border-left: 4px solid #ffc107;
                                                padding: 1rem;
                                                border-radius: 8px;
                                                margin-top: 2rem;'>
                                        <small style='color: #856404;'>
                                            ⚠️ <strong>Nota:</strong> Estas recomendaciones son generadas por IA y deben ser 
                                            revisadas por un experto en datos e integración antes de implementarlas.
                                        </small>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    
                                except Exception as e:
                                    progress_bar.empty()
                                    status_text.empty()
                                    
                                    st.markdown("""
                                    <div style='background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
                                                padding: 1.5rem;
                                                border-radius: 10px;
                                                text-align: center;
                                                color: white;'>
                                        <h3 style='margin: 0;'>❌ Error al Generar Análisis</h3>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    
                                    st.error(f"**Detalles del error:** {str(e)}")
                                    
                                    with st.expander("💡 Posibles soluciones"):
                                        st.markdown("""
                                        - ✓ Verifica que tu API key sea correcta
                                        - ✓ Asegúrate de tener créditos en tu cuenta de Groq
                                        - ✓ Revisa tu conexión a internet
                                        - ✓ Intenta generar el reporte nuevamente
                                        """)
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
