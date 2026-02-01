"""
Módulo de Integración con IA - Groq/Llama-3
TechLogistics S.A.S.

Este módulo maneja la comunicación con la API de Groq para generar
análisis y recomendaciones estratégicas en tiempo real.
"""

import os
from groq import Groq
from dotenv import load_dotenv
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

# ================================
# CONFIGURACIÓN
# ================================

class AIAnalyzer:
    """
    Clase para análisis con IA usando Groq/Llama-3
    """
    
    def __init__(self, api_key=None):
        """
        Inicializa el cliente de Groq
        
        Parameters:
        -----------
        api_key : str, optional
            API key de Groq. Si no se proporciona, se carga de .env
        """
        load_dotenv()
        
        if api_key:
            self.api_key = api_key
        else:
            self.api_key = os.getenv("GROQ_API_KEY")
        
        if not self.api_key:
            raise ValueError(
                "❌ API Key de Groq no encontrada. "
                "Configura GROQ_API_KEY en tu archivo .env o proporciona la key directamente"
            )
        
        self.client = Groq(api_key=self.api_key)
        self.model = "llama-3.1-70b-versatile"
    
    # ================================
    # PREPARACIÓN DE DATOS
    # ================================
    
    def prepare_data_summary(self, df):
        """
        Prepara un resumen estadístico conciso de los datos
        
        Parameters:
        -----------
        df : pd.DataFrame
            Dataset filtrado por el usuario
        
        Returns:
        --------
        str : Resumen en formato texto
        """
        if df is None or len(df) == 0:
            return "No hay datos disponibles para analizar."
        
        summary_parts = []
        
        # Información general
        summary_parts.append(f"Dataset: {len(df):,} registros, {len(df.columns)} columnas")
        
        # Período si hay fechas
        date_cols = ['Fecha_Venta', 'Fecha_Entrega', 'Fecha_Registro']
        for col in date_cols:
            if col in df.columns and pd.api.types.is_datetime64_any_dtype(df[col]):
                min_date = df[col].min()
                max_date = df[col].max()
                if pd.notna(min_date) and pd.notna(max_date):
                    summary_parts.append(f"Período ({col}): {min_date.date()} a {max_date.date()}")
                    break
        
        # KPIs principales
        summary_parts.append("\nKPIs Principales:")
        
        if 'Precio_Venta' in df.columns:
            ingresos = df['Precio_Venta'].sum()
            ticket_promedio = df['Precio_Venta'].mean()
            summary_parts.append(f"- Ingresos Totales: ${ingresos:,.2f}")
            summary_parts.append(f"- Ticket Promedio: ${ticket_promedio:,.2f}")
        
        if 'NPS' in df.columns:
            nps_avg = df['NPS'].mean()
            summary_parts.append(f"- NPS Promedio: {nps_avg:.2f}")
            
            # Distribución NPS
            detractores = (df['NPS'] <= 6).sum()
            neutrales = ((df['NPS'] == 7) | (df['NPS'] == 8)).sum()
            promotores = (df['NPS'] >= 9).sum()
            total_nps = detractores + neutrales + promotores
            if total_nps > 0:
                summary_parts.append(f"  · Detractores (0-6): {detractores:,} ({detractores/total_nps*100:.1f}%)")
                summary_parts.append(f"  · Neutrales (7-8): {neutrales:,} ({neutrales/total_nps*100:.1f}%)")
                summary_parts.append(f"  · Promotores (9-10): {promotores:,} ({promotores/total_nps*100:.1f}%)")
        
        if 'Margen_Utilidad' in df.columns:
            margen_avg = df['Margen_Utilidad'].mean()
            margen_median = df['Margen_Utilidad'].median()
            summary_parts.append(f"- Margen Promedio: {margen_avg:.2f}% (Mediana: {margen_median:.2f}%)")
            
            # Productos con margen negativo
            neg_margin = df[df['Margen_Utilidad'] < 0]
            if len(neg_margin) > 0:
                pct_neg = len(neg_margin) / len(df) * 100
                loss = (neg_margin['Margen_Utilidad'] * neg_margin['Precio_Venta'] / 100).sum() if 'Precio_Venta' in neg_margin.columns else 0
                summary_parts.append(f"  · SKUs con Margen Negativo: {len(neg_margin):,} ({pct_neg:.1f}%) - Pérdida: ${abs(loss):,.2f}")
        
        if 'Brecha_Entrega' in df.columns:
            brecha_avg = df['Brecha_Entrega'].mean()
            brecha_median = df['Brecha_Entrega'].median()
            entregas_tarde = (df['Brecha_Entrega'] > 0).sum()
            pct_tarde = entregas_tarde / len(df) * 100
            summary_parts.append(f"- Brecha de Entrega Promedio: {brecha_avg:.1f} días (Mediana: {brecha_median:.1f})")
            summary_parts.append(f"  · Entregas tardías: {entregas_tarde:,} ({pct_tarde:.1f}%)")
        
        if 'Existencias' in df.columns:
            stock_total = df['Existencias'].sum()
            stock_promedio = df['Existencias'].mean()
            summary_parts.append(f"- Stock Total: {stock_total:,.0f} unidades (Promedio por SKU: {stock_promedio:.0f})")
        
        # Distribución por dimensiones clave
        if 'Canal' in df.columns:
            canal_dist = df['Canal'].value_counts().to_dict()
            summary_parts.append(f"\nDistribución por Canal: {canal_dist}")
            
            # Ingresos por canal si está disponible
            if 'Precio_Venta' in df.columns:
                canal_ingresos = df.groupby('Canal')['Precio_Venta'].sum().to_dict()
                summary_parts.append(f"Ingresos por Canal: {', '.join([f'{k}: ${v:,.0f}' for k, v in canal_ingresos.items()])}")
        
        if 'Categoria' in df.columns:
            if 'Precio_Venta' in df.columns:
                top_cat = df.groupby('Categoria')['Precio_Venta'].sum().nlargest(5).to_dict()
                summary_parts.append(f"\nTop 5 Categorías por Ingresos:")
                for cat, ing in top_cat.items():
                    summary_parts.append(f"  · {cat}: ${ing:,.2f}")
            else:
                top_cat = df['Categoria'].value_counts().head(5).to_dict()
                summary_parts.append(f"\nTop 5 Categorías por Volumen: {top_cat}")
        
        if 'Ciudad' in df.columns:
            ciudad_dist = df['Ciudad'].value_counts().head(5).to_dict()
            summary_parts.append(f"\nTop 5 Ciudades: {ciudad_dist}")
        
        if 'Bodega' in df.columns:
            bodegas = df['Bodega'].nunique()
            summary_parts.append(f"\nBodegas Activas: {bodegas}")
        
        # Problemas detectados
        problemas = []
        
        if 'SKU_No_Match' in df.columns:
            skus_no_match = (df['SKU_No_Match'] == True).sum()
            if skus_no_match > 0:
                pct = skus_no_match / len(df) * 100
                ingresos_riesgo = df[df['SKU_No_Match'] == True]['Precio_Venta'].sum() if 'Precio_Venta' in df.columns else 0
                problemas.append(f"  · Ventas sin SKU catalogado: {skus_no_match:,} ({pct:.1f}%) - ${ingresos_riesgo:,.2f} en riesgo")
        
        if 'Edad_Inventario' in df.columns:
            inventario_viejo = (df['Edad_Inventario'] > 30).sum()
            if inventario_viejo > 0:
                pct_viejo = inventario_viejo / len(df) * 100
                problemas.append(f"  · Registros con inventario >30 días sin revisión: {inventario_viejo:,} ({pct_viejo:.1f}%)")
            
            if 'Bodega' in df.columns:
                bodegas_criticas = df[df['Edad_Inventario'] > 30]['Bodega'].nunique()
                if bodegas_criticas > 0:
                    problemas.append(f"  · Bodegas con inventario >30 días sin revisión: {bodegas_criticas}")
        
        if 'Ratio_Soporte' in df.columns:
            ratio_alto = (df['Ratio_Soporte'] > 0.1).sum()  # >10% de tickets
            if ratio_alto > 0:
                pct_ratio = ratio_alto / len(df) * 100
                problemas.append(f"  · Productos con alto ratio de soporte (>10%): {ratio_alto:,} ({pct_ratio:.1f}%)")
        
        if problemas:
            summary_parts.append("\n⚠️ Problemas Detectados:")
            summary_parts.extend(problemas)
        else:
            summary_parts.append("\n✅ No se detectaron problemas críticos evidentes")
        
        return "\n".join(summary_parts)
    
    # ================================
    # CONSTRUCCIÓN DE PROMPTS
    # ================================
    
    def build_analysis_prompt(self, data_summary, query, analysis_type="general"):
        """
        Construye el prompt para el modelo de IA
        
        Parameters:
        -----------
        data_summary : str
            Resumen de los datos
        query : str
            Pregunta o solicitud del usuario
        analysis_type : str
            Tipo de análisis solicitado
        
        Returns:
        --------
        str : Prompt completo
        """
        prompt = f"""Eres un consultor senior experto en análisis de datos para retail tecnológico.
Tu especialidad es convertir datos complejos en recomendaciones estratégicas accionables.

CONTEXTO DE NEGOCIO:
TechLogistics S.A.S. es una empresa de retail tecnológico que enfrenta:
- Erosión de márgenes de beneficio
- Caída drástica en lealtad de clientes (NPS bajo)
- Problemas de visibilidad operativa (sistemas no integrados)
- Desafíos logísticos con tiempos de entrega
- Gestión de inventario ineficiente

DATOS DISPONIBLES:
{data_summary}

TIPO DE ANÁLISIS SOLICITADO: {analysis_type}

PREGUNTA ESPECÍFICA DEL USUARIO:
{query}

INSTRUCCIONES:
Proporciona un análisis estructurado en exactamente 3 secciones:

**1. DIAGNÓSTICO (¿Qué está pasando?)**
- Interpreta los datos actuales con números específicos
- Identifica patrones, tendencias y anomalías
- Destaca la severidad de los problemas
- Compara con benchmarks del sector retail cuando sea relevante

**2. ANÁLISIS DE CAUSA RAÍZ (¿Por qué está pasando?)**
- Explica las razones subyacentes de los problemas identificados
- Conecta los síntomas con causas probables
- Considera factores operativos, estratégicos y de mercado
- Identifica interdependencias entre problemas
- Prioriza las causas por impacto

**3. RECOMENDACIONES ESTRATÉGICAS (¿Qué hacer?)**
Divide en tres horizontes temporales:

a) **Acciones Inmediatas (0-15 días):**
   - Quick wins que no requieren inversión significativa
   - Decisiones urgentes para contener problemas críticos

b) **Mediano Plazo (30-60 días):**
   - Iniciativas que requieren coordinación entre áreas
   - Cambios de procesos o proveedores

c) **Transformación Estructural (90+ días):**
   - Inversiones en tecnología o sistemas
   - Cambios organizacionales o estratégicos

Para cada recomendación incluye:
- Métrica de éxito
- Impacto financiero estimado (cuando sea posible)
- Responsable sugerido

IMPORTANTE:
- Usa SOLO datos del resumen proporcionado (no inventes cifras)
- Sé directo y ejecutivo (escribe para CEO/CFO)
- Enfócate en insights ACCIONABLES, no teoría
- Prioriza por impacto financiero y urgencia
- Menciona nombres específicos cuando estén disponibles (SKUs, bodegas, categorías, ciudades)
- Usa formato profesional pero accesible
- Si los datos son insuficientes para algún análisis, indícalo claramente

Responde en español de manera profesional, como si estuvieras presentando a la junta directiva.
"""
        return prompt
    
    # ================================
    # ANÁLISIS PRINCIPAL
    # ================================
    
    def analyze(self, df, query, analysis_type="general"):
        """
        Genera análisis con IA basado en los datos filtrados
        
        Parameters:
        -----------
        df : pd.DataFrame
            Dataset filtrado por el usuario
        query : str
            Pregunta o solicitud del usuario
        analysis_type : str
            Tipo de análisis ("general", "rentabilidad", "satisfaccion", "logistica", "inventario")
        
        Returns:
        --------
        dict : Diccionario con 'success' (bool), 'content' (str), y 'error' (str opcional)
        """
        try:
            # Validar que hay datos
            if df is None or len(df) == 0:
                return {
                    'success': False,
                    'content': '',
                    'error': 'No hay datos disponibles para analizar. Por favor, carga al menos un archivo CSV.'
                }
            
            # Preparar resumen de datos
            data_summary = self.prepare_data_summary(df)
            
            # Construir prompt
            prompt = self.build_analysis_prompt(data_summary, query, analysis_type)
            
            # Llamar a la API de Groq
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un consultor senior en análisis de datos retail con 15+ años de experiencia en transformación digital y optimización operativa. Tus análisis son directos, basados en datos, y enfocados en ROI."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model=self.model,
                temperature=0.7,  # Balance entre creatividad y consistencia
                max_tokens=2000,  # Aumentado para respuestas más completas
                top_p=0.9
            )
            
            # Extraer respuesta
            response = chat_completion.choices[0].message.content
            
            return {
                'success': True,
                'content': response,
                'error': None
            }
        
        except Exception as e:
            error_msg = str(e)
            
            # Mensajes de error más específicos
            if "api_key" in error_msg.lower():
                detailed_error = """
❌ **Error de Autenticación**

La API Key de Groq no es válida o no está configurada correctamente.

**Soluciones:**
1. Verifica que el archivo `.env` existe en la carpeta del proyecto
2. Asegúrate de que contiene: `GROQ_API_KEY=tu_api_key_aqui`
3. Obtén una API Key gratuita en: https://console.groq.com
4. O ingresa la API Key manualmente en el campo de texto del dashboard
"""
            elif "rate" in error_msg.lower() or "quota" in error_msg.lower():
                detailed_error = """
❌ **Límite de Uso Excedido**

Has superado el límite de solicitudes de la API de Groq.

**Soluciones:**
1. Espera unos minutos antes de intentar nuevamente
2. Revisa tu cuota en: https://console.groq.com
3. Considera actualizar tu plan si usas frecuentemente
"""
            elif "connection" in error_msg.lower() or "timeout" in error_msg.lower():
                detailed_error = """
❌ **Error de Conexión**

No se pudo conectar con los servidores de Groq.

**Soluciones:**
1. Verifica tu conexión a internet
2. Intenta nuevamente en unos segundos
3. Si el problema persiste, revisa el estado de Groq en su página de status
"""
            else:
                detailed_error = f"""
❌ **Error al Generar Análisis**

{error_msg}

**Posibles causas:**
- API Key inválida o expirada
- Límite de rate excedido
- Problema de conexión
- Error en los datos de entrada

**Soluciones:**
1. Verifica que GROQ_API_KEY esté correctamente configurada
2. Revisa tu cuota en https://console.groq.com
3. Intenta nuevamente en unos segundos
"""
            
            return {
                'success': False,
                'content': '',
                'error': detailed_error
            }
    
    # ================================
    # ANÁLISIS ESPECIALIZADOS
    # ================================
    
    def analyze_rentabilidad(self, df):
        """Análisis enfocado en rentabilidad y márgenes"""
        query = """Analiza en profundidad la rentabilidad del negocio:
        - Identifica SKUs o categorías con márgenes problemáticos
        - Evalúa la estructura de costos
        - Recomienda ajustes de precios o eliminación de productos
        - Cuantifica el impacto financiero de las recomendaciones"""
        
        return self.analyze(df, query, "Análisis de Rentabilidad")
    
    def analyze_satisfaccion(self, df):
        """Análisis enfocado en satisfacción del cliente"""
        query = """Analiza la satisfacción del cliente (NPS) en detalle:
        - Identifica los principales detractores y sus causas
        - Relaciona NPS con otras variables (entrega, categoría, canal)
        - Recomienda acciones específicas para mejorar la lealtad
        - Proyecta el impacto de mejorar el NPS en retención e ingresos"""
        
        return self.analyze(df, query, "Análisis de Satisfacción del Cliente")
    
    def analyze_logistica(self, df):
        """Análisis enfocado en operaciones logísticas"""
        query = """Analiza el desempeño logístico:
        - Identifica bodegas o rutas con problemas de entrega
        - Evalúa la correlación entre tiempos de entrega y satisfacción
        - Recomienda cambios en operadores o procesos
        - Estima el ROI de las mejoras logísticas"""
        
        return self.analyze(df, query, "Análisis de Operaciones Logísticas")
    
    def analyze_inventario(self, df):
        """Análisis enfocado en gestión de inventario"""
        query = """Analiza la gestión de inventario:
        - Identifica productos con stock excesivo o inventario obsoleto
        - Evalúa la antigüedad de revisiones de inventario
        - Detecta SKUs fantasma o no catalogados
        - Recomienda estrategias de optimización de stock"""
        
        return self.analyze(df, query, "Análisis de Gestión de Inventario")
    
    def analyze_general(self, df):
        """Análisis general del negocio"""
        query = """Realiza un análisis integral del negocio:
        - Resume los principales desafíos identificados en los datos
        - Prioriza problemas por urgencia e impacto
        - Proporciona una hoja de ruta ejecutiva
        - Identifica las oportunidades de mayor valor"""
        
        return self.analyze(df, query, "Resumen Ejecutivo")
    
    # ================================
    # COMPARACIÓN DE ESCENARIOS
    # ================================
    
    def compare_scenarios(self, df_before, df_after, scenario_description):
        """
        Compara dos escenarios (ej: antes/después de filtros)
        
        Parameters:
        -----------
        df_before : pd.DataFrame
            Dataset del primer escenario
        df_after : pd.DataFrame
            Dataset del segundo escenario
        scenario_description : str
            Descripción de la comparación
        
        Returns:
        --------
        dict : Resultado del análisis
        """
        summary_before = self.prepare_data_summary(df_before)
        summary_after = self.prepare_data_summary(df_after)
        
        prompt = f"""Compara estos dos escenarios y analiza el impacto de los cambios:

**ESCENARIO 1 (ANTES):**
{summary_before}

**ESCENARIO 2 (DESPUÉS):**
{scenario_description}

{summary_after}

**Proporciona:**
1. **Principales Diferencias Cuantificadas:** Cambios en KPIs clave
2. **Impacto en el Negocio:** ¿Qué significan estos cambios?
3. **Recomendaciones Específicas:** Acciones basadas en esta comparación

Sé específico con los números y el impacto financiero.
"""
        
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.model,
                temperature=0.7,
                max_tokens=1500
            )
            
            return {
                'success': True,
                'content': chat_completion.choices[0].message.content,
                'error': None
            }
        
        except Exception as e:
            return {
                'success': False,
                'content': '',
                'error': f"Error en comparación: {str(e)}"
            }

# ================================
# FUNCIONES DE UTILIDAD
# ================================

def test_groq_connection(api_key=None):
    """
    Prueba la conexión con Groq
    
    Parameters:
    -----------
    api_key : str, optional
        API key a probar
    
    Returns:
    --------
    dict : Resultado de la prueba con 'success' (bool) y 'message' (str)
    """
    try:
        analyzer = AIAnalyzer(api_key=api_key)
        
        # Crear un DataFrame de prueba
        test_df = pd.DataFrame({
            'Precio_Venta': [100, 200, 150],
            'NPS': [8, 6, 9],
            'Margen_Utilidad': [20, -5, 15]
        })
        
        # Intentar un análisis simple
        result = analyzer.analyze(
            test_df,
            "Resume estos datos de prueba en una oración",
            "test"
        )
        
        if result['success']:
            return {
                'success': True,
                'message': '✅ Conexión con Groq exitosa. API Key válida y funcionando.'
            }
        else:
            return {
                'success': False,
                'message': f"❌ Error en la respuesta de Groq: {result['error']}"
            }
    
    except Exception as e:
        return {
            'success': False,
            'message': f"❌ Error al conectar con Groq: {str(e)}"
        }

# ================================
# EJEMPLO DE USO
# ================================

if __name__ == "__main__":
    print("🤖 Probando integración con Groq...\n")
    
    # Probar conexión
    test_result = test_groq_connection()
    print(test_result['message'])
    
    if test_result['success']:
        print("\n" + "="*80)
        print("EJEMPLO DE ANÁLISIS")
        print("="*80 + "\n")
        
        # Crear un dataset de ejemplo
        example_df = pd.DataFrame({
            'SKU': ['SKU001', 'SKU002', 'SKU003'] * 100,
            'Precio_Venta': [100, 250, 180] * 100,
            'Costo_Unitario': [80, 300, 140] * 100,
            'NPS': [8, 4, 9] * 100,
            'Canal': ['Online', 'Tienda', 'Online'] * 100,
            'Categoria': ['Laptops', 'Tablets', 'Laptops'] * 100,
            'Brecha_Entrega': [2, 15, 1] * 100
        })
        
        # Calcular margen
        example_df['Margen_Utilidad'] = (
            (example_df['Precio_Venta'] - example_df['Costo_Unitario']) / 
            example_df['Precio_Venta'] * 100
        )
        
        # Crear analizador
        analyzer = AIAnalyzer()
        
        # Ejecutar análisis
        print("Generando análisis de rentabilidad...\n")
        result = analyzer.analyze_rentabilidad(example_df)
        
        if result['success']:
            print(result['content'])
        else:
            print(result['error'])
    
    else:
        print("\n⚠️ No se pudo establecer conexión con Groq")
        print("Verifica tu API Key en el archivo .env o proporciona una manualmente")