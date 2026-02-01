import streamlit as st
import pandas as pd

# Configuración visual para celular
st.set_page_config(page_title="Rentabilidad Mary", layout="centered")

def limpiar_moneda(valor):
    if isinstance(valor, str):
        valor = valor.replace('$', '').replace(' ', '').replace(',', '').strip()
        try: return float(valor)
        except: return 0.0
    return valor

@st.cache_data
def cargar_datos():
    # El archivo debe tener este nombre exacto en GitHub
    file_name = 'pyg.csv' 
    try:
        df = pd.read_csv(file_name, engine='python', encoding='utf-8-sig')
        df.columns = df.columns.str.strip().str.lower().str.replace('\n', '', regex=True)
        
        # Limpieza de columnas clave
        cols_clave = ['ebitda (cartera)', 'precio', 'uds', '1era milla', 'log um veh']
        for col in cols_clave:
            if col in df.columns:
                df[col] = df[col].apply(limpiar_moneda)
        
        # Estandarizar textos
        df['canal'] = df['canal'].astype(str).str.strip().str.upper()
        df['tipo huevo'] = df['tipo huevo'].astype(str).str.strip().str.lower()
        df['ciudad'] = df['ciudad'].astype(str).str.strip()
        
        # Calcular costo logístico
        df['costo_logistico_total'] = df['1era milla'] + df['log um veh']
        return df
    except Exception as e:
        st.error(f"Error al cargar el archivo: {e}")
        return None

# --- INICIO DE LA APP ---
st.title("🥚 Rentabilidad Mary")
df = cargar_datos()

if df is not None:
    menu = st.sidebar.radio("MENÚ", ["Ranking de Rentabilidad", "Simulador de Precios"])

    # 1. OPCIÓN 1: RANKING
    if menu == "Ranking de Rentabilidad":
        st.header("🔝 Top 5 Canales y Ciudades")
        huevos_disp = sorted([h.upper() for h in df['tipo huevo'].unique()])
        tipo_huevo = st.selectbox("Seleccione el Tipo de Huevo:", huevos_disp)
        
        df_h = df[df['tipo huevo'] == tipo_huevo.lower()]
        canales_interes = ['AU ESP', 'TAT', 'MY', 'FS', 'GS', 'HD']
        df_interes = df_h[df_h['canal'].isin(canales_interes)]

        if not df_interes.empty:
            # Top 5 Canales
            top_5 = df_interes.groupby('canal')['ebitda (cartera)'].mean().sort_values(ascending=False).head(5)
            
            for canal in top_5.index:
                with st.expander(f"📢 CANAL: {canal} (Rent. Promedio: ${top_5[canal]:,.2f})"):
                    df_c = df_interes[df_interes['canal'] == canal]
                    ciudades = df_c.groupby('ciudad')['ebitda (cartera)'].mean().sort_values(ascending=False).head(3)
                    for i, (ciudad, rent) in enumerate(ciudades.items(), 1):
                        st.write(f"**{i}. {ciudad.title()}**: ${rent:,.2f}")
        else:
            st.warning("No hay datos para este tipo de huevo en los canales definidos.")

    # 2. OPCIÓN 2: SIMULADOR
    elif menu == "Simulador de Precios":
        st.header("💰 Precio Mínimo de Venta")
        col1, col2 = st.columns(2)
        with col1:
            huevos_disp = sorted([h.upper() for h in df['tipo huevo'].unique()])
            tipo = st.selectbox("Huevo a vender", huevos_disp)
        with col2:
            cantidad = st.number_input("Cantidad de huevos", min_value=1, value=1000)

        df_h = df[df['tipo huevo'] == tipo.lower()]
        canales_interes = ['AU ESP', 'TAT', 'MY', 'FS', 'GS', 'HD']
        df_interes = df_h[df_h['canal'].isin(canales_interes)]
        
        log_avg = df_h['costo_logistico_total'].mean()
        sugerencias = df_interes.groupby(['canal', 'ciudad'])[['precio', 'costo_logistico_total']].mean().reset_index()

        st.markdown("---")
        for _, fila in sugerencias.iterrows():
            total_v = fila['precio'] * cantidad
            costo_log = fila['costo_logistico_total']
            
            # Alerta de logística
            alerta = ""
            if costo_log > log_avg * 1.15:
                alerta = "⚠️ **Logística muy costosa en este punto**"
            
            st.subheader(f"📍 {fila['ciudad'].title()} ({fila['canal']})")
            st.write(f"Precio Mínimo Sugerido: **${fila['precio']:,.2f}**")
            st.write(f"Venta Total por {cantidad} uds: **${total_v:,.2f}**")
            if alerta: st.warning(alerta)
            st.markdown("---")
