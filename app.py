import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

# 1. CONFIGURACIÓN DE PÁGINA Y MARCA
st.set_page_config(
    page_title="City Centro UI - Real Time Dashboard",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Aplicar Estilos del Manual de Marca (Fuentes Montserrat y Colores)
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@300;500;700&display=swap" rel="stylesheet">
    <style>
        /* Fuente Principal */
        html, body, [class*="css"], .stText, .stMarkdown {
            font-family: 'Montserrat', sans-serif !important;
        }
        
        /* Fondo y Contenedores */
        .stApp {
            background-color: #F8F9FA;
        }
        
        /* Personalización de Métricas (KPIs) */
        div[data-testid="stMetricValue"] {
            color: #1A1A1A;
            font-weight: 700;
            font-size: 2.2rem;
        }
        
        div[data-testid="metric-container"] {
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            border: 1px solid #EEEEEE;
        }
        
        /* Sidebar Estilo Marriott (Negro según manual) */
        [data-testid="stSidebar"] {
            background-color: #1A1A1A;
            color: white;
        }
        
        /* Botones */
        .stButton>button {
            background-color: #000000;
            color: white;
            border-radius: 4px;
            width: 100%;
            border: none;
            padding: 10px;
        }
    </style>
    """, unsafe_allow_html=True)

# 2. FUNCIÓN PARA OBTENER DATOS (Corregida para Easypanel)
def fetch_data():
    # Lee la variable de entorno configurada en Easypanel
    N8N_URL = os.getenv("N8N_WEBHOOK_URL", "https://tu-n8n.com/webhook/salesforce-data")
    
    try:
        response = requests.get(N8N_URL, timeout=20)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"⚠️ Error de conexión: No se pudo obtener datos de n8n. Verifica la URL: {N8N_URL}")
        st.info(f"Detalle técnico: {e}")
        return []

# 3. EJECUCIÓN Y PROCESAMIENTO
raw_data = fetch_data()

# Sidebar: Logo e Información fija
with st.sidebar:
    # Intentamos cargar el logo, si no existe mostramos texto
    if os.path.exists("logo_blanco.png"):
        st.image("logo_blanco.png", use_container_width=True)
    else:
        st.header("CITY CENTRO")
        st.caption("BY MARRIOTT")
    
    st.markdown("---")
    st.write("📍 **Ushuaia, Argentina**")
    st.write(f"🕒 **Sincronizado:** {datetime.now().strftime('%H:%M:%S')}")
    
    if st.button("🔄 Actualizar Ahora"):
        st.rerun()

if not raw_data:
    st.warning("Esperando datos de Salesforce... Asegúrate de que el flujo en n8n esté activo.")
else:
    df = pd.DataFrame(raw_data)
    
    # TÍTULO PRINCIPAL
    st.title("City Centro by Marriott")
    st.subheader("Dashboard de Operaciones en Tiempo Real")
    st.markdown("---")

    # 4. FILA DE KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    total_res = len(df)
    # Calculamos llegadas hoy (asumiendo formato YYYY-MM-DD en el JSON)
    hoy = datetime.now().strftime('%Y-%m-%d')
    llegadas_hoy = len(df[df['Arrival_date__c'] == hoy]) if 'Arrival_date__c' in df else 0
    
    # Manejo de nulos para seguridad
    neg_cases = int(df['Negative_Cases__c'].sum()) if 'Negative_Cases__c' in df else 0
    total_pax = int(df['Total_Guest_Count__c'].sum()) if 'Total_Guest_Count__c' in df else 0

    col1.metric("Reservas Totales", total_res)
    col2.metric("Llegadas (Hoy)", llegadas_hoy)
    col3.metric("Huéspedes en Casa", total_pax)
    
    # Alerta roja si hay casos negativos
    col4.metric("Casos Críticos", neg_cases, 
                delta="Atención Requerida" if neg_cases > 0 else "Todo OK", 
                delta_color="inverse" if neg_cases > 0 else "normal")

    st.markdown("---")

    # 5. GRÁFICOS INTERACTIVOS
    c1, c2 = st.columns([1, 1])

    with c1:
        st.write("### 🏠 Disponibilidad por Room Pool")
        if 'Room_Pool_Booked__c' in df:
            fig_pie = px.pie(
                df, names='Room_Pool_Booked__c', 
                color_discrete_sequence=['#1A1A1A', '#4A4A4A', '#8A8A8A', '#D1D1D1'],
                hole=0.5
            )
            fig_pie.update_layout(font_family="Montserrat", margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig_pie, use_container_width=True)

    with c2:
        st.write("### 🏆 Perfil de Lealtad (Elite Status)")
        if 'Elite_Status__c' in df:
            elite_counts = df['Elite_Status__c'].value_counts().reset_index()
            elite_counts.columns = ['Nivel', 'Cantidad']
            fig_bar = px.bar(
                elite_counts, x='Nivel', y='Cantidad',
                color_discrete_sequence=['#1A1A1A']
            )
            fig_bar.update_layout(font_family="Montserrat", plot_bgcolor='rgba(0,0,0,0)', yaxis_title=None, xaxis_title=None)
            st.plotly_chart(fig_bar, use_container_width=True)

    # 6. TABLA DE DETALLE (Buscable y filtrable)
    st.write("### 📋 Listado Detallado de Estancias")
    
    # Columnas que queremos mostrar (ajustadas a tu objeto Salesforce)
    cols_interes = ['Name', 'Concatenated_Guest__c', 'Arrival_date__c', 'Elite_Status__c', 'Room_Pool_Booked__c', 'Marsha_ConfNo__c']
    # Filtramos solo las columnas que realmente existan en el DF para evitar errores
    cols_finales = [c for c in cols_interes if c in df.columns]
    
    st.dataframe(df[cols_finales], use_container_width=True, hide_index=True)

# Pie de página
st.markdown("---")
st.caption("City Centro by Marriott Ushuaia - Sistema de Reporte Interno v1.0")