import pandas as pd

file_path = r'C:\\Users\\mary.rojas\\Documents\\rentabilidad mary\\pyg.csv'

def limpiar_moneda(valor):
    if isinstance(valor, str):
        valor = valor.replace('$', '').replace(' ', '').replace(',', '').strip()
        try: return float(valor)
        except: return 0.0
    return valor

def cargar_y_preparar_datos():
    try:
        df = pd.read_csv(file_path, engine='python', encoding='utf-8-sig')
        df.columns = df.columns.str.strip().str.lower().str.replace('\n', '', regex=True)
        
        # Limpieza de columnas de dinero
        cols_clave = ['ebitda (cartera)', 'precio', 'uds', '1era milla', 'log um veh']
        for col in cols_clave:
            if col in df.columns:
                df[col] = df[col].apply(limpiar_moneda)
        
        # Limpieza profunda de texto
        if 'canal' in df.columns:
            df['canal'] = df['canal'].astype(str).str.strip().str.upper()
        if 'tipo huevo' in df.columns:
            df['tipo huevo'] = df['tipo huevo'].astype(str).str.strip().str.lower()
        if 'ciudad' in df.columns:
            df['ciudad'] = df['ciudad'].astype(str).str.strip()

        df['costo_logistico_total'] = df['1era milla'] + df['log um veh']
        return df
    except Exception as e:
        print(f"❌ Error al cargar archivo: {e}")
        return None

def opcion_1_analisis_canales(df):
    print("\n" + "="*50)
    # Mostramos qué opciones existen para que el usuario no adivine
    huevos_disponibles = df['tipo huevo'].unique()
    print(f"Tipos de huevo detectados en el archivo: {', '.join(huevos_disponibles).upper()}")
    
    tipo_huevo_input = input("👉 Ingrese el TIPO DE HUEVO a consultar: ").strip().lower()
    
    df_h = df[df['tipo huevo'].str.contains(tipo_huevo_input, na=False)]
    
    if df_h.empty:
        print(f"❌ No se encontraron datos para '{tipo_huevo_input}'.")
        return

    # Definimos los canales que te interesan
    canales_interes = ['AU ESP', 'TAT', 'MY', 'FS', 'GS', 'HD']
    
    # Filtramos por tus canales y sacamos el Top 5 por Ebitda
    df_interes = df_h[df_h['canal'].isin(canales_interes)]
    
    if df_interes.empty:
        print("⚠️ El huevo seleccionado no tiene ventas en los canales AU ESP, TAT, MY, FS, GS o HD.")
        return

    top_5_canales = df_interes.groupby('canal')['ebitda (cartera)'].mean().sort_values(ascending=False).head(5)

    print(f"\n--- ANÁLISIS DE RENTABILIDAD PARA HUEVO: {tipo_huevo_input.upper()} ---")
    
    for canal in top_5_canales.index:
        rent_c = top_5_canales[canal]
        print(f"\n📢 CANAL: {canal} | Ebitda Promedio: ${rent_c:,.2f}")
        
        # Top 3 ciudades por ese canal
        df_c = df_interes[df_interes['canal'] == canal]
        top_ciudades = df_c.groupby('ciudad')['ebitda (cartera)'].mean().sort_values(ascending=False).head(3)
        
        for i, (ciudad, rent_v) in enumerate(top_ciudades.items(), 1):
            print(f"      {i}. {ciudad.title()} (${rent_v:,.2f})")

def opcion_2_simulador_precio(df):
    print("\n" + "="*50)
    tipo_huevo_input = input("👉 Ingrese el TIPO DE HUEVO que va a vender: ").strip().lower()
    try:
        cantidad = float(input("👉 Ingrese la CANTIDAD de huevos: "))
    except:
        print("❌ Cantidad inválida."); return

    df_h = df[df['tipo huevo'].str.contains(tipo_huevo_input, na=False)]
    if df_h.empty:
        print(f"❌ No hay registros para '{tipo_huevo_input}'.")
        return

    # Agrupamos por canal y ciudad (solo tus canales)
    canales_interes = ['AU ESP', 'TAT', 'MY', 'FS', 'GS', 'HD']
    df_interes = df_h[df_h['canal'].isin(canales_interes)]
    
    sugerencias = df_interes.groupby(['canal', 'ciudad'])[['precio', 'costo_logistico_total']].mean().reset_index()
    log_avg = df_h['costo_logistico_total'].mean()

    print(f"\n--- PRECIO MÍNIMO SUGERIDO PARA {cantidad:,.0f} UDS ---")
    for _, fila in sugerencias.iterrows():
        p_min = fila['precio']
        total = p_min * cantidad
        alerta = "⚠️ (Logística Alta)" if fila['costo_logistico_total'] > log_avg * 1.1 else ""
        
        print(f"[{fila['canal']}] {fila['ciudad'].title()}:")
        print(f"   Venta Sugerida: ${total:,.2f} (Precio unitario: ${p_min:,.2f}) {alerta}")

def menu_principal():
    df = cargar_y_preparar_datos()
    if df is not None:
        while True:
            print("\n========================================")
            print("     CONTROL DE RENTABILIDAD MARY")
            print("========================================")
            print("1. Análisis Top 5 Canales y 3 Ciudades")
            print("2. Simulador de Precio Mínimo")
            print("3. Salir")
            opcion = input("\nSeleccione (1-3): ")
            if opcion == '1': opcion_1_analisis_canales(df)
            elif opcion == '2': opcion_2_simulador_precio(df)
            elif opcion == '3': break

if __name__ == "__main__":
    menu_principal()