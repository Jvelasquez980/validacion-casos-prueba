"""
Módulo de Análisis Estratégico - TechLogistics DSS
Las 5 preguntas de alta gerencia
"""

import streamlit as st
import numpy as np
import plotly.express as px


# ================================
# PREGUNTA 1: FUGA DE CAPITAL
# ================================

def render_capital_leak(filtered_data):
    st.subheader("💸 Pregunta 1: Fuga de Capital y Rentabilidad")
    st.markdown("""
    **Objetivo:** Localizar SKUs vendidos con margen negativo y determinar si representan
    una pérdida aceptable por volumen o una falla crítica de precios.
    """)

    if 'Margen_Utilidad' not in filtered_data.columns:
        st.warning("""
        ⚠️ **Columna requerida no encontrada:** `Margen_Utilidad`
        
        Cálculo esperado: `(Precio_Venta - Costo_Unitario) / Precio_Venta * 100`
        """)
        return

    negative_margin = filtered_data[filtered_data['Margen_Utilidad'] < 0].copy()

    if len(negative_margin) == 0:
        st.success("✅ No se detectaron SKUs con margen negativo en el período seleccionado.")
        return

    # KPIs
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        n_skus = negative_margin['SKU'].nunique() if 'SKU' in negative_margin.columns else len(negative_margin)
        st.metric("SKUs con Margen Negativo", f"{n_skus:,}", delta=f"{len(negative_margin):,} ventas")

    with col2:
        if 'Precio_Venta' in negative_margin.columns:
            total_loss = (negative_margin['Margen_Utilidad'] * negative_margin['Precio_Venta'] / 100).sum()
            st.metric("Pérdida Total Estimada", f"${abs(total_loss):,.2f}", delta="Negativo", delta_color="inverse")

    with col3:
        if 'SKU' in filtered_data.columns:
            pct = negative_margin['SKU'].nunique() / filtered_data['SKU'].nunique() * 100
            st.metric("% SKUs Afectados", f"{pct:.1f}%")

    with col4:
        if 'Canal' in negative_margin.columns and 'Precio_Venta' in negative_margin.columns:
            online_df = negative_margin[negative_margin['Canal'] == 'Online']
            if len(online_df) > 0:
                online_loss = (online_df['Margen_Utilidad'] * online_df['Precio_Venta'] / 100).sum()
                st.metric("Pérdida Canal Online", f"${abs(online_loss):,.2f}")

    st.markdown("---")

    # Top 10 SKUs peor margen
    if 'SKU' in negative_margin.columns:
        st.markdown("**📉 Top 10 SKUs con Peor Margen**")
        top_worst = negative_margin.groupby('SKU').agg({'Margen_Utilidad': 'mean'}).sort_values('Margen_Utilidad').head(10)

        fig = px.bar(top_worst.reset_index(), x='SKU', y='Margen_Utilidad',
                     title="SKUs con Peor Margen de Utilidad",
                     color='Margen_Utilidad', color_continuous_scale='Reds',
                     labels={'Margen_Utilidad': 'Margen (%)'})
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.markdown("""
    <div class="warning-box">
    <strong>⚠️ Recomendaciones Críticas:</strong><br><br>
    1. <strong>Revisión Inmediata de Precios:</strong> Ajustar precios de los SKUs con peor margen<br>
    2. <strong>Análisis de Costos:</strong> Verificar si los costos unitarios están correctamente registrados<br>
    3. <strong>Estrategia por Canal:</strong> Revisar política de descuentos por canal<br>
    4. <strong>Decisión de Descatalogación:</strong> Evaluar productos con margen negativo persistente
    </div>
    """, unsafe_allow_html=True)


# ================================
# PREGUNTA 2: CRISIS LOGÍSTICA
# ================================

def render_logistics_crisis(filtered_data):
    st.subheader("🚚 Pregunta 2: Crisis Logística y Cuellos de Botella")
    st.markdown("""
    **Objetivo:** Identificar ciudades y bodegas donde la correlación entre Tiempo de Entrega
    y NPS bajo es más fuerte.
    """)

    required = ['Brecha_Entrega', 'NPS', 'Ciudad', 'Bodega']
    missing = [col for col in required if col not in filtered_data.columns]

    if missing:
        st.warning(f"""
        ⚠️ **Columnas requeridas no encontradas:** {', '.join([f'`{c}`' for c in missing])}
        
        - `Brecha_Entrega`: Dias_Entrega_Real - Lead_Time_Prometido
        - `NPS`: Puntuación de satisfacción (0-10)
        - `Ciudad`: Ciudad de entrega
        - `Bodega`: Bodega de origen
        """)
        return

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**📍 Análisis por Ciudad**")
        city_corr = filtered_data.groupby('Ciudad').apply(
            lambda x: x['Brecha_Entrega'].corr(x['NPS']) if len(x) > 5 else np.nan
        ).sort_values().dropna().head(10)

        if len(city_corr) > 0:
            fig = px.bar(x=city_corr.values, y=city_corr.index, orientation='h',
                         title="Correlación Brecha de Entrega vs NPS por Ciudad",
                         labels={'x': 'Correlación', 'y': 'Ciudad'},
                         color=city_corr.values, color_continuous_scale='RdYlGn_r')
            fig.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay suficientes datos por ciudad.")

    with col2:
        st.markdown("**🏭 Análisis por Bodega**")
        warehouse_corr = filtered_data.groupby('Bodega').apply(
            lambda x: x['Brecha_Entrega'].corr(x['NPS']) if len(x) > 5 else np.nan
        ).sort_values().dropna().head(10)

        if len(warehouse_corr) > 0:
            fig = px.bar(x=warehouse_corr.values, y=warehouse_corr.index, orientation='h',
                         title="Correlación Brecha de Entrega vs NPS por Bodega",
                         labels={'x': 'Correlación', 'y': 'Bodega'},
                         color=warehouse_corr.values, color_continuous_scale='RdYlGn_r')
            fig.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay suficientes datos por bodega.")

    st.markdown("---")
    st.markdown("""
    <div class="warning-box">
    <strong>🚨 Acciones Recomendadas:</strong><br><br>
    <ul>
        <li>Cambio de operador logístico en zonas críticas</li>
        <li>Auditoría de procesos de despacho</li>
        <li>Revisión de promesas de entrega</li>
        <li>Implementación de tracking en tiempo real</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)


# ================================
# PREGUNTA 3: VENTA INVISIBLE
# ================================

def render_invisible_sales(filtered_data):
    st.subheader("👻 Pregunta 3: Análisis de la Venta Invisible")
    st.markdown("""
    **Objetivo:** Cuantificar el impacto financiero de las ventas cuyos SKUs no están
    en el maestro de inventario.
    """)

    if 'SKU_No_Match' not in filtered_data.columns:
        st.warning("""
        ⚠️ **Columna requerida no encontrada:** `SKU_No_Match`
        
        Crea esta columna al hacer el merge entre transacciones e inventario.
        `True` si el SKU no existe en inventario.
        """)
        return

    invisible = filtered_data[filtered_data['SKU_No_Match'] == True]
    total = filtered_data

    # KPIs
    col1, col2, col3 = st.columns(3)

    with col1:
        pct = (len(invisible) / len(total) * 100) if len(total) > 0 else 0
        st.metric("Ventas Sin Control", f"{len(invisible):,}", delta=f"{pct:.1f}% del total")

    with col2:
        if 'Precio_Venta' in invisible.columns:
            inv_rev = invisible['Precio_Venta'].sum()
            tot_rev = total['Precio_Venta'].sum()
            pct_rev = (inv_rev / tot_rev * 100) if tot_rev > 0 else 0
            st.metric("Ingresos en Riesgo", f"${inv_rev:,.2f}", delta=f"{pct_rev:.1f}% del total")

    with col3:
        n_skus = invisible['SKU'].nunique() if 'SKU' in invisible.columns else 0
        st.metric("SKUs No Catalogados", f"{n_skus:,}")

    st.markdown("---")
    st.markdown("""
    <div class="warning-box">
    <strong>💰 Acciones Correctivas:</strong><br><br>
    <ul>
        <li>Catalogar urgentemente los SKUs no catalogados con mayor ingreso</li>
        <li>Implementar validación de SKU en punto de venta</li>
        <li>Sincronización diaria entre sistemas</li>
        <li>Dashboard de alertas para SKUs nuevos detectados</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)


# ================================
# PREGUNTA 4: DIAGNÓSTICO DE FIDELIDAD
# ================================

def render_loyalty_diagnosis(filtered_data):
    st.subheader("😞 Pregunta 4: Diagnóstico de Fidelidad")
    st.markdown("""
    **Objetivo:** Identificar categorías con alta disponibilidad pero sentimiento negativo del cliente.
    """)

    required = ['Categoria', 'Existencias', 'NPS']
    missing = [col for col in required if col not in filtered_data.columns]

    if missing:
        st.warning(f"""
        ⚠️ **Columnas requeridas no encontradas:** {', '.join([f'`{c}`' for c in missing])}
        
        - `Categoria`: Categoría del producto
        - `Existencias`: Stock disponible
        - `NPS`: Puntuación de satisfacción
        """)
        return

    cat_analysis = filtered_data.groupby('Categoria').agg({
        'Existencias': 'mean',
        'NPS': 'mean'
    }).rename(columns={'Existencias': 'Stock_Promedio', 'NPS': 'NPS_Promedio'})

    # Detectar paradoja: alto stock + NPS bajo
    cat_analysis['Paradoja'] = (
        (cat_analysis['Stock_Promedio'] > cat_analysis['Stock_Promedio'].median()) &
        (cat_analysis['NPS_Promedio'] < 7)
    )

    fig = px.scatter(cat_analysis.reset_index(), x='Stock_Promedio', y='NPS_Promedio',
                     color='Paradoja', hover_data=['Categoria'],
                     title='Análisis de Categorías: Stock vs NPS',
                     labels={'Stock_Promedio': 'Stock Promedio', 'NPS_Promedio': 'NPS Promedio'},
                     color_discrete_map={True: '#F96167', False: '#97BC62'})

    fig.add_hline(y=7, line_dash="dash", line_color="red", annotation_text="NPS Crítico")
    fig.add_vline(x=cat_analysis['Stock_Promedio'].median(), line_dash="dash",
                  line_color="gray", annotation_text="Stock Mediano")
    st.plotly_chart(fig, use_container_width=True)

    paradox = cat_analysis[cat_analysis['Paradoja'] == True]
    if len(paradox) > 0:
        st.markdown("---")
        st.markdown("**⚠️ Categorías con Paradoja Detectada**")
        st.dataframe(paradox, use_container_width=True)
    else:
        st.success("✅ No se detectaron categorías con la paradoja de alto stock y bajo NPS.")


# ================================
# PREGUNTA 5: RIESGO OPERATIVO
# ================================

def render_operational_risk(filtered_data):
    st.subheader("⚠️ Pregunta 5: Storytelling de Riesgo Operativo")
    st.markdown("""
    **Objetivo:** Visualizar la relación entre antigüedad de última revisión del stock
    y tasa de tickets de soporte.
    """)

    required = ['Edad_Inventario', 'Ratio_Soporte', 'Bodega']
    missing = [col for col in required if col not in filtered_data.columns]

    if missing:
        st.warning(f"""
        ⚠️ **Columnas requeridas no encontradas:** {', '.join([f'`{c}`' for c in missing])}
        
        - `Edad_Inventario`: Días desde última revisión
        - `Ratio_Soporte`: Tickets de soporte / total ventas
        - `Bodega`: Ubicación del inventario
        """)
        return

    warehouse_risk = filtered_data.groupby('Bodega').agg({
        'Edad_Inventario': 'mean',
        'Ratio_Soporte': 'mean'
    }).rename(columns={
        'Edad_Inventario': 'Dias_Sin_Revision',
        'Ratio_Soporte': 'Tickets_Por_Venta'
    })

    warehouse_risk['Critica'] = warehouse_risk['Dias_Sin_Revision'] > 30
    critical = warehouse_risk[warehouse_risk['Critica'] == True]

    # Gráfico
    fig = px.scatter(warehouse_risk.reset_index(), x='Dias_Sin_Revision', y='Tickets_Por_Venta',
                     color='Critica', hover_data=['Bodega'],
                     title='Riesgo Operativo por Bodega',
                     labels={'Dias_Sin_Revision': 'Días desde Última Revisión',
                             'Tickets_Por_Venta': 'Ratio Tickets de Soporte'},
                     color_discrete_map={True: '#F96167', False: '#97BC62'},
                     trendline="ols")
    fig.add_vline(x=30, line_dash="dash", line_color="red", annotation_text="Límite Crítico (30 días)")
    st.plotly_chart(fig, use_container_width=True)

    # Correlación
    correlation = warehouse_risk['Dias_Sin_Revision'].corr(warehouse_risk['Tickets_Por_Venta'])
    st.metric("Correlación Detectada", f"{correlation:.3f}")

    if len(critical) > 0:
        st.markdown("---")
        st.markdown("**🚨 Bodegas Operando 'A Ciegas'**")
        st.dataframe(critical, use_container_width=True)

    st.markdown("---")
    st.markdown("""
    <div class="warning-box">
    <strong>🔧 Plan de Mejora Operativa:</strong><br><br>
    1. <strong>Acción Inmediata:</strong> Auditoría física en bodegas críticas<br>
    2. <strong>Mediano Plazo:</strong> Sistema de revisión automática cada 14 días<br>
    3. <strong>Transformación:</strong> Digitalización con RFID o códigos QR
    </div>
    """, unsafe_allow_html=True)