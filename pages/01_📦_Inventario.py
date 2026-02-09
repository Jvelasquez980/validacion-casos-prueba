import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
                    
                    # ========== GRÁFICAS DE ANÁLISIS ==========
                    st.markdown("### 📊 Análisis de Inventario - Gráficas")
                    
                    # Crear columnas para las gráficas
                    col1, col2 = st.columns(2)
                    
                    # Gráfica 1: Cantidad de productos por categoría
                    with col1:
                        st.markdown("#### 📦 Cantidad de Productos por Categoría")
                        productos_categoria = df_limpio['Categoria'].value_counts().reset_index()
                        productos_categoria.columns = ['Categoria', 'Cantidad']
                        
                        fig_productos = px.bar(
                            productos_categoria,
                            x='Categoria',
                            y='Cantidad',
                            color='Cantidad',
                            color_continuous_scale='Viridis',
                            text='Cantidad',
                            title="Cantidad de Productos por Categoría"
                        )
                        fig_productos.update_layout(
                            height=400,
                            xaxis_title="Categoría",
                            yaxis_title="Cantidad de Productos",
                            hovermode='x unified',
                            showlegend=False
                        )
                        fig_productos.update_traces(textposition='auto')
                        st.plotly_chart(fig_productos, use_container_width=True)
                    
                    # Gráfica 2: Costo promedio por categoría
                    with col2:
                        st.markdown("#### 💰 Costo Promedio (USD) por Categoría")
                        costo_categoria = df_limpio.groupby('Categoria')['Costo_Unitario_USD'].mean().reset_index()
                        costo_categoria.columns = ['Categoria', 'Costo_Promedio']
                        costo_categoria = costo_categoria.sort_values('Costo_Promedio', ascending=False)
                        
                        fig_costo = px.bar(
                            costo_categoria,
                            x='Categoria',
                            y='Costo_Promedio',
                            color='Costo_Promedio',
                            color_continuous_scale='RdYlGn_r',
                            text=costo_categoria['Costo_Promedio'].apply(lambda x: f'${x:.2f}'),
                            title="Costo Promedio por Categoría"
                        )
                        fig_costo.update_layout(
                            height=400,
                            xaxis_title="Categoría",
                            yaxis_title="Costo Promedio (USD)",
                            hovermode='x unified',
                            showlegend=False
                        )
                        fig_costo.update_traces(textposition='auto')
                        st.plotly_chart(fig_costo, use_container_width=True)
                    
                    col3, col4 = st.columns(2)
                    
                    # Gráfica 3: Distribución de bodegas por categoría
                    with col3:
                        st.markdown("#### 🏭 Distribución de Bodegas por Categoría")
                        bodega_categoria = df_limpio.groupby('Categoria')['Bodega_Origen'].nunique().reset_index()
                        bodega_categoria.columns = ['Categoria', 'Cantidad_Bodegas']
                        
                        fig_bodega = px.bar(
                            bodega_categoria,
                            x='Categoria',
                            y='Cantidad_Bodegas',
                            color='Cantidad_Bodegas',
                            color_continuous_scale='Plasma',
                            text='Cantidad_Bodegas',
                            title="Cantidad de Bodegas por Categoría"
                        )
                        fig_bodega.update_layout(
                            height=400,
                            xaxis_title="Categoría",
                            yaxis_title="Cantidad de Bodegas",
                            hovermode='x unified',
                            showlegend=False
                        )
                        fig_bodega.update_traces(textposition='auto')
                        st.plotly_chart(fig_bodega, use_container_width=True)
                    
                    # Gráfica 4: Stock actual total por categoría
                    with col4:
                        st.markdown("#### 📈 Stock Actual Total por Categoría")
                        stock_categoria = df_limpio.groupby('Categoria')['Stock_Actual'].sum().reset_index()
                        stock_categoria.columns = ['Categoria', 'Stock_Total']
                        stock_categoria = stock_categoria.sort_values('Stock_Total', ascending=False)
                        
                        fig_stock = px.bar(
                            stock_categoria,
                            x='Categoria',
                            y='Stock_Total',
                            color='Stock_Total',
                            color_continuous_scale='Blues',
                            text='Stock_Total',
                            title="Stock Actual Total por Categoría"
                        )
                        fig_stock.update_layout(
                            height=400,
                            xaxis_title="Categoría",
                            yaxis_title="Stock Total (Unidades)",
                            hovermode='x unified',
                            showlegend=False
                        )
                        fig_stock.update_traces(textposition='auto')
                        st.plotly_chart(fig_stock, use_container_width=True)
                    
                    st.markdown("---")
                    
                    # ========== GRÁFICAS ADICIONALES ==========
                    st.markdown("### 📈 Análisis Avanzado de Inventario")
                    
                    col5, col6 = st.columns(2)
                    
                    # Gráfica 5: Valor total del inventario por categoría
                    with col5:
                        st.markdown("#### 💎 Valor Total del Inventario por Categoría")
                        df_limpio['Valor_Total'] = df_limpio['Stock_Actual'] * df_limpio['Costo_Unitario_USD']
                        valor_categoria = df_limpio.groupby('Categoria')['Valor_Total'].sum().reset_index()
                        valor_categoria.columns = ['Categoria', 'Valor_Total']
                        valor_categoria = valor_categoria.sort_values('Valor_Total', ascending=False)
                        
                        fig_valor = px.pie(
                            valor_categoria,
                            names='Categoria',
                            values='Valor_Total',
                            title="Valor Total del Inventario por Categoría",
                            hover_data={'Valor_Total': ':.2f'}
                        )
                        fig_valor.update_traces(
                            textposition='inside',
                            textinfo='label+percent',
                            hovertemplate='<b>%{label}</b><br>Valor: $%{value:,.2f} USD<extra></extra>'
                        )
                        fig_valor.update_layout(height=400)
                        st.plotly_chart(fig_valor, use_container_width=True)
                    
                    # Gráfica 6: Productos en stock crítico
                    with col6:
                        st.markdown("#### 🚨 Productos en Stock Crítico")
                        df_critico = df_limpio[df_limpio['Stock_Actual'] < df_limpio['Punto_Reorden']].copy()
                        df_critico['Deficiencia'] = df_critico['Punto_Reorden'] - df_critico['Stock_Actual']
                        
                        critico_categoria = df_critico.groupby('Categoria').size().reset_index(name='Cantidad_Critica')
                        
                        fig_critico = px.bar(
                            critico_categoria,
                            x='Categoria',
                            y='Cantidad_Critica',
                            color='Cantidad_Critica',
                            color_continuous_scale='Reds',
                            text='Cantidad_Critica',
                            title="Productos en Stock Crítico"
                        )
                        fig_critico.update_layout(
                            height=400,
                            xaxis_title="Categoría",
                            yaxis_title="Cantidad de Productos Críticos",
                            hovermode='x unified',
                            showlegend=False
                        )
                        fig_critico.update_traces(textposition='auto')
                        st.plotly_chart(fig_critico, use_container_width=True)
                        
                        # Mostrar alerta si hay productos críticos
                        if len(df_critico) > 0:
                            st.warning(f"⚠️ {len(df_critico)} productos tienen stock por debajo del punto de reorden")
                    
                    col7, col8 = st.columns(2)
                    
                    # Gráfica 7: Distribución de stock por bodega (Sunburst)
                    with col7:
                        st.markdown("#### 🏭 Distribución de Stock por Bodega y Categoría")
                        bodega_distribucion = df_limpio.groupby(['Bodega_Origen', 'Categoria'])['Stock_Actual'].sum().reset_index()
                        
                        # Preparar datos para sunburst
                        bodega_total = df_limpio.groupby('Bodega_Origen')['Stock_Actual'].sum().reset_index()
                        
                        labels_list = ['Total'] + bodega_total['Bodega_Origen'].tolist() + [f"{row['Bodega_Origen']} - {row['Categoria']}" for _, row in bodega_distribucion.iterrows()]
                        parents_list = [''] + ['Total'] * len(bodega_total) + bodega_total['Bodega_Origen'].tolist()
                        values_list = [bodega_total['Stock_Actual'].sum()] + bodega_total['Stock_Actual'].tolist() + bodega_distribucion['Stock_Actual'].tolist()
                        
                        fig_sunburst = go.Figure(go.Sunburst(
                            labels=labels_list,
                            parents=parents_list,
                            values=values_list,
                            marker=dict(colorscale='Spectral'),
                            hovertemplate='<b>%{label}</b><br>Stock: %{value} unidades<extra></extra>'
                        ))
                        fig_sunburst.update_layout(height=400, title="Stock por Bodega y Categoría")
                        st.plotly_chart(fig_sunburst, use_container_width=True)
                    
                    # Gráfica 8: Lead Time promedio por categoría
                    with col8:
                        st.markdown("#### ⏱️ Lead Time Promedio (días) por Categoría")
                        leadtime_categoria = df_limpio.groupby('Categoria')['Lead_Time_Dias'].mean().reset_index()
                        leadtime_categoria.columns = ['Categoria', 'Lead_Time_Promedio']
                        leadtime_categoria = leadtime_categoria.sort_values('Lead_Time_Promedio', ascending=False)
                        
                        fig_leadtime = px.bar(
                            leadtime_categoria,
                            x='Categoria',
                            y='Lead_Time_Promedio',
                            color='Lead_Time_Promedio',
                            color_continuous_scale='Oranges',
                            text=leadtime_categoria['Lead_Time_Promedio'].apply(lambda x: f'{x:.1f} días'),
                            title="Lead Time Promedio por Categoría"
                        )
                        fig_leadtime.update_layout(
                            height=400,
                            xaxis_title="Categoría",
                            yaxis_title="Lead Time Promedio (días)",
                            hovermode='x unified',
                            showlegend=False
                        )
                        fig_leadtime.update_traces(textposition='auto')
                        st.plotly_chart(fig_leadtime, use_container_width=True)
                    
                    col9, col10 = st.columns(2)
                    
                    # Gráfica 9: Scatter Plot - Costo vs Stock
                    with col9:
                        st.markdown("#### 💰 Análisis de Riesgo: Costo vs Stock")
                        
                        fig_scatter = px.scatter(
                            df_limpio,
                            x='Stock_Actual',
                            y='Costo_Unitario_USD',
                            color='Categoria',
                            size='Valor_Total',
                            hover_name='SKU_ID',
                            hover_data={'Stock_Actual': True, 'Costo_Unitario_USD': ':.2f', 'Categoria': True, 'Valor_Total': ':.2f'},
                            title="Análisis de Riesgo: Costo vs Stock",
                            labels={'Stock_Actual': 'Stock Actual (Unidades)', 'Costo_Unitario_USD': 'Costo Unitario (USD)'}
                        )
                        fig_scatter.update_traces(
                            marker=dict(opacity=0.6, line=dict(width=1)),
                            textposition="top center"
                        )
                        fig_scatter.update_layout(
                            height=400,
                            hovermode='closest',
                            plot_bgcolor='rgba(240,240,240,0.5)',
                            showlegend=True,
                            legend=dict(
                                x=1.02,
                                y=1,
                                bgcolor='rgba(255, 255, 255, 0.8)',
                                bordercolor='rgba(0, 0, 0, 0.1)',
                                borderwidth=1
                            )
                        )
                        # Agregar línea de referencia del punto de reorden promedio
                        stock_promedio = df_limpio['Stock_Actual'].mean()
                        costo_promedio = df_limpio['Costo_Unitario_USD'].mean()
                        
                        fig_scatter.add_vline(x=stock_promedio, line_dash="dash", line_color="gray", 
                                             annotation_text="Stock Promedio", annotation_position="top right",
                                             line_width=2)
                        fig_scatter.add_hline(y=costo_promedio, line_dash="dash", line_color="gray",
                                             annotation_text="Costo Promedio", annotation_position="right",
                                             line_width=2)
                        
                        # Agregar zoom interactivo
                        fig_scatter.update_xaxes(fixedrange=False)
                        fig_scatter.update_yaxes(fixedrange=False)
                        
                        st.plotly_chart(fig_scatter, use_container_width=True)
                        
                        # Información adicional para entender el gráfico
                        col_info1, col_info2, col_info3 = st.columns(3)
                        with col_info1:
                            st.metric("Stock Promedio", f"{stock_promedio:.0f} unidades")
                        with col_info2:
                            st.metric("Costo Promedio", f"${costo_promedio:.2f}")
                        with col_info3:
                            productos_riesgo = len(df_limpio[(df_limpio['Stock_Actual'] < stock_promedio) & 
                                                             (df_limpio['Costo_Unitario_USD'] > costo_promedio)])
                            st.metric("Productos Riesgo", f"{productos_riesgo} (alto costo, bajo stock)")
                    
                    # Gráfica 10: Antigüedad de última revisión por categoría
                    with col10:
                        st.markdown("#### 📅 Antigüedad de Última Revisión por Categoría")
                        from datetime import datetime
                        
                        df_limpio['Ultima_Revision'] = pd.to_datetime(df_limpio['Ultima_Revision'])
                        df_limpio['Dias_Desde_Revision'] = (datetime.now() - df_limpio['Ultima_Revision']).dt.days
                        
                        antiguedad_categoria = df_limpio.groupby('Categoria')['Dias_Desde_Revision'].mean().reset_index()
                        antiguedad_categoria.columns = ['Categoria', 'Dias_Promedio']
                        antiguedad_categoria = antiguedad_categoria.sort_values('Dias_Promedio', ascending=False)
                        
                        fig_antiguedad = px.bar(
                            antiguedad_categoria,
                            x='Categoria',
                            y='Dias_Promedio',
                            color='Dias_Promedio',
                            color_continuous_scale='YlOrRd',
                            text=antiguedad_categoria['Dias_Promedio'].apply(lambda x: f'{int(x)} días'),
                            title="Antigüedad Promedio de Revisión"
                        )
                        fig_antiguedad.update_layout(
                            height=400,
                            xaxis_title="Categoría",
                            yaxis_title="Días desde última revisión",
                            hovermode='x unified',
                            showlegend=False
                        )
                        fig_antiguedad.update_traces(textposition='auto')
                        st.plotly_chart(fig_antiguedad, use_container_width=True)
                    
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
                        label="📥 Descargar Inventario Limpiado (CSV)",
                        data=csv_limpio,
                        file_name="inventario_limpiado.csv",
                        mime="text/csv"
                    )
                except Exception as e:
                    st.error(f"❌ Error al limpiar datos: {e}")
    
    except Exception as e:
        st.error(f"❌ Error al procesar: {e}")
else:
    st.info("📤 Por favor, carga un archivo CSV de Inventario en la barra lateral")

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
            key="groq_key_inventario"
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
        key="btn_generar_inventario"
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
            
            # Preparar resumen de INVENTARIO
            resumen = f"""
Datos de Inventario - TechLogistics S.A.

Total de productos en catálogo: {len(df_limpio)}

Estadísticas de Stock Actual:
{df_limpio['Stock_Actual'].describe().to_string()}

Productos con stock crítico (< Punto_Reorden):
{len(df_limpio[df_limpio['Stock_Actual'] < df_limpio['Punto_Reorden']])} productos ({(len(df_limpio[df_limpio['Stock_Actual'] < df_limpio['Punto_Reorden']])/len(df_limpio)*100):.1f}%)

Distribución por bodega:
{df_limpio['Bodega_Origen'].value_counts().to_string()}

Estadísticas de costos:
{df_limpio['Costo_Unitario_USD'].describe().to_string()}

Valor total del inventario: ${(df_limpio['Stock_Actual'] * df_limpio['Costo_Unitario_USD']).sum():,.2f} USD

Lead time promedio: {df_limpio['Lead_Time_Dias'].mean():.1f} días
"""
            
            status_text.text("🧠 Analizando datos de inventario...")
            progress_bar.progress(60)
            
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{
                    "role": "user",
                    "content": f"""Eres un consultor estratégico senior especializado en gestión de inventarios para TechLogistics S.A.

Analiza estos datos de inventario:

{resumen}

Genera exactamente 3 párrafos de recomendaciones estratégicas accionables y específicas.

Formato requerido:
- Párrafo 1: Análisis de la situación actual del inventario y principales hallazgos críticos
- Párrafo 2: Recomendación táctica inmediata para optimizar stock (corto plazo)
- Párrafo 3: Recomendación estratégica para gestión de inventario (mediano-largo plazo)

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
                <h3 style='color: #333; margin-top: 0;'>📋 Recomendaciones Estratégicas - Inventario</h3>
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
                    file_name=f"recomendaciones_inventario_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.txt",
                    mime="text/plain",
                    use_container_width=True,
                    key="download_inv"
                )
            
            with col2:
                if st.button("📋 Copiar al Portapapeles", use_container_width=True, key="copy_inv"):
                    st.code(recomendaciones, language=None)
                    st.success("✅ Texto listo para copiar")
            
            with col3:
                if st.button("🔄 Generar Nuevo Análisis", use_container_width=True, key="refresh_inv"):
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
                    revisadas por un experto en gestión de inventarios antes de implementarlas.
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