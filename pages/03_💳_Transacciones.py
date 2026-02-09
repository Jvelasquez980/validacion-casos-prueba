import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.data_loader import display_dataframe_info, load_csv_file
from utils.session_init import init_session_state
from utils.data_cleaning import limpiar_transacciones, generar_audit_summary, calcular_health_score, contar_valores_invalidos

# Inicializar session state
init_session_state()

st.set_page_config(
    page_title="Transacciones",
    page_icon="💳",
    layout="wide"
)

st.header("💳 Transacciones")

# Obtener el archivo del session state
if st.session_state.get('transacciones_file') is not None:
    try:
        df = load_csv_file(st.session_state.transacciones_file)
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
                    label="📥 Descargar Transacciones Original (CSV)",
                    data=csv,
                    file_name="transacciones_original.csv",
                    mime="text/csv"
                )
            
            with tab2:
                st.subheader("Datos Limpiados")
                try:
                    df_limpio = limpiar_transacciones(df)
                    
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
                    audit = generar_audit_summary(df, df_limpio, "Transacciones")
                    
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
                    
                    # ========== GRÁFICAS DE ANÁLISIS ==========
                    st.markdown("### 📊 Análisis de Transacciones - Gráficas")
                    
                    col1, col2 = st.columns(2)
                    
                    # Gráfica 1: Cantidad de transacciones por cantidad vendida
                    with col1:
                        st.markdown("#### 📦 Transacciones por Cantidad Vendida")
                        cantidad_dist = df_limpio['Cantidad_Vendida'].value_counts().sort_index().reset_index()
                        cantidad_dist.columns = ['Cantidad_Vendida', 'Num_Transacciones']
                        
                        fig_cantidad = px.bar(
                            cantidad_dist,
                            x='Cantidad_Vendida',
                            y='Num_Transacciones',
                            color='Num_Transacciones',
                            color_continuous_scale='Viridis',
                            text='Num_Transacciones',
                            title="Cantidad de Transacciones por Cantidad Vendida"
                        )
                        fig_cantidad.update_layout(
                            height=400,
                            xaxis_title="Cantidad Vendida (unidades)",
                            yaxis_title="Número de Transacciones",
                            hovermode='x unified',
                            showlegend=False
                        )
                        fig_cantidad.update_traces(textposition='auto')
                        st.plotly_chart(fig_cantidad, use_container_width=True)
                    
                    # Gráfica 2: Cantidad de transacciones por estado de envío
                    with col2:
                        st.markdown("#### 🚚 Cantidad de Transacciones por Estado de Envío")
                        estado_dist = df_limpio['Estado_Envio'].value_counts().reset_index()
                        estado_dist.columns = ['Estado_Envio', 'Cantidad']
                        
                        color_map_estado = {'Entregado': '#2ecc71', 'En_Transito': '#3498db', 'Perdido': '#e74c3c', 'Retrasado': '#f39c12'}
                        
                        fig_estado = px.bar(
                            estado_dist,
                            x='Estado_Envio',
                            y='Cantidad',
                            color='Estado_Envio',
                            color_discrete_map=color_map_estado,
                            text='Cantidad',
                            title="Transacciones por Estado de Envío"
                        )
                        fig_estado.update_layout(
                            height=400,
                            xaxis_title="Estado de Envío",
                            yaxis_title="Cantidad de Transacciones",
                            hovermode='x unified',
                            showlegend=False
                        )
                        fig_estado.update_traces(textposition='auto')
                        st.plotly_chart(fig_estado, use_container_width=True)
                    
                    col3, col4 = st.columns(2)
                    
                    # Gráfica 3: Histograma de costo de envío
                    with col3:
                        st.markdown("#### 💰 Distribución del Costo de Envío")
                        
                        fig_costo_hist = px.histogram(
                            df_limpio,
                            x='Costo_Envio',
                            nbins=30,
                            color_discrete_sequence=['#3498db'],
                            title="Distribución del Costo de Envío",
                            labels={'Costo_Envio': 'Costo Envío (USD)', 'count': 'Frecuencia'}
                        )
                        fig_costo_hist.update_layout(
                            height=400,
                            showlegend=False,
                            bargap=0.1
                        )
                        st.plotly_chart(fig_costo_hist, use_container_width=True)
                        
                        # Mostrar estadísticas
                        costo_stats_col1, costo_stats_col2, costo_stats_col3 = st.columns(3)
                        with costo_stats_col1:
                            st.metric("Costo Promedio", f"${df_limpio['Costo_Envio'].mean():.2f}")
                        with costo_stats_col2:
                            st.metric("Costo Máximo", f"${df_limpio['Costo_Envio'].max():.2f}")
                        with costo_stats_col3:
                            st.metric("Costo Mínimo", f"${df_limpio['Costo_Envio'].min():.2f}")
                    
                    # Gráfica 4: Costo promedio de envío por ciudad destino
                    with col4:
                        st.markdown("#### 🏙️ Costo Promedio de Envío por Ciudad Destino")
                        costo_ciudad = df_limpio.groupby('Ciudad_Destino')['Costo_Envio'].mean().sort_values(ascending=False).reset_index()
                        costo_ciudad.columns = ['Ciudad_Destino', 'Costo_Promedio']
                        
                        fig_costo_ciudad = px.bar(
                            costo_ciudad,
                            x='Ciudad_Destino',
                            y='Costo_Promedio',
                            color='Costo_Promedio',
                            color_continuous_scale='RdYlGn_r',
                            text=costo_ciudad['Costo_Promedio'].apply(lambda x: f'${x:.2f}'),
                            title="Costo Promedio de Envío por Ciudad"
                        )
                        fig_costo_ciudad.update_layout(
                            height=400,
                            xaxis_title="Ciudad Destino",
                            yaxis_title="Costo Promedio (USD)",
                            hovermode='x unified',
                            showlegend=False,
                            xaxis_tickangle=-45
                        )
                        fig_costo_ciudad.update_traces(textposition='auto')
                        st.plotly_chart(fig_costo_ciudad, use_container_width=True)
                    
                    col5, col6 = st.columns(2)
                    
                    # Gráfica 5: Costo promedio de envío por canal de venta
                    with col5:
                        st.markdown("#### 📱 Costo Promedio de Envío por Canal de Venta")
                        costo_canal = df_limpio.groupby('Canal_Venta')['Costo_Envio'].mean().sort_values(ascending=False).reset_index()
                        costo_canal.columns = ['Canal_Venta', 'Costo_Promedio']
                        
                        fig_costo_canal = px.bar(
                            costo_canal,
                            x='Canal_Venta',
                            y='Costo_Promedio',
                            color='Costo_Promedio',
                            color_continuous_scale='Plasma',
                            text=costo_canal['Costo_Promedio'].apply(lambda x: f'${x:.2f}'),
                            title="Costo Promedio de Envío por Canal"
                        )
                        fig_costo_canal.update_layout(
                            height=400,
                            xaxis_title="Canal de Venta",
                            yaxis_title="Costo Promedio (USD)",
                            hovermode='x unified',
                            showlegend=False
                        )
                        fig_costo_canal.update_traces(textposition='auto')
                        st.plotly_chart(fig_costo_canal, use_container_width=True)
                    
                    # Gráfica 6: Top SKUs por cantidad vendida
                    with col6:
                        st.markdown("#### 🏆 Top 15 SKUs por Cantidad Vendida")
                        top_skus = df_limpio.groupby('SKU_ID')['Cantidad_Vendida'].sum().sort_values(ascending=False).head(15).reset_index()
                        
                        fig_top_skus = px.bar(
                            top_skus,
                            x='SKU_ID',
                            y='Cantidad_Vendida',
                            color='Cantidad_Vendida',
                            color_continuous_scale='Blues',
                            text='Cantidad_Vendida',
                            title="Top 15 SKUs por Cantidad Vendida"
                        )
                        fig_top_skus.update_layout(
                            height=400,
                            xaxis_title="SKU ID",
                            yaxis_title="Cantidad Vendida Total",
                            hovermode='x unified',
                            showlegend=False,
                            xaxis_tickangle=-45
                        )
                        fig_top_skus.update_traces(textposition='auto')
                        st.plotly_chart(fig_top_skus, use_container_width=True)
                    
                    st.markdown("---")
                    
                    # ========== GRÁFICAS ADICIONALES AVANZADAS ==========
                    st.markdown("### 📈 Análisis Avanzado de Transacciones")
                    
                    col7, col8 = st.columns(2)
                    
                    # Gráfica 7: Scatter - Precio Final vs Cantidad Vendida
                    with col7:
                        st.markdown("#### 💎 Correlación: Precio Final vs Cantidad Vendida")
                        
                        fig_scatter_precio = px.scatter(
                            df_limpio,
                            x='Cantidad_Vendida',
                            y='Precio_Venta_Final',
                            color='Canal_Venta',
                            size='Costo_Envio',
                            hover_name='Transaccion_ID',
                            hover_data={'Cantidad_Vendida': True, 'Precio_Venta_Final': ':.2f', 'Canal_Venta': True},
                            title="Precio Final vs Cantidad Vendida",
                            labels={'Cantidad_Vendida': 'Cantidad Vendida (unidades)', 'Precio_Venta_Final': 'Precio Final (USD)'},
                            color_discrete_map={'Físico': '#3498db', 'Online': '#e74c3c'}
                        )
                        fig_scatter_precio.update_layout(
                            height=400,
                            hovermode='closest',
                            plot_bgcolor='rgba(240,240,240,0.5)'
                        )
                        st.plotly_chart(fig_scatter_precio, use_container_width=True)
                    
                    # Gráfica 8: Box Plot - Tiempo de Entrega por Estado
                    with col8:
                        st.markdown("#### ⏱️ Tiempo de Entrega por Estado de Envío")
                        
                        fig_box_tiempo = px.box(
                            df_limpio,
                            x='Estado_Envio',
                            y='Tiempo_Entrega_Real',
                            color='Estado_Envio',
                            title="Distribución de Tiempo de Entrega por Estado",
                            labels={'Tiempo_Entrega_Real': 'Días', 'Estado_Envio': 'Estado de Envío'},
                            color_discrete_map={'Entregado': '#2ecc71', 'En_Transito': '#3498db', 'Perdido': '#e74c3c', 'Retrasado': '#f39c12'}
                        )
                        fig_box_tiempo.update_layout(
                            height=400,
                            showlegend=False
                        )
                        st.plotly_chart(fig_box_tiempo, use_container_width=True)
                    
                    col9, col10 = st.columns(2)
                    
                    # Gráfica 9: Scatter - Costo Envío vs Tiempo de Entrega
                    with col9:
                        st.markdown("#### ⚡ Costo de Envío vs Tiempo de Entrega")
                        
                        fig_scatter_costo_tiempo = px.scatter(
                            df_limpio,
                            x='Costo_Envio',
                            y='Tiempo_Entrega_Real',
                            color='Estado_Envio',
                            size='Cantidad_Vendida',
                            hover_name='Transaccion_ID',
                            hover_data={'Costo_Envio': ':.2f', 'Tiempo_Entrega_Real': True, 'Estado_Envio': True},
                            title="Costo Envío vs Tiempo de Entrega",
                            labels={'Costo_Envio': 'Costo (USD)', 'Tiempo_Entrega_Real': 'Tiempo (días)'},
                            color_discrete_map={'Entregado': '#2ecc71', 'En_Transito': '#3498db', 'Perdido': '#e74c3c', 'Retrasado': '#f39c12'}
                        )
                        fig_scatter_costo_tiempo.update_layout(
                            height=400,
                            hovermode='closest',
                            plot_bgcolor='rgba(240,240,240,0.5)'
                        )
                        st.plotly_chart(fig_scatter_costo_tiempo, use_container_width=True)
                    
                    # Gráfica 10: Histograma - Distribución de Tiempo de Entrega
                    with col10:
                        st.markdown("#### 📅 Distribución de Tiempo de Entrega Real")
                        
                        fig_hist_tiempo = px.histogram(
                            df_limpio,
                            x='Tiempo_Entrega_Real',
                            nbins=25,
                            color_discrete_sequence=['#9b59b6'],
                            title="Distribución de Tiempo de Entrega",
                            labels={'Tiempo_Entrega_Real': 'Días de Entrega', 'count': 'Frecuencia'}
                        )
                        fig_hist_tiempo.update_layout(
                            height=400,
                            showlegend=False,
                            bargap=0.1
                        )
                        st.plotly_chart(fig_hist_tiempo, use_container_width=True)
                        
                        # Estadísticas de tiempo
                        tiempo_stats_col1, tiempo_stats_col2, tiempo_stats_col3 = st.columns(3)
                        with tiempo_stats_col1:
                            st.metric("Tiempo Promedio", f"{df_limpio['Tiempo_Entrega_Real'].mean():.1f} días")
                        with tiempo_stats_col2:
                            st.metric("Tiempo Máximo", f"{df_limpio['Tiempo_Entrega_Real'].max():.0f} días")
                        with tiempo_stats_col3:
                            st.metric("Tiempo Mínimo", f"{df_limpio['Tiempo_Entrega_Real'].min():.0f} días")
                    
                    st.markdown("---")
                    col11, col12 = st.columns(2)
                    
                    # Gráfica 11: Heatmap - Estado Envío vs Canal de Venta
                    with col11:
                        st.markdown("#### 🔥 Matriz: Estado de Envío vs Canal de Venta")
                        
                        crosstab_estado_canal = pd.crosstab(
                            df_limpio['Estado_Envio'].astype(str),
                            df_limpio['Canal_Venta'].astype(str)
                        )
                        
                        fig_heatmap_estado = px.imshow(
                            crosstab_estado_canal,
                            labels=dict(x="Canal de Venta", y="Estado de Envío", color="Cantidad"),
                            color_continuous_scale='YlGnBu',
                            title="Matriz: Estado de Envío vs Canal de Venta",
                            text_auto=True,
                            aspect='auto'
                        )
                        fig_heatmap_estado.update_layout(height=400)
                        st.plotly_chart(fig_heatmap_estado, use_container_width=True)
                    
                    # Gráfica 12: Gráfico de Línea - Transacciones por Fecha
                    with col12:
                        st.markdown("#### 📊 Tendencia de Transacciones por Fecha")
                        
                        df_limpio['Fecha_Venta'] = pd.to_datetime(df_limpio['Fecha_Venta'])
                        transacciones_fecha = df_limpio.groupby(df_limpio['Fecha_Venta'].dt.date).size().reset_index(name='Cantidad')
                        transacciones_fecha.columns = ['Fecha', 'Cantidad']
                        
                        fig_timeline = px.line(
                            transacciones_fecha,
                            x='Fecha',
                            y='Cantidad',
                            title="Tendencia de Transacciones en el Tiempo",
                            labels={'Fecha': 'Fecha de Venta', 'Cantidad': 'Número de Transacciones'},
                            markers=True
                        )
                        fig_timeline.update_layout(
                            height=400,
                            hovermode='x unified'
                        )
                        fig_timeline.update_traces(line=dict(color='#3498db', width=2))
                        st.plotly_chart(fig_timeline, use_container_width=True)
                    
                    st.markdown("---")
                    col13, col14 = st.columns(2)
                    
                    # Gráfica 13: Scatter - Cantidad Vendida vs Costo Envío
                    with col13:
                        st.markdown("#### 📦 Cantidad Vendida vs Costo de Envío")
                        
                        fig_scatter_cantidad_costo = px.scatter(
                            df_limpio,
                            x='Cantidad_Vendida',
                            y='Costo_Envio',
                            color='Estado_Envio',
                            size='Tiempo_Entrega_Real',
                            hover_name='Transaccion_ID',
                            hover_data={'Cantidad_Vendida': True, 'Costo_Envio': ':.2f', 'Estado_Envio': True},
                            title="Cantidad Vendida vs Costo de Envío",
                            labels={'Cantidad_Vendida': 'Cantidad (unidades)', 'Costo_Envio': 'Costo (USD)'},
                            color_discrete_map={'Entregado': '#2ecc71', 'En_Transito': '#3498db', 'Perdido': '#e74c3c', 'Retrasado': '#f39c12'}
                        )
                        fig_scatter_cantidad_costo.update_layout(
                            height=400,
                            hovermode='closest',
                            plot_bgcolor='rgba(240,240,240,0.5)'
                        )
                        st.plotly_chart(fig_scatter_cantidad_costo, use_container_width=True)
                    
                    # Gráfica 14: Pie Chart - Distribución de Ventas por Canal
                    with col14:
                        st.markdown("#### 🎯 Distribución de Ventas por Canal")
                        
                        canal_dist = df_limpio['Canal_Venta'].value_counts().reset_index()
                        canal_dist.columns = ['Canal_Venta', 'Cantidad']
                        
                        fig_pie_canal = px.pie(
                            canal_dist,
                            names='Canal_Venta',
                            values='Cantidad',
                            title="Distribución de Transacciones por Canal",
                            color_discrete_map={'Físico': '#3498db', 'Online': '#e74c3c'},
                            hole=0.3
                        )
                        fig_pie_canal.update_traces(
                            textposition='inside',
                            textinfo='label+percent',
                            hovertemplate='<b>%{label}</b><br>Transacciones: %{value}<br>Porcentaje: %{percent}<extra></extra>'
                        )
                        fig_pie_canal.update_layout(height=400)
                        st.plotly_chart(fig_pie_canal, use_container_width=True)
                    
                    st.markdown("---")
                    
                    # Gráfica 15: Box Plot - Precio por Canal de Venta
                    st.markdown("#### 💰 Precio de Venta por Canal de Venta")
                    
                    fig_box_precio = px.box(
                        df_limpio,
                        x='Canal_Venta',
                        y='Precio_Venta_Final',
                        color='Canal_Venta',
                        title="Distribución de Precios de Venta por Canal",
                        labels={'Precio_Venta_Final': 'Precio (USD)', 'Canal_Venta': 'Canal de Venta'},
                        color_discrete_map={'Físico': '#3498db', 'Online': '#e74c3c'}
                    )
                    fig_box_precio.update_layout(
                        height=400,
                        showlegend=False
                    )
                    st.plotly_chart(fig_box_precio, use_container_width=True)
                    
                    st.markdown("---")
                    
                    # Dashboard de KPIs Logísticos
                    st.markdown("#### 📊 Dashboard de KPIs Logísticos")
                    
                    col_gauge1, col_gauge2, col_gauge3 = st.columns(3)
                    
                    with col_gauge1:
                        # % Entregas a Tiempo (consideramos "a tiempo" los "Entregado")
                        entregas_exitosas = len(df_limpio[df_limpio['Estado_Envio'] == 'Entregado'])
                        total_entregas = len(df_limpio)
                        pct_entregas_exitosas = (entregas_exitosas / total_entregas) * 100
                        
                        fig_gauge_entrega = go.Figure(go.Indicator(
                            mode="gauge+number+delta",
                            value=pct_entregas_exitosas,
                            domain={'x': [0, 1], 'y': [0, 1]},
                            title={'text': "% Entregas Exitosas"},
                            delta={'reference': 80},
                            gauge={
                                'axis': {'range': [0, 100]},
                                'bar': {'color': "#2ecc71"},
                                'steps': [
                                    {'range': [0, 50], 'color': "#e74c3c"},
                                    {'range': [50, 75], 'color': "#f39c12"},
                                    {'range': [75, 90], 'color': "#3498db"},
                                    {'range': [90, 100], 'color': "#2ecc71"}
                                ],
                                'threshold': {
                                    'line': {'color': "red", 'width': 4},
                                    'thickness': 0.75,
                                    'value': 85
                                }
                            }
                        ))
                        fig_gauge_entrega.update_layout(height=300)
                        st.plotly_chart(fig_gauge_entrega, use_container_width=True)
                    
                    with col_gauge2:
                        # Costo Promedio de Envío
                        costo_promedio = df_limpio['Costo_Envio'].mean()
                        
                        fig_gauge_costo = go.Figure(go.Indicator(
                            mode="gauge+number+delta",
                            value=costo_promedio,
                            domain={'x': [0, 1], 'y': [0, 1]},
                            title={'text': "Costo Promedio Envío"},
                            delta={'reference': 60},
                            gauge={
                                'axis': {'range': [0, 150]},
                                'bar': {'color': "#e67e22"},
                                'steps': [
                                    {'range': [0, 40], 'color': "#2ecc71"},
                                    {'range': [40, 80], 'color': "#f39c12"},
                                    {'range': [80, 150], 'color': "#e74c3c"}
                                ],
                                'threshold': {
                                    'line': {'color': "red", 'width': 4},
                                    'thickness': 0.75,
                                    'value': 100
                                }
                            }
                        ))
                        fig_gauge_costo.update_layout(height=300)
                        st.plotly_chart(fig_gauge_costo, use_container_width=True)
                    
                    with col_gauge3:
                        # Tiempo de Entrega Promedio
                        tiempo_promedio = df_limpio['Tiempo_Entrega_Real'].mean()
                        
                        fig_gauge_tiempo = go.Figure(go.Indicator(
                            mode="gauge+number+delta",
                            value=tiempo_promedio,
                            domain={'x': [0, 1], 'y': [0, 1]},
                            title={'text': "Tiempo Promedio Entrega"},
                            delta={'reference': 15},
                            gauge={
                                'axis': {'range': [0, 40]},
                                'bar': {'color': "#9b59b6"},
                                'steps': [
                                    {'range': [0, 10], 'color': "#2ecc71"},
                                    {'range': [10, 20], 'color': "#3498db"},
                                    {'range': [20, 40], 'color': "#e74c3c"}
                                ],
                                'threshold': {
                                    'line': {'color': "red", 'width': 4},
                                    'thickness': 0.75,
                                    'value': 25
                                }
                            }
                        ))
                        fig_gauge_tiempo.update_layout(height=300)
                        st.plotly_chart(fig_gauge_tiempo, use_container_width=True)
                    
                    st.markdown("---")
                    display_dataframe_info(df_limpio)
                    
                    # Mostrar cambios realizados
                    st.subheader("Cambios Realizados")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Registros originales", len(df))
                    with col2:
                        st.metric("Registros limpiados", len(df_limpio))
                    
                    # Descargar archivo limpiado
                    csv_limpio = df_limpio.to_csv(index=False)
                    st.download_button(
                        label="📥 Descargar Transacciones Limpiado (CSV)",
                        data=csv_limpio,
                        file_name="transacciones_limpiado.csv",
                        mime="text/csv"
                    )
                except Exception as e:
                    st.error(f"❌ Error al limpiar datos: {e}")
    
    except Exception as e:
        st.error(f"❌ Error al procesar: {e}")
else:
    st.info("📤 Por favor, carga un archivo CSV de Transacciones en la barra lateral")

# ========== ANÁLISIS CON IA ==========

st.markdown("---")
st.markdown("""
<div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            padding: 2rem; 
            border-radius: 15px; 
            text-align: center;
            margin: 2rem 0;'>
    <h2 style='color: white; margin: 0; font-size: 2rem;'>🤖 Análisis Estratégico con IA</h2>
    <p style='color: rgba(255,255,255,0.9); margin-top: 0.5rem; font-size: 1.1rem;'>
        Genera recomendaciones estratégicas personalizadas con Llama 3.3
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
            key="groq_key_transacciones"
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
        key="btn_generar_transacciones"
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
            import time
            
            # Simular progreso
            for i in range(20):
                progress_bar.progress(i * 5)
                status_text.text(f"🔄 Conectando con Llama 3.3... {i*5}%")
                time.sleep(0.05)
            
            client = Groq(api_key=groq_api_key)
            
            # Preparar resumen de TRANSACCIONES
            resumen = f"""
Datos de Transacciones Logísticas - TechLogistics S.A.

Total de transacciones: {len(df_limpio)}

Estadísticas de Tiempo_Entrega:
{df_limpio['Tiempo_Entrega'].describe().to_string()}

Distribución por estado de envío:
{df_limpio['Estado_Envio'].value_counts().to_string()}

Top 10 ciudades destino:
{df_limpio['Ciudad_Destino'].value_counts().head(10).to_string()}

Análisis financiero:
- Ingresos totales: ${(df_limpio['Cantidad_Vendida'] * df_limpio['Precio_Venta_Final']).sum():,.2f} USD
- Costos de envío totales: ${df_limpio['Costo_Envio'].sum():,.2f} USD
- Margen neto: ${((df_limpio['Cantidad_Vendida'] * df_limpio['Precio_Venta_Final']).sum() - df_limpio['Costo_Envio'].sum()):,.2f} USD

Métricas operativas:
- Tiempo promedio de entrega: {df_limpio['Tiempo_Entrega'].mean():.1f} días
- Entregas rápidas (≤3 días): {len(df_limpio[df_limpio['Tiempo_Entrega'] <= 3])} ({(len(df_limpio[df_limpio['Tiempo_Entrega'] <= 3])/len(df_limpio)*100):.1f}%)
- Entregas lentas (>7 días): {len(df_limpio[df_limpio['Tiempo_Entrega'] > 7])} ({(len(df_limpio[df_limpio['Tiempo_Entrega'] > 7])/len(df_limpio)*100):.1f}%)
"""
            
            status_text.text("🧠 Analizando transacciones logísticas...")
            progress_bar.progress(60)
            
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{
                    "role": "user",
                    "content": f"""Eres un consultor estratégico senior especializado en logística y operaciones para TechLogistics S.A.

Analiza estos datos de transacciones logísticas:

{resumen}

Genera exactamente 3 párrafos de recomendaciones estratégicas accionables y específicas.

Formato requerido:
- Párrafo 1: Análisis del desempeño logístico actual y principales hallazgos
- Párrafo 2: Recomendación táctica inmediata para optimizar entregas (corto plazo)
- Párrafo 3: Recomendación estratégica para eficiencia operativa (mediano-largo plazo)

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
                <h3 style='color: #333; margin-top: 0;'>📋 Recomendaciones Estratégicas - Transacciones</h3>
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
                    file_name=f"recomendaciones_transacciones_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.txt",
                    mime="text/plain",
                    use_container_width=True,
                    key="download_trans"
                )
            
            with col2:
                if st.button("📋 Copiar al Portapapeles", use_container_width=True, key="copy_trans"):
                    st.code(recomendaciones, language=None)
                    st.success("✅ Texto listo para copiar")
            
            with col3:
                if st.button("🔄 Generar Nuevo Análisis", use_container_width=True, key="refresh_trans"):
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
                    revisadas por un experto en logística antes de implementarlas.
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