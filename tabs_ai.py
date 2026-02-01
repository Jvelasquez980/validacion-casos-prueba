"""
Módulo de Pestaña IA - TechLogistics DSS
Interfaz para generar análisis con Groq/Llama-3
"""

import streamlit as st
import os
from datetime import datetime

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None


def render_ai_recommendations(filtered_data):
    """Renderiza la pestaña completa de recomendaciones con IA"""

    st.markdown("""
    Esta sección utiliza **IA Generativa (Groq/Llama-3)** para analizar tus datos
    y generar recomendaciones estratégicas personalizadas en tiempo real.
    """)

    # Verificar si el módulo de IA está disponible
    try:
        from ia_integration import AIAnalyzer, test_groq_connection
        ai_available = True
    except ImportError:
        ai_available = False
        st.error("❌ Archivo `ia_integration.py` no encontrado. Ponlo en la misma carpeta.")
        return

    # ================================
    # CONFIGURACIÓN DE API KEY
    # ================================
    st.markdown("---")
    st.subheader("🔑 Configuración de API Key")

    col1, col2 = st.columns([2, 1])

    with col1:
        if load_dotenv:
            load_dotenv()
        env_key = os.getenv("GROQ_API_KEY")

        if env_key:
            st.success("✅ API Key encontrada en archivo `.env`")
            manual_api_key = None
        else:
            st.warning("⚠️ No se encontró API Key en `.env`")
            st.markdown("Ingresa tu API Key manualmente:")
            manual_api_key = st.text_input(
                "API Key de Groq",
                type="password",
                help="Obtén una gratis en https://console.groq.com"
            )

    with col2:
        st.markdown("**Obtener API Key:**")
        st.markdown("""
        1. Ve a [console.groq.com](https://console.groq.com)
        2. Crea cuenta gratuita
        3. Ve a "API Keys"
        4. Genera una nueva key
        """)

        if st.button("🧪 Probar Conexión"):
            with st.spinner("Probando..."):
                key = manual_api_key if manual_api_key else None
                result = test_groq_connection(api_key=key)
                if result['success']:
                    st.success(result['message'])
                else:
                    st.error(result['message'])

    st.markdown("---")

    # ================================
    # SELECTOR DE ANÁLISIS
    # ================================
    st.subheader("📊 Tipo de Análisis")

    col1, col2 = st.columns([3, 1])

    with col1:
        analysis_type = st.selectbox("Selecciona el tipo de análisis:", [
            "Resumen General de Datos",
            "Análisis de Rentabilidad",
            "Análisis de Satisfacción del Cliente",
            "Optimización Logística",
            "Gestión de Inventario",
            "Pregunta Personalizada"
        ])

    with col2:
        st.markdown("**Registros actuales:**")
        st.metric("Dataset", f"{len(filtered_data):,}")

    # Pregunta personalizada
    custom_query = None
    if analysis_type == "Pregunta Personalizada":
        custom_query = st.text_area(
            "Escribe tu pregunta de negocio:",
            placeholder="Ejemplo: ¿Cuáles son los 3 principales problemas en mis datos?",
            height=100
        )

    # ================================
    # GENERAR ANÁLISIS
    # ================================
    st.markdown("---")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        btn_disabled = (analysis_type == "Pregunta Personalizada" and not custom_query)
        generate = st.button("🚀 Generar Análisis con IA", type="primary",
                             use_container_width=True, disabled=btn_disabled)

    if not generate:
        return

    # Verificar datos
    if len(filtered_data) == 0:
        st.error("❌ No hay datos para analizar. Sube al menos un archivo CSV.")
        return

    try:
        api_key = manual_api_key if manual_api_key else None
        analyzer = AIAnalyzer(api_key=api_key)

        # Mapeo de tipo de análisis a función
        analysis_map = {
            "Resumen General de Datos": analyzer.analyze_general,
            "Análisis de Rentabilidad": analyzer.analyze_rentabilidad,
            "Análisis de Satisfacción del Cliente": analyzer.analyze_satisfaccion,
            "Optimización Logística": analyzer.analyze_logistica,
            "Gestión de Inventario": analyzer.analyze_inventario,
        }

        with st.spinner("🤖 Analizando datos con IA... Esto puede tardar 10-30 segundos..."):
            if analysis_type == "Pregunta Personalizada":
                result = analyzer.analyze(filtered_data, custom_query, "Análisis Personalizado")
            else:
                result = analysis_map[analysis_type](filtered_data)

        # ================================
        # MOSTRAR RESULTADO
        # ================================
        if result['success']:
            st.markdown("---")
            st.markdown("### 📋 Análisis Generado")

            st.markdown(f"""
            <div class="success-box">
            {result['content'].replace(chr(10), '<br>')}
            </div>
            """, unsafe_allow_html=True)

            # Botones de descarga
            st.markdown("---")
            col1, col2, col3 = st.columns(3)

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

            with col1:
                st.download_button("📥 Descargar (TXT)", data=result['content'],
                                   file_name=f"analisis_ia_{timestamp}.txt",
                                   mime="text/plain", use_container_width=True)
            with col2:
                st.download_button("📥 Descargar (MD)", data=result['content'],
                                   file_name=f"analisis_ia_{timestamp}.md",
                                   mime="text/markdown", use_container_width=True)
            with col3:
                if st.button("📋 Ver Texto Plano", use_container_width=True):
                    st.code(result['content'], language=None)

            # Info del análisis
            with st.expander("ℹ️ Información sobre este Análisis"):
                st.markdown(f"""
                - **Tipo:** {analysis_type}
                - **Registros analizados:** {len(filtered_data):,}
                - **Modelo:** Llama-3.1 70B (via Groq)
                - **Fecha:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

                > ⚠️ Este análisis es generado por IA basándose en los datos que subiste.
                > Las recomendaciones deben validarse antes de implementarlas.
                """)
        else:
            st.markdown("---")
            st.error(result['error'])

    except ValueError as e:
        st.error(f"""
        ❌ **Error de Configuración:** {str(e)}
        
        Configura tu API Key en `.env` o ingrésala manualmente arriba.
        """)
    except Exception as e:
        st.error(f"""
        ❌ **Error Inesperado:** {str(e)}
        
        Verifica que `ia_integration.py` esté en la misma carpeta
        y que tengas instaladas las dependencias: `pip install groq python-dotenv`
        """)