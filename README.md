# TechLogistics S.A.S. - Sistema de Soporte a la Decisión (DSS)

[![Streamlit App](https://img.shields.io/badge/Streamlit-App_en_Vivo-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)](https://validacion-casos-prueba-fwkqfjw5ebcbunkerzgq8o.streamlit.app)

> 🌐 **Aplicación Web:** [https://validacion-casos-prueba-fwkqfjw5ebcbunkerzgq8o.streamlit.app](https://validacion-casos-prueba-fwkqfjw5ebcbunkerzgq8o.streamlit.app)

---

## 📋 Descripción del Proyecto

TechLogistics S.A.S. (Ficticio), un gigante del retail tecnológico, ha detectado una erosión en su margen de beneficios y una caída drástica en la lealtad de sus clientes. La junta directiva sospecha que la causa raíz es la invisibilidad operativa: sus tres sistemas principales (ERP de Inventarios, Logística y Feedback) no hablan el mismo idioma. Este proyecto fue desarrollado como consultoría senior para realizar una curaduría profunda y diseñar un Sistema de Soporte a la Decisión (DSS) en un Dashboard que transforme este caos en una estrategia de recuperación rentable.

---

## 🎯 Objetivos

- Auditoría de calidad de datos
- Integración de datasets heterogéneos
- Análisis de rentabilidad y operaciones
- Recomendaciones estratégicas con IA

---

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
├── streamlit_app.py            # Dashboard Streamlit
├── requirements.txt            # Dependencias
├── hallazgos.pdf              # Documento de hallazgos
└── README.md
```

---

## 🚀 Ruta para la Creación del Proyecto

### Requisitos Previos
- Python 3.9+
- pip
- Cuenta Groq API (para IA)

### Pasos de Instalación

#### 1. Clonar repositorio
```bash
git clone https://github.com/Jvelasquez980/validacion-casos-prueba.git
```

#### 2. Crear entorno virtual
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

#### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

#### 4. Configurar variables de entorno
```bash
# Crear archivo .env con:
GROQ_API_KEY=tu_api_key_aqui
```

#### 5. Ejecutar Dashboard
```bash
streamlit run app.py
```

---

## 📊 Datasets Utilizados

1. **inventario_central_v2.csv** - Stock teórico reportado por el sistema ERP al inicio del trimestre
2. **transacciones_logistica_v2.csv** - Flujo de salida de mercancía y ejecución de la promesa de entrega
3. **feedback_clientes_v2.csv** - Datos cualitativos y cuantitativos de la experiencia post-venta

---

## 🛠️ Desarrollo del Proyecto: Limpieza y Análisis de Datos

### Fase 1: Vista Inicial de los Datasets

Se empezó con una **vista inicial** de todos y cada uno de los datasets que se nos brindó. Se realizó una exploración exhaustiva para comprender la estructura, tipos de datos y calidad de la información disponible. Además, se logró obtener una **visión clara de todos y cada uno de los aspectos negativos** de los datasets, identificando problemas de calidad, inconsistencias y valores faltantes.

---

### Fase 2: Limpieza Individual de Datasets

Se continuó el desarrollo con la **limpieza individual** de los datasets. Se crearon **3 distintos archivos .ipynb** en los cuales se ve cómo se planteó la limpieza de todos y cada uno de los datasets de forma individual.

#### Paso 1: Estandarización de Datos

Primero se comenzó con la **estandarización de los datos**. Muchas de las columnas que se encontraban tenían **datos mezclados**, lo cual hacía imposible que se realicen análisis de forma correcta. Se unificaron formatos de fecha, se corrigieron tipos de datos inconsistentes y se normalizaron escalas de medición.

#### Paso 2: Manejo de Outliers

Se continuó la limpieza con el **manejo de los outliers**. En algunos casos, debido a que fueron casos concretos, se realizaron **limpiezas concretas** a los datos extraños. Sin embargo, en otros datos se manejaron los outliers a partir de los **cuantiles identificados**, estableciendo límites estadísticos para detectar y tratar valores atípicos.

#### Paso 3: Imputación de Datos Nulos

Se continuó con la limpieza a partir de la **imputación de los datos nulos**. Se revisaban las columnas específicas que contenían los datos nulos, y a partir de los tipos de datos se realizaron **distintas imputaciones**:

- Unas basadas únicamente en **medidas como la mediana**
- Otras que se fijaban en los **valores de las columnas adyacentes** para realizar las imputaciones

#### Paso 4: Corrección de Valores Inválidos

Por último, en temas de limpieza, se corrigieron los **valores que eran inválidos** (como negativos en precio de venta).

---

### Fase 3: Merge Unificado

Se creó el **merge unificado** que toma todos los valores de todos los datasets. Durante este proceso **se pierden 5,500 datos** que no contaban con las columnas suficientes para realizar el merge. Esta decisión se toma **en pro de conservar datos orgánicos** y mantener la integridad de la información.

---

## 🖥️ Desarrollo de la Aplicación

Después de la limpieza, se realizó la aplicación siguiendo la siguiente estructura:

### Estructura de la Aplicación

1. **Main (app.py)** - Archivo principal que inicia la aplicación

2. **Páginas modulares** - Se continuó dividiendo la app en páginas que muestran la información de los datasets

3. **Gráficas personalizadas** - Cada una de estas vistas posee sus propias gráficas

4. **Generador de informes** - Se implementa el generador de informes automatizado mediante Groq

---

## 🔧 Funcionalidades del Dashboard

- **Pestaña 1:** Auditoría de Calidad
- **Pestaña 2:** Análisis Exploratorio
- **Pestaña 3:** Análisis Estratégico
- **Pestaña 4:** Recomendaciones IA

---

## 📈 Métricas Clave Calculadas

- Health Score por dataset
- Margen de Utilidad
- Brecha de Entrega vs Prometido
- Ratio de Soporte por Categoría

---

## 👥 Autores

- Jerónimo Velásquez Escobar
- Manuela Caro Villada

---

## 📝 Licencia

Proyecto académico - Universidad EAFIT 2026-1