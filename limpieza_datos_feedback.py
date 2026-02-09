import numpy as np
import pandas as pd

# Función para manejar outliers en Rating_Producto
def manejar_outliers_rating_producto(df, medida='Mediana'):
    """
    Detecta y reemplaza outliers en la columna Rating_Producto.
    
    Parámetros:
    -----------
    df : DataFrame
        Dataframe que contiene la columna Rating_Producto
    medida : str
        Medida para reemplazar outliers: 'Moda', 'Mediana' o 'Media'
        
    Retorna:
    --------
    DataFrame : Dataframe con outliers reemplazados
    """
    
    df_copy = df.copy()
    df_copy['Ticket_Soporte_Abierto'] = df_copy['Ticket_Soporte_Abierto'].replace({"1": "Sí", "0": "No"})
    columna = 'Rating_Producto'
    
    # Detectar outliers usando IQR
    Q1 = df_copy[columna].quantile(0.25)
    Q3 = df_copy[columna].quantile(0.75)
    IQR = Q3 - Q1
    
    limite_inferior = Q1 - 1.5 * IQR
    limite_superior = Q3 + 1.5 * IQR

    if limite_inferior < 1:
        limite_inferior = 0
    
    # Identificar outliers
    outliers_mask = (df_copy[columna] < limite_inferior) | (df_copy[columna] > limite_superior)
    num_outliers = outliers_mask.sum()
    
    # Seleccionar la medida de reemplazo
    if medida.lower() == 'moda':
        valor_reemplazo = df_copy[columna].mode()[0]
    elif medida.lower() == 'mediana':
        valor_reemplazo = df_copy[columna].median()
    elif medida.lower() == 'media':
        valor_reemplazo = df_copy[columna].mean()
    else:
        raise ValueError("La medida debe ser 'Moda', 'Mediana' o 'Media'")
    
    # Reemplazar outliers
    df_copy.loc[outliers_mask, columna] = valor_reemplazo
    
    print(f"Outliers detectados: {num_outliers}")
    print(f"Límite inferior: {limite_inferior:.2f}")
    print(f"Límite superior: {limite_superior:.2f}")
    print(f"Valor de reemplazo ({medida}): {valor_reemplazo:.2f}")
    print(f"Outliers reemplazados exitosamente")
    
    return df_copy

# Función para manejar outliers en Rating_Producto
def manejar_outliers_edad_cliente(df, medida='Mediana'):
    """
    Detecta y reemplaza outliers en la columna Edad_Cliente.
    
    Parámetros:
    -----------
    df : DataFrame
        Dataframe que contiene la columna Edad_Cliente
    medida : str
        Medida para reemplazar outliers: 'Moda', 'Mediana' o 'Media'
        
    Retorna:
    --------
    DataFrame : Dataframe con outliers reemplazados
    """
    
    df_copy = df.copy()
    columna = 'Edad_Cliente'
    
    # Detectar outliers usando IQR
    Q1 = df_copy[columna].quantile(0.25)
    Q3 = df_copy[columna].quantile(0.75)
    IQR = Q3 - Q1
    
    limite_inferior = Q1 - 1.5 * IQR
    limite_superior = Q3 + 1.5 * IQR

    if limite_inferior < 1:
        limite_inferior = 0
    
    # Identificar outliers
    outliers_mask = (df_copy[columna] < limite_inferior) | (df_copy[columna] > limite_superior)
    num_outliers = outliers_mask.sum()
    
    # Seleccionar la medida de reemplazo
    if medida.lower() == 'moda':
        valor_reemplazo = df_copy[columna].mode()[0]
    elif medida.lower() == 'mediana':
        valor_reemplazo = df_copy[columna].median()
    elif medida.lower() == 'media':
        valor_reemplazo = df_copy[columna].mean()
    else:
        raise ValueError("La medida debe ser 'Moda', 'Mediana' o 'Media'")
    
    # Reemplazar outliers
    df_copy.loc[outliers_mask, columna] = valor_reemplazo
    
    print(f"Outliers detectados: {num_outliers}")
    print(f"Límite inferior: {limite_inferior:.2f}")
    print(f"Límite superior: {limite_superior:.2f}")
    print(f"Valor de reemplazo ({medida}): {valor_reemplazo:.2f}")
    print(f"Outliers reemplazados exitosamente")
    
    return df_copy

def imputar_valores_comentario_texto(df):
    """
    Imputa valores faltantes en Comentario_Texto con un valor específico.
    """
    df.loc[df['Comentario_Texto'] == "---", 'Comentario_Texto'] = np.nan
    df['Comentario_Texto'].fillna(df['Comentario_Texto'].mode()[0], inplace=True)
    return df

def imputar_valores_recomienda_marca(df):
    """
    Imputa valores faltantes en Recomienda_Marca con la moda.
    """
    df['Recomienda_Marca'].fillna(df['Recomienda_Marca'].mode()[0], inplace=True)
    return df