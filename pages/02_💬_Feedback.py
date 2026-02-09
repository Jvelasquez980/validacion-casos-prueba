import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.data_loader import display_dataframe_info, load_csv_file
from utils.session_init import init_session_state
from utils.data_cleaning import limpiar_feedback, generar_audit_summary, calcular_health_score, contar_valores_invalidos

# Inicializar session state
init_session_state()

st.set_page_config(
    page_title="Feedback",
    page_icon="💬",
    layout="wide"
)

st.header("💬 Feedback")

# Obtener el archivo del session state
if st.session_state.get('feedback_file') is not None:
    try:
        df = load_csv_file(st.session_state.feedback_file)
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
                    label="📥 Descargar Feedback Original (CSV)",
                    data=csv,
                    file_name="feedback_original.csv",
                    mime="text/csv"
                )
            
            with tab2:
                st.subheader("Datos Limpiados")
                try:
                    df_limpio = limpiar_feedback(df)
                    
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
                    audit = generar_audit_summary(df, df_limpio, "Feedback")
                    
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
                    st.markdown("### 📊 Análisis de Feedback - Gráficas")
                    
                    col1, col2 = st.columns(2)
                    
                    # Gráfica 1: Cantidad de feedback por tipo de comentario
                    with col1:
                        st.markdown("#### 💭 Cantidad de Feedback por Tipo de Comentario")
                        comentario_count = df_limpio['Comentario_Texto'].value_counts().reset_index()
                        comentario_count.columns = ['Comentario', 'Cantidad']
                        
                        fig_comentario = px.bar(
                            comentario_count,
                            x='Comentario',
                            y='Cantidad',
                            color='Cantidad',
                            color_continuous_scale='Viridis',
                            text='Cantidad',
                            title="Cantidad de Feedback por Tipo de Comentario"
                        )
                        fig_comentario.update_layout(
                            height=400,
                            xaxis_title="Tipo de Comentario",
                            yaxis_title="Cantidad",
                            hovermode='x unified',
                            showlegend=False
                        )
                        fig_comentario.update_traces(textposition='auto')
                        st.plotly_chart(fig_comentario, use_container_width=True)
                    
                    # Gráfica 2: Cantidad de feedback por recomendación de marca
                    with col2:
                        st.markdown("#### ⭐ Cantidad de Feedback por Recomendación de Marca")
                        recomendacion_count = df_limpio['Recomienda_Marca'].value_counts().reset_index()
                        recomendacion_count.columns = ['Recomendacion', 'Cantidad']
                        
                        # Mapear valores para mejor visualización
                        color_map = {'SI': '#2ecc71', 'MAYBE': '#f39c12', 'NO': '#e74c3c'}
                        recomendacion_count['Color'] = recomendacion_count['Recomendacion'].map(color_map)
                        
                        fig_recomendacion = px.pie(
                            recomendacion_count,
                            names='Recomendacion',
                            values='Cantidad',
                            title="Distribución de Recomendación de Marca",
                            color='Recomendacion',
                            color_discrete_map=color_map
                        )
                        fig_recomendacion.update_traces(
                            textposition='inside',
                            textinfo='label+percent',
                            hovertemplate='<b>%{label}</b><br>Cantidad: %{value}<br>Porcentaje: %{percent}<extra></extra>'
                        )
                        fig_recomendacion.update_layout(height=400)
                        st.plotly_chart(fig_recomendacion, use_container_width=True)
                    
                    col3, col4 = st.columns(2)
                    
                    # Gráfica 3: Cantidad de feedback por ticket de soporte abierto
                    with col3:
                        st.markdown("#### 🎫 Cantidad de Feedback por Ticket de Soporte Abierto")
                        ticket_count = df_limpio['Ticket_Soporte_Abierto'].value_counts().reset_index()
                        ticket_count.columns = ['Ticket_Abierto', 'Cantidad']
                        
                        fig_ticket = px.bar(
                            ticket_count,
                            x='Ticket_Abierto',
                            y='Cantidad',
                            color='Ticket_Abierto',
                            color_discrete_map={'Sí': '#e74c3c', 'No': '#2ecc71'},
                            text='Cantidad',
                            title="Feedback con Ticket de Soporte Abierto"
                        )
                        fig_ticket.update_layout(
                            height=400,
                            xaxis_title="Ticket de Soporte Abierto",
                            yaxis_title="Cantidad",
                            hovermode='x unified',
                            showlegend=False
                        )
                        fig_ticket.update_traces(textposition='auto')
                        st.plotly_chart(fig_ticket, use_container_width=True)
                        
                        # Mostrar porcentaje
                        pct_con_ticket = (ticket_count[ticket_count['Ticket_Abierto'] == 'Sí']['Cantidad'].values[0] / ticket_count['Cantidad'].sum() * 100) if 'Sí' in ticket_count['Ticket_Abierto'].values else 0
                        st.metric("% Feedback con Ticket", f"{pct_con_ticket:.1f}%")
                    
                    # Gráfica 4: Cantidad de feedback por rango de edad
                    with col4:
                        st.markdown("#### 👥 Cantidad de Feedback por Rango de Edad")
                        
                        # Crear rangos de edad
                        def categorizar_edad(edad):
                            if edad < 18:
                                return "< 18"
                            elif edad < 26:
                                return "18-25"
                            elif edad < 36:
                                return "26-35"
                            elif edad < 51:
                                return "36-50"
                            elif edad < 66:
                                return "51-65"
                            else:
                                return "65+"
                        
                        df_limpio['Rango_Edad'] = df_limpio['Edad_Cliente'].apply(categorizar_edad)
                        edad_count = df_limpio['Rango_Edad'].value_counts().reindex(['< 18', '18-25', '26-35', '36-50', '51-65', '65+'], fill_value=0)
                        edad_count = edad_count.reset_index()
                        edad_count.columns = ['Rango_Edad', 'Cantidad']
                        
                        fig_edad = px.bar(
                            edad_count,
                            x='Rango_Edad',
                            y='Cantidad',
                            color='Cantidad',
                            color_continuous_scale='Plasma',
                            text='Cantidad',
                            title="Cantidad de Feedback por Rango de Edad"
                        )
                        fig_edad.update_layout(
                            height=400,
                            xaxis_title="Rango de Edad",
                            yaxis_title="Cantidad",
                            hovermode='x unified',
                            showlegend=False
                        )
                        fig_edad.update_traces(textposition='auto')
                        st.plotly_chart(fig_edad, use_container_width=True)
                    
                    # Gráfica 5: Cantidad de feedback por rango de satisfacción NPS
                    col5, col6 = st.columns(2)
                    
                    with col5:
                        st.markdown("#### 📊 Cantidad de Feedback por Rango de Satisfacción NPS")
                        
                        # Crear rangos de NPS
                        def categorizar_nps(nps):
                            if nps < -50:
                                return "Muy Insatisfecho (< -50)"
                            elif nps < 0:
                                return "Insatisfecho (-50 a 0)"
                            elif nps < 30:
                                return "Neutral (0 a 30)"
                            elif nps < 70:
                                return "Satisfecho (30 a 70)"
                            else:
                                return "Muy Satisfecho (≥ 70)"
                        
                        df_limpio['Rango_NPS'] = df_limpio['Satisfaccion_NPS'].apply(categorizar_nps)
                        nps_count = df_limpio['Rango_NPS'].value_counts().reindex(
                            ['Muy Insatisfecho (< -50)', 'Insatisfecho (-50 a 0)', 'Neutral (0 a 30)', 'Satisfecho (30 a 70)', 'Muy Satisfecho (≥ 70)'],
                            fill_value=0
                        )
                        nps_count = nps_count.reset_index()
                        nps_count.columns = ['Rango_NPS', 'Cantidad']
                        
                        # Colores según nivel de satisfacción
                        colors_nps = ['#e74c3c', '#e67e22', '#f39c12', '#3498db', '#2ecc71']
                        
                        fig_nps = px.bar(
                            nps_count,
                            x='Rango_NPS',
                            y='Cantidad',
                            color='Cantidad',
                            color_continuous_scale='RdYlGn',
                            text='Cantidad',
                            title="Cantidad de Feedback por Rango de Satisfacción NPS"
                        )
                        fig_nps.update_layout(
                            height=400,
                            xaxis_title="Rango de Satisfacción NPS",
                            yaxis_title="Cantidad",
                            hovermode='x unified',
                            showlegend=False,
                            xaxis_tickangle=-45
                        )
                        fig_nps.update_traces(textposition='auto')
                        st.plotly_chart(fig_nps, use_container_width=True)
                    
                    # Estadísticas adicionales de NPS
                    with col6:
                        st.markdown("#### 📈 Estadísticas de Satisfacción")
                        
                        col_stat1, col_stat2 = st.columns(2)
                        with col_stat1:
                            nps_promedio = df_limpio['Satisfaccion_NPS'].mean()
                            st.metric("NPS Promedio", f"{nps_promedio:.1f}/10")
                        
                        with col_stat2:
                            nps_max = df_limpio['Satisfaccion_NPS'].max()
                            st.metric("NPS Máximo", f"{nps_max:.1f}/10")
                        
                        col_stat3, col_stat4 = st.columns(2)
                        with col_stat3:
                            nps_min = df_limpio['Satisfaccion_NPS'].min()
                            st.metric("NPS Mínimo", f"{nps_min:.1f}/10")
                        
                        with col_stat4:
                            nps_mediana = df_limpio['Satisfaccion_NPS'].median()
                            st.metric("NPS Mediana", f"{nps_mediana:.1f}/10")
                        
                        st.markdown("---")
                        
                        # Distribuición de ratings
                        st.markdown("#### ⭐ Ratings Promedio")
                        col_rating1, col_rating2 = st.columns(2)
                        with col_rating1:
                            rating_prod = df_limpio['Rating_Producto'].mean()
                            st.metric("Rating Producto", f"{rating_prod:.2f}/5")
                        with col_rating2:
                            rating_log = df_limpio['Rating_Logistica'].mean()
                            st.metric("Rating Logística", f"{rating_log:.2f}/5")
                    
                    st.markdown("---")
                    
                    # ========== GRÁFICAS ADICIONALES AVANZADAS ==========
                    st.markdown("### 📈 Análisis Avanzado de Feedback")
                    
                    col7, col8 = st.columns(2)
                    
                    # Gráfica 1: Scatter - Rating Producto vs Rating Logística
                    with col7:
                        st.markdown("#### 📊 Correlación: Rating Producto vs Rating Logística")
                        
                        # Convertir NPS a un rango positivo para el size
                        df_limpio['NPS_Scaled'] = (df_limpio['Satisfaccion_NPS'] + 100) / 2
                        
                        fig_scatter_ratings = px.scatter(
                            df_limpio,
                            x='Rating_Producto',
                            y='Rating_Logistica',
                            color='Satisfaccion_NPS',
                            size='NPS_Scaled',
                            hover_name='Feedback_ID',
                            hover_data={'Rating_Producto': True, 'Rating_Logistica': True, 'Satisfaccion_NPS': ':.1f', 'NPS_Scaled': False},
                            title="Rating Producto vs Rating Logística",
                            labels={'Rating_Producto': 'Rating Producto (1-5)', 'Rating_Logistica': 'Rating Logística (1-5)'},
                            color_continuous_scale='RdYlGn'
                        )
                        fig_scatter_ratings.update_layout(
                            height=400,
                            hovermode='closest',
                            plot_bgcolor='rgba(240,240,240,0.5)'
                        )
                        st.plotly_chart(fig_scatter_ratings, use_container_width=True)
                    
                    # Gráfica 2: Box Plot - Rating Producto por Rango de Edad
                    with col8:
                        st.markdown("#### 📦 Rating Producto por Rango de Edad")
                        
                        fig_box_prod_edad = px.box(
                            df_limpio,
                            x='Rango_Edad',
                            y='Rating_Producto',
                            color='Rango_Edad',
                            title="Distribución de Rating Producto por Edad",
                            category_orders={'Rango_Edad': ['< 18', '18-25', '26-35', '36-50', '51-65', '65+']},
                            labels={'Rating_Producto': 'Rating (1-5)', 'Rango_Edad': 'Rango de Edad'}
                        )
                        fig_box_prod_edad.update_layout(
                            height=400,
                            showlegend=False
                        )
                        st.plotly_chart(fig_box_prod_edad, use_container_width=True)
                    
                    col9, col10 = st.columns(2)
                    
                    # Gráfica 3: Box Plot - Rating Logística por Rango de Edad
                    with col9:
                        st.markdown("#### 🚚 Rating Logística por Rango de Edad")
                        
                        fig_box_log_edad = px.box(
                            df_limpio,
                            x='Rango_Edad',
                            y='Rating_Logistica',
                            color='Rango_Edad',
                            title="Distribución de Rating Logística por Edad",
                            category_orders={'Rango_Edad': ['< 18', '18-25', '26-35', '36-50', '51-65', '65+']},
                            labels={'Rating_Logistica': 'Rating (1-5)', 'Rango_Edad': 'Rango de Edad'}
                        )
                        fig_box_log_edad.update_layout(
                            height=400,
                            showlegend=False
                        )
                        st.plotly_chart(fig_box_log_edad, use_container_width=True)
                    
                    # Gráfica 4: Scatter - NPS vs Rating Producto
                    with col10:
                        st.markdown("#### 🎯 Satisfacción NPS vs Rating Producto")
                        
                        # Escalar Rating Logistica para size (convertir a positivo si es necesario)
                        df_limpio['Rating_Log_Scaled'] = df_limpio['Rating_Logistica'] * 10
                        
                        fig_scatter_nps = px.scatter(
                            df_limpio,
                            x='Rating_Producto',
                            y='Satisfaccion_NPS',
                            color='Recomienda_Marca',
                            size='Rating_Log_Scaled',
                            hover_name='Feedback_ID',
                            hover_data={'Rating_Producto': True, 'Satisfaccion_NPS': ':.1f', 'Recomienda_Marca': True, 'Rating_Log_Scaled': False},
                            title="NPS vs Rating Producto",
                            labels={'Rating_Producto': 'Rating Producto (1-5)', 'Satisfaccion_NPS': 'Satisfacción NPS'},
                            color_discrete_map={'SI': '#2ecc71', 'MAYBE': '#f39c12', 'NO': '#e74c3c'}
                        )
                        fig_scatter_nps.update_layout(
                            height=400,
                            hovermode='closest',
                            plot_bgcolor='rgba(240,240,240,0.5)'
                        )
                        st.plotly_chart(fig_scatter_nps, use_container_width=True)
                    
                    st.markdown("---")
                    col11, col12 = st.columns(2)
                    
                    # Gráfica 5: Heatmap - Recomienda Marca vs Rating Producto
                    with col11:
                        st.markdown("#### 🔥 Matriz: Recomendación vs Rating Producto")
                        
                        crosstab_recomenda = pd.crosstab(
                            df_limpio['Recomienda_Marca'].astype(str),
                            df_limpio['Rating_Producto'].astype(int)
                        )
                        
                        fig_heatmap_recomenda = px.imshow(
                            crosstab_recomenda,
                            labels=dict(x="Rating Producto", y="Recomienda Marca", color="Cantidad"),
                            color_continuous_scale='YlOrRd',
                            title="Matriz: Recomendación vs Rating Producto",
                            text_auto=True,
                            aspect='auto'
                        )
                        fig_heatmap_recomenda.update_layout(height=400)
                        st.plotly_chart(fig_heatmap_recomenda, use_container_width=True)
                    
                    # Gráfica 6: Histograma - Distribución de Edades
                    with col12:
                        st.markdown("#### 👥 Distribución de Edades de Clientes")
                        
                        fig_hist_edad = px.histogram(
                            df_limpio,
                            x='Edad_Cliente',
                            nbins=20,
                            color_discrete_sequence=['#3498db'],
                            title="Distribución de Edades",
                            labels={'Edad_Cliente': 'Edad (años)', 'count': 'Frecuencia'}
                        )
                        fig_hist_edad.update_layout(
                            height=400,
                            showlegend=False,
                            bargap=0.1
                        )
                        st.plotly_chart(fig_hist_edad, use_container_width=True)
                    
                    st.markdown("---")
                    col13, col14 = st.columns([1.5, 1])
                    
                    # Gráfica 7: Heatmap Correlación
                    with col13:
                        st.markdown("#### 🔗 Matriz de Correlación entre Métricas")
                        
                        # Crear matriz de correlación
                        df_corr = df_limpio[['Rating_Producto', 'Rating_Logistica', 'Satisfaccion_NPS', 'Edad_Cliente']].corr()
                        
                        fig_corr_matrix = px.imshow(
                            df_corr,
                            labels=dict(color="Correlación"),
                            color_continuous_scale='RdBu',
                            color_continuous_midpoint=0,
                            text_auto='.2f',
                            title="Correlación entre Métricas",
                            zmin=-1,
                            zmax=1,
                            aspect='auto'
                        )
                        fig_corr_matrix.update_layout(height=400)
                        st.plotly_chart(fig_corr_matrix, use_container_width=True)
                    
                    # Gráfica 8: Tabla Cruzada - Comentario vs Recomienda
                    with col14:
                        st.markdown("#### 💬 Comentario vs Recomendación")
                        
                        crosstab_comment = pd.crosstab(
                            df_limpio['Comentario_Texto'].astype(str),
                            df_limpio['Recomienda_Marca'].astype(str)
                        )
                        
                        fig_heatmap_comment = px.imshow(
                            crosstab_comment,
                            labels=dict(x="Recomienda Marca", y="Tipo Comentario", color="Cantidad"),
                            color_continuous_scale='Viridis',
                            title="Comentario vs Recomendación",
                            text_auto=True,
                            aspect='auto'
                        )
                        fig_heatmap_comment.update_layout(height=400)
                        st.plotly_chart(fig_heatmap_comment, use_container_width=True)
                    
                    st.markdown("---")
                    
                    # Gráfica 9: Gauge Charts - KPI Dashboard
                    st.markdown("#### 📊 Dashboard de KPIs")
                    
                    col_gauge1, col_gauge2, col_gauge3 = st.columns(3)
                    
                    with col_gauge1:
                        nps_avg = df_limpio['Satisfaccion_NPS'].mean()
                        fig_gauge_nps = go.Figure(go.Indicator(
                            mode="gauge+number+delta",
                            value=nps_avg,
                            domain={'x': [0, 1], 'y': [0, 1]},
                            title={'text': "NPS Promedio"},
                            delta={'reference': 0},
                            gauge={
                                'axis': {'range': [-100, 100]},
                                'bar': {'color': "#3498db"},
                                'steps': [
                                    {'range': [-100, -50], 'color': "#e74c3c"},
                                    {'range': [-50, 0], 'color': "#e67e22"},
                                    {'range': [0, 30], 'color': "#f39c12"},
                                    {'range': [30, 70], 'color': "#3498db"},
                                    {'range': [70, 100], 'color': "#2ecc71"}
                                ],
                                'threshold': {
                                    'line': {'color': "red", 'width': 4},
                                    'thickness': 0.75,
                                    'value': 50
                                }
                            }
                        ))
                        fig_gauge_nps.update_layout(height=300)
                        st.plotly_chart(fig_gauge_nps, use_container_width=True)
                    
                    with col_gauge2:
                        rating_prod_avg = df_limpio['Rating_Producto'].mean()
                        fig_gauge_prod = go.Figure(go.Indicator(
                            mode="gauge+number+delta",
                            value=rating_prod_avg,
                            domain={'x': [0, 1], 'y': [0, 1]},
                            title={'text': "Rating Producto"},
                            delta={'reference': 3},
                            gauge={
                                'axis': {'range': [1, 5]},
                                'bar': {'color': "#f39c12"},
                                'steps': [
                                    {'range': [1, 2], 'color': "#e74c3c"},
                                    {'range': [2, 3], 'color': "#f39c12"},
                                    {'range': [3, 4], 'color': "#3498db"},
                                    {'range': [4, 5], 'color': "#2ecc71"}
                                ],
                                'threshold': {
                                    'line': {'color': "red", 'width': 4},
                                    'thickness': 0.75,
                                    'value': 4
                                }
                            }
                        ))
                        fig_gauge_prod.update_layout(height=300)
                        st.plotly_chart(fig_gauge_prod, use_container_width=True)
                    
                    with col_gauge3:
                        rating_log_avg = df_limpio['Rating_Logistica'].mean()
                        fig_gauge_log = go.Figure(go.Indicator(
                            mode="gauge+number+delta",
                            value=rating_log_avg,
                            domain={'x': [0, 1], 'y': [0, 1]},
                            title={'text': "Rating Logística"},
                            delta={'reference': 3},
                            gauge={
                                'axis': {'range': [1, 5]},
                                'bar': {'color': "#2ecc71"},
                                'steps': [
                                    {'range': [1, 2], 'color': "#e74c3c"},
                                    {'range': [2, 3], 'color': "#f39c12"},
                                    {'range': [3, 4], 'color': "#3498db"},
                                    {'range': [4, 5], 'color': "#2ecc71"}
                                ],
                                'threshold': {
                                    'line': {'color': "red", 'width': 4},
                                    'thickness': 0.75,
                                    'value': 4
                                }
                            }
                        ))
                        fig_gauge_log.update_layout(height=300)
                        st.plotly_chart(fig_gauge_log, use_container_width=True)
                    
                    st.markdown("---")
                    
                    # Gráfica 10: Violin Plot - Rating Producto por Comentario
                    st.markdown("#### 🎻 Violin Plot: Rating Producto por Tipo de Comentario")
                    
                    fig_violin = px.violin(
                        df_limpio,
                        x='Comentario_Texto',
                        y='Rating_Producto',
                        color='Comentario_Texto',
                        box=True,
                        points='outliers',
                        title="Distribución de Rating Producto por Tipo de Comentario",
                        labels={'Rating_Producto': 'Rating (1-5)', 'Comentario_Texto': 'Tipo de Comentario'}
                    )
                    fig_violin.update_layout(
                        height=450,
                        showlegend=False,
                        hovermode='x unified'
                    )
                    st.plotly_chart(fig_violin, use_container_width=True)
                    
                    st.markdown("---")
                    
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
                        label="📥 Descargar Feedback Limpiado (CSV)",
                        data=csv_limpio,
                        file_name="feedback_limpiado.csv",
                        mime="text/csv"
                    )
                except Exception as e:
                    st.error(f"❌ Error al limpiar datos: {e}")
    
    except Exception as e:
        st.error(f"❌ Error al procesar: {e}")
else:
    st.info("📤 Por favor, carga un archivo CSV de Feedback en la barra lateral")


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
            key="groq_key_feedback"
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
        key="btn_generar_feedback"
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
            
            # Preparar resumen de FEEDBACK
            resumen = f"""
Datos de Feedback de Clientes - TechLogistics S.A.

Total de registros: {len(df_limpio)}

Estadísticas de Rating_Producto:
{df_limpio['Rating_Producto'].describe().to_string()}

Estadísticas de Rating_Logistica:
{df_limpio['Rating_Logistica'].describe().to_string()}

Distribución de Satisfaccion_NPS:
{df_limpio['Satisfaccion_NPS'].value_counts().head(10).to_string()}

Análisis de calidad:
- Comentarios con rating producto bajo (≤2): {len(df_limpio[df_limpio['Rating_Producto'] <= 2])} ({(len(df_limpio[df_limpio['Rating_Producto'] <= 2])/len(df_limpio)*100):.1f}%)
- Comentarios con rating logística bajo (≤2): {len(df_limpio[df_limpio['Rating_Logistica'] <= 2])} ({(len(df_limpio[df_limpio['Rating_Logistica'] <= 2])/len(df_limpio)*100):.1f}%)

Rating promedio producto: {df_limpio['Rating_Producto'].mean():.2f}/5.0
Rating promedio logística: {df_limpio['Rating_Logistica'].mean():.2f}/5.0
NPS promedio: {df_limpio['Satisfaccion_NPS'].mean():.2f}/10.0
"""
            
            status_text.text("🧠 Analizando feedback de clientes...")
            progress_bar.progress(60)
            
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{
                    "role": "user",
                    "content": f"""Eres un consultor estratégico senior especializado en experiencia del cliente para TechLogistics S.A.

Analiza estos datos de feedback de clientes:

{resumen}

Genera exactamente 3 párrafos de recomendaciones estratégicas accionables y específicas.

Formato requerido:
- Párrafo 1: Análisis de la satisfacción del cliente y principales hallazgos
- Párrafo 2: Recomendación táctica inmediata para mejorar la experiencia (corto plazo)
- Párrafo 3: Recomendación estratégica para fidelización de clientes (mediano-largo plazo)

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
                <h3 style='color: #333; margin-top: 0;'>📋 Recomendaciones Estratégicas - Feedback Clientes</h3>
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
                    file_name=f"recomendaciones_feedback_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.txt",
                    mime="text/plain",
                    use_container_width=True,
                    key="download_feed"
                )
            
            with col2:
                if st.button("📋 Copiar al Portapapeles", use_container_width=True, key="copy_feed"):
                    st.code(recomendaciones, language=None)
                    st.success("✅ Texto listo para copiar")
            
            with col3:
                if st.button("🔄 Generar Nuevo Análisis", use_container_width=True, key="refresh_feed"):
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
                    revisadas por un experto en experiencia del cliente antes de implementarlas.
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