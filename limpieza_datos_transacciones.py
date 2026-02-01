import pandas as pd
import numpy as np

def corregir_nombres_ciudad_destino(df):
    df['Ciudad_Destino'] = df['Ciudad_Destino'].replace({
        'BOG': 'Bogotá',
        'MED': 'Medellín'})
    return df   

def corregir_canal_venta(df):
    df['canal_venta'] = df['canal_venta'].replace({
        'WhatsApp': 'Online',
        '': 'Online',
    })