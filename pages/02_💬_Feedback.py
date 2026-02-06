import streamlit as st
import pandas as pd
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