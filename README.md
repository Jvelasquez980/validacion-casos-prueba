# TechLogistics S.A.S. - Sistema de Soporte a la Decisión (DSS)

## 📋 Descripción del Proyecto
TechLogistics S.A.S.(Ficticio), un gigante del retail tecnológico, ha detectado una erosión en su margen de beneficios y una caída drástica en la lealtad de sus clientes. La junta directiva sospecha que la causa raíz es la invisibilidad operativa: sus tres sistemas principales (ERP de Inventarios, Logística y Feedback) no hablan el mismo idioma. Usted ha sido contratado como Consultor Senior para realizar una curaduría profunda y diseñar un Sistema de Soporte a la Decisión (DSS) en un Dashboard que transforme este caos en una estrategia de recuperación rentable.

## 🎯 Objetivos
- Auditoría de calidad de datos
- Integración de datasets heterogéneos
- Análisis de rentabilidad y operaciones
- Recomendaciones estratégicas con IA

## 📁 Estructura del Repositorio
```
├── datasets/
│   ├── feedback_clientes_v2.csv               
│   ├── inventario_central_v2.csv           
│   └── transacciones_logistica_v2.csv
├── src/
│   ├── data_cleaning.py        # Módulo de limpieza
│   ├── feature_engineering.py  # Creación de variables
│   ├── ai_integration.py       # Integración con Groq
│   └── utils.py                # Funciones auxiliares
├── streamlit_app.py                      # Dashboard Streamlit
├── requirements.txt            # Dependencias
├── hallazgos.pdf              # Documento de hallazgos
└── README.md
```

## 🚀 Instalación y Ejecución

### Requisitos Previos
- Python 3.9+
- pip
- Cuenta Groq API (para IA)

### Pasos de Instalación
```bash
# 1. Clonar repositorio
git clone https://github.com/Jvelasquez980/validacion-casos-prueba.git

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
# Crear archivo .env con:
GROQ_API_KEY=tu_api_key_aqui
```

### Ejecutar Dashboard
```bash
streamlit run app.py
```

## 📊 Datasets Utilizados
1. **inventario_central_v2.csv** - Este archivo representa el stock teórico reportado por el sistema ERP al inicio del trimestre
2. **transacciones_logistica_v2.csv** - Contiene el flujo de salida de mercancía y la ejecución de la promesa de entrega.
3. **feedback_clientes_v2.csv** - Datos cualitativos y cuantitativos de la experiencia post-venta.

## 🔧 Funcionalidades del Dashboard
- **Pestaña 1:** Auditoría de Calidad
- **Pestaña 2:** Análisis Exploratorio
- **Pestaña 3:** Análisis Estratégico
- **Pestaña 4:** Recomendaciones IA

## 📈 Métricas Clave Calculadas
- Health Score por dataset
- Margen de Utilidad
- Brecha de Entrega vs Prometido
- Ratio de Soporte por Categoría

## 👥 Autor
- Jerónimo Velásquez Escobar.
- Manuela Caro Villada. 

## 📝 Licencia
Proyecto académico - Universidad EAFIT 2026-1