import pandas as pd
import streamlit as st
import io


def display_dataframe_info(df, title="Información del Archivo"):
    """Muestra información básica del dataframe."""
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total de Registros", len(df))
    with col2:
        st.metric("Columnas", len(df.columns))
    
    st.subheader("Vista de Datos")
    st.write(df)
    
    st.subheader("Estadísticas")
    try:
        if 'Precio_Venta_Final' in df.columns and 'Cantidad_Vendida' in df.columns:
            st.write(df[['Cantidad_Vendida','Precio_Venta_Final', 'Costo_Envio', 'Tiempo_Entrega_Real']].describe())
        elif 'SKU_ID' in df.columns and 'Costo_Unitario_USD' in df.columns:
            st.write(df[['SKU_ID','Costo_Unitario_USD', 'Punto_Reorden', 'Lead_Time_Dias']].describe())
        else:
                st.write(df.describe())
    except Exception as e:
        st.error(f"Error al calcular estadísticas: {e}")


def load_csv_file(file_bytes):
    """Carga un archivo CSV desde bytes y retorna el dataframe."""
    try:
        if file_bytes is None:
            return None
        # Convertir bytes a BytesIO para que pandas pueda leerlo
        file_obj = io.BytesIO(file_bytes)
        df = pd.read_csv(file_obj, na_filter=True)
        # Limpiar columnas sin nombre
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"❌ Error al cargar: {e}")
        return None


def show_file_preview(df, num_rows=5):
    """Muestra una vista previa del archivo."""
    return df.head(num_rows)
