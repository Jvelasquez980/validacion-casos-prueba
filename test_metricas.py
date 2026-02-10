#!/usr/bin/env python3
"""
Script de prueba para validar que las métricas se crean correctamente
"""
import pandas as pd
import numpy as np
from utils.data_integration import crear_metricas_nuevas

# Crear dataframe de prueba
print("🧪 Creando dataframe de prueba...")
df_test = pd.DataFrame({
    'Transaccion_ID': [1, 2, 3],
    'SKU_ID': ['A001', 'A002', 'A003'],
    'Rating_Producto': [4.5, 3.5, 5.0],
    'Rating_Logistica': [4.0, 3.0, 4.5],
    'Precio_Venta_Final': [100.0, 80.0, 150.0],
    'Costo_Unitario_USD': [40.0, 30.0, 50.0],
    'Cantidad_Vendida': [2, 3, 1],
    'Costo_Envio': [10.0, 15.0, 8.0]
})

print(f"Columnas iniciales: {list(df_test.columns)}")
print(f"Registros: {len(df_test)}\n")

# Crear métricas
print("📊 Creando métricas...")
df_result = crear_metricas_nuevas(df_test)

print(f"✅ Métricas creadas exitosamente!")
print(f"Columnas después: {list(df_result.columns)}\n")

# Verificar que existen las métricas esperadas
metricas_esperadas = ['Ganancia_Neta_Total', 'Margen_Real_Pct', 'Rating_Servicio', 'Margen_Unitario_Pct']
for metrica in metricas_esperadas:
    if metrica in df_result.columns:
        print(f"✅ {metrica} existe")
        print(f"   Valores: {df_result[metrica].values}")
    else:
        print(f"❌ {metrica} NO EXISTE")

print("\n📋 Resultado final:")
print(df_result.to_string())
