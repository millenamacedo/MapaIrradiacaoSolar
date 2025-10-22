import streamlit as st
import pandas as pd
import folium
from branca.colormap import LinearColormap
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

            # --- Correção de coordenadas ---
            def corrigir_coordenada(valor):
                if abs(valor) > 180:
                    valor = valor / 10
                    if abs(valor) > 180:
                        valor = valor / 10
                return valor

            df["LON"] = df["LON"].apply(corrigir_coordenada)
            df["LAT"] = df["LAT"].apply(corrigir_coordenada)

            # --- Cria o mapa ---
            m = folium.Map(location=[df["LAT"].mean(), df["LON"].mean()], zoom_start=5)

            # --- Gradiente contínuo com mais cores ---
            colormap = LinearColormap(
                colors=["#313695", "#4575b4", "#74add1", "#fee090", "#fdae61", "#f46d43", "#d73027"],
                vmin=df["ANNUAL"].min(),
                vmax=df["ANNUAL"].max()
            )

            # --- Adiciona marcadores com cores do gradiente ---
            for _, row in df.iterrows():
                folium.CircleMarker(
                    location=[row["LAT"], row["LON"]],
                    radius=6,
                    color=colormap(row["ANNUAL"]),
                    fill=True,
                    fill_color=colormap(row["ANNUAL"]),
                    fill_opacity=0.7,
                    popup=f"Irradiação: {row['ANNUAL']} kWh/m²/ano"
                ).add_to(m)

            # --- Legenda personalizada com texto preto ---
            min_val = df["ANNUAL"].min()
            max_val = df["ANNUAL"].max()
            mid_val = (min_val + max_val) / 2
            legend_html = f'''
            <div style="
                position: fixed; 
                bottom: 50px; left: 50px; width: 220px; height: 150px; 
                background-color: white; border:2px solid grey; z-index:9999; font-size:14px;
                padding: 10px; border-radius: 8px; color: black;
            ">
            <b>Legenda - Irradiação (kWh/m²/ano)</b><br>
            <div style="background:{colormap(min_val)};width:20px;height:20px;display:inline-block;"></div> {min_val:.0f}<br>
            <div style="background:{colormap(mid_val)};width:20px;height:20px;display:inline-block;"></div> Médio ({mid_val:.0f})<br>
            <div style="background:{colormap(max_val)};width:20px;height:20px;display:inline-block;"></div> {max_val:.0f}<br>
            </div>
            '''
            m.get_root().html.add_child(folium.Element(legend_html))

            # --- Exibe o mapa ---
            st.subheader("🗺️ Mapa de Irradiação Solar (gradiente ajustado e legenda legível)")
            st_folium(m, width=1000, height=600)

            st.success("✅ Coordenadas corrigidas automaticamente!")

        else:
            st.error("❌ O CSV deve conter as colunas: LON, LAT e ANNUAL.")
    except Exception as e:
        st.error(f"Erro ao ler o arquivo CSV: {e}")
else:
    st.info("Por favor, faça o upload de um arquivo CSV contendo as colunas: LON, LAT e ANNUAL.")
