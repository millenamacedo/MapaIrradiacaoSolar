import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Mapa de Irradiação Solar", layout="wide")
st.title("☀️ Mapa Interativo - Irradiação Solar Anual")

st.write("""
Este aplicativo exibe um mapa interativo com os níveis de irradiação solar anual, 
baseado em dados geográficos.  
Faça upload de um CSV com colunas: **LON**, **LAT**, **ANNUAL**.
""")

uploaded_file = st.file_uploader("📂 Faça upload do arquivo CSV", type=["csv"])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file, sep=None, engine="python")

        st.subheader("📋 Pré-visualização dos Dados")
        st.dataframe(df.head())

        if all(col in df.columns for col in ["LON", "LAT", "ANNUAL"]):

            # Corrige coordenadas automaticamente se estiverem fora do intervalo normal
            if df["LAT"].abs().max() > 90:
                df["LAT"] = df["LAT"] / 10 if df["LAT"].abs().max() < 900 else df["LAT"] / 100
            if df["LON"].abs().max() > 180:
                df["LON"] = df["LON"] / 10 if df["LON"].abs().max() < 1800 else df["LON"] / 100

            # Cria o mapa centralizado na média das coordenadas
            m = folium.Map(location=[df["LAT"].mean(), df["LON"].mean()], zoom_start=5)

            # Função de cor
            def cor_irradiacao(valor):
                if valor < 4400:
                    return "blue"
                elif 4400 <= valor < 4550:
                    return "green"
                elif 4550 <= valor < 4650:
                    return "orange"
                else:
                    return "red"

            for _, row in df.iterrows():
                folium.CircleMarker(
                    location=[row["LAT"], row["LON"]],
                    radius=6,
                    color=cor_irradiacao(row["ANNUAL"]),
                    fill=True,
                    fill_opacity=0.7,
                    popup=f"Irradiação: {row['ANNUAL']} kWh/m²/ano"
                ).add_to(m)

            legend_html = '''
            <div style="
                position: fixed; 
                bottom: 50px; left: 50px; width: 200px; height: 140px; 
                background-color: white; border:2px solid grey; z-index:9999; font-size:14px;
                padding: 10px; border-radius: 8px;
            ">
            <b>Legenda - Irradiação (kWh/m²/ano)</b><br>
            <i style="color:blue;">⬤</i> < 44
