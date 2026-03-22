import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime

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
            background-color: #FFFFFF;
        }
        
        /* Personalización de Métricas (KPIs) */
        div[data-testid="stMetricValue"] {
            color: #1A1A1A;
            font-weight: 700;
            font-size: 2.2rem;
        }
        
        /* Sidebar Estilo Marriott */
        [data-testid="stSidebar"] {
            background-color: #1A1A1A;
            color: white;
        }
        
        /* Botones y acentos */
        .stButton>button {
            background-color: #000000;
            color: white;
            border-radius: 5px;
        }
    </style>
    """, unsafe_allow_html=True)

# 2. FUNCIÓN PARA OBTENER DATOS
def fetch_data():
    # Sustituye por tu URL real de Easypanel/n8n
    N8N_URL = st.secrets.get("N8N_WEBHOOK_URL", "https://tu-n8n.com/webhook/salesforce-data")
    try:
        response = requests.get(N8N_URL, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error de conexión con n8n: {e}")
        return []

# 3. LÓGICA DE DATOS
raw_data = fetch_data()

if not raw_data:
    st.warning("No se encontraron datos de reservas activos.")
else:
    df = pd.DataFrame(raw_data)
    
    # Sidebar: Logo e Info
    with st.sidebar:
        st.image("logo_blanco.png", use_container_width=True) # Asegúrate de subir el logo al VPS
        st.markdown("---")
        st.write("📍 **Ushuaia, Argentina**")
        st.write(f"🕒 Actualizado: {datetime.now().strftime('%H:%M:%S')}")
        if st.button("🔄 Refrescar Datos"):
            st.rerun()

    # TÍTULO PRINCIPAL
    st.title("City Centro by Marriott")
    st.subheader("Panel de Control de Reservas - Tiempo Real")
    st.markdown("---")

    # 4. FILA DE KPIs (Métricas clave)
    col1, col2, col3, col4 = st.columns(4)
    
    total_reservas = len(df)
    llegadas_hoy = len(df[df['Arrival_date__c'] == datetime.now().strftime('%Y-%m-%d')])
    casos_negativos = int(df['Negative_Cases__c'].sum()) if 'Negative_Cases__c' in df else 0
    adultos = int(df['Total_Guest_Count__c'].sum()) if 'Total_Guest_Count__c' in df else 0

    col1.metric("Reservas Activas", total_reservas)
    col2.metric("Llegadas Hoy", llegadas_hoy)
    col3.metric("Total Huéspedes", adultos)
    col4.metric("Casos a Revisar", casos_negativos, delta="- Alerta", delta_color="inverse" if casos_negativos > 0 else "normal")

    st.markdown("---")

    # 5. GRÁFICOS
    c1, c2 = st.columns([1, 1])

    with c1:
        st.write("### Ocupación por Room Pool (MARSHA)")
        if 'Room_Pool_Booked__c' in df:
            fig_pie = px.pie(
                df, names='Room_Pool_Booked__c', 
                color_discrete_sequence=['#000000', '#555555', '#999999', '#CCCCCC'],
                hole=0.5
            )
            fig_pie.update_layout(showlegend=True, font_family="Montserrat")
            st.plotly_chart(fig_pie, use_container_width=True)

    with c2:
        st.write("### Nivel de Elite (Lealtad)")
        if 'Elite_Status__c' in df:
            elite_counts = df['Elite_Status__c'].value_counts().reset_index()
            fig_bar = px.bar(
                elite_counts, x='index', y='Elite_Status__c',
                labels={'index': 'Nivel', 'Elite_Status__c': 'Cantidad'},
                color_discrete_sequence=['#1A1A1A']
            )
            fig_bar.update_layout(font_family="Montserrat")
            st.plotly_chart(fig_bar, use_container_width=True)

    # 6. TABLA DETALLADA (Interactiva)
    st.write("### Listado de Huéspedes")
    # Limpiamos las columnas para mostrar solo lo relevante
    cols_to_show = ['Name', 'Concatenated_Guest__c', 'Arrival_date__c', 'Elite_Status__c', 'Room_Pool_Booked__c', 'Marsha_ConfNo__c']
    st.dataframe(df[cols_to_show], use_container_width=True)