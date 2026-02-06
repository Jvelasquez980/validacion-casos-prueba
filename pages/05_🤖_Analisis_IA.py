import streamlit as st
import pandas as pd
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Análisis con IA", page_icon="🤖")
st.title("🤖 Análisis Estratégico con IA")

# Inicializar cliente Groq
@st.cache_resource
def init_groq():
    return Groq(api_key=os.getenv("GROQ_API_KEY"))

client = init_groq()

# Cargar datos (reutiliza tu lógica de data_loader.py)
@st.cache_data
def load_data():
    # Adapta según tu estructura
    feedback = pd.read_csv('data/feedback_clientes_limpio.csv')
    inventario = pd.read_csv('data/inventario_central_limpio.csv')
    transacciones = pd.read_csv('data/transaccion_completa_limpio.csv')
    return feedback, inventario, transacciones

# Función para generar análisis
def generar_analisis(datos_resumen, contexto=""):
    prompt = f"""
Eres un analista de datos estratégico. Basándote en los siguientes datos:

{datos_resumen}

{contexto}

Genera:
1. Un resumen estadístico conciso de los hallazgos clave
2. Tres párrafos de recomendaciones estratégicas accionables y específicas

Formato:
## Resumen Estadístico
[tu análisis]

## Recomendaciones Estratégicas
### 1. [Título recomendación]
[párrafo]

### 2. [Título recomendación]
[párrafo]

### 3. [Título recomendación]
[párrafo]
"""
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",  # o "llama-3.1-70b-versatile"
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=2000
    )
    
    return response.choices[0].message.content

# UI Principal
feedback, inventario, transacciones = load_data()

st.sidebar.header("Filtros de Datos")

# Ejemplo de filtros (adapta a tus necesidades)
dataset_seleccionado = st.sidebar.selectbox(
    "Selecciona dataset para analizar:",
    ["Feedback Clientes", "Inventario", "Transacciones", "Análisis Integrado"]
)

if dataset_seleccionado == "Feedback Clientes":
    # Filtros específicos
    categorias = st.sidebar.multiselect(
        "Categorías de producto",
        options=feedback['categoria'].unique() if 'categoria' in feedback.columns else [],
        default=None
    )
    
    # Filtrar datos
    df_filtrado = feedback.copy()
    if categorias:
        df_filtrado = df_filtrado[df_filtrado['categoria'].isin(categorias)]
    
    # Mostrar datos filtrados
    st.subheader("📊 Datos Filtrados")
    st.dataframe(df_filtrado.head(10))
    
    # Preparar resumen para IA
    resumen = f"""
Total de registros: {len(df_filtrado)}
Calificación promedio: {df_filtrado['calificacion'].mean():.2f}
Distribución por categoría:
{df_filtrado['categoria'].value_counts().to_string()}
    """
    
elif dataset_seleccionado == "Inventario":
    df_filtrado = inventario.copy()
    resumen = f"""
Total productos: {len(df_filtrado)}
Stock total: {df_filtrado['stock'].sum()}
Productos bajo stock mínimo: {len(df_filtrado[df_filtrado['stock'] < df_filtrado['stock_minimo']])}
    """

# Botón para generar análisis
if st.button("🚀 Generar Análisis con IA", type="primary"):
    with st.spinner("Analizando datos con Llama-3..."):
        try:
            analisis = generar_analisis(
                resumen,
                f"Contexto: Análisis de {dataset_seleccionado}"
            )
            
            st.markdown("---")
            st.markdown(analisis)
            
            # Opción de descarga
            st.download_button(
                "📥 Descargar Análisis",
                analisis,
                file_name=f"analisis_ia_{dataset_seleccionado.lower().replace(' ', '_')}.md",
                mime="text/markdown"
            )
            
        except Exception as e:
            st.error(f"Error al generar análisis: {str(e)}")