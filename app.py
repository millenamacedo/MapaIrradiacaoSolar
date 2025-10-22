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

            # --- Correção de coordenadas ---
            def corrigir_coordenada(valor):
                """Corrige coordenadas que estão com ponto decimal fora do lugar"""
                if abs(valor) > 180:  # longitude válida é até ±180
                    valor = valor / 10
                    if abs(valor) > 180:
                        valor = valor / 10
                return valor

            df["LON"] = df["LON"].apply(corrigir_coordenada)
            df["LAT"] = df["LAT"].apply(corrigir_coordenada)

            # --- Cria o mapa ---
            m = folium.Map(location=[df["LAT"].mean(), df["LON"].mean()], zoom_start=5)

            # --- Função para definir cores com mais gradientes ---
            def cor_irradiacao(valor):
                if valor < 3800:
                    return "#313695"  # azul escuro
                elif 3800 <= valor < 4100:
                    return "#4575b4"  # azul
                elif 4100 <= valor < 4400:
                    return "#74add1"  # azul claro
                elif 4400 <= valor < 4700:
                    return "#fee090"  # amarelo claro
                elif 4700 <= valor < 5000:
                    return "#fdae61"  # laranja claro
                elif 5000 <= valor < 5400:
                    return "#f46d43"  # laranja
                else:  # >= 5400
                    return "#d73027"  # vermelho

            # --- Adiciona marcadores ---
            for _, row in df.iterrows():
                folium.CircleMarker(
                    location=[row["LAT"], row["LON"]],
                    radius=6,
                    color=cor_irradiacao(row["ANNUAL"]),
                    fill=True,
                    fill_opacity=0.7,
                    popup=f"Irradiação: {row['ANNUAL']} kWh/m²/ano"
                ).add_to(m)

            # --- Legenda ---
            legend_html = '''
            <div style="
                position: fixed; 
                bottom: 50px; left: 50px; width: 220px; height: 240px; 
                background-color: white; border:2px solid grey; z-index:9999; font-size:14px;
                padding: 10px; border-radius: 8px;
            ">
            <b>Legenda - Irradiação (kWh/m²/ano)</b><br>
            <i style="color:#313695;">⬤</i> < 3800<br>
            <i style="color:#4575b4;">⬤</i> 3800–4099<br>
            <i style="color:#74add1;">⬤</i> 4100–4399<br>
            <i style="color:#fee090;">⬤</i> 4400–4699<br>
            <i style="color:#fdae61;">⬤</i> 4700–4999<br>
            <i style="color:#f46d43;">⬤</i> 5000–5399<br>
            <i style="color:#d73027;">⬤</i> ≥ 5400<br>
            </div>
            '''
            m.get_root().html.add_child(folium.Element(legend_html))

            # --- Exibe o mapa ---
            st.subheader("🗺️ Mapa de Irradiação Solar (corrigido)")
            st_folium(m, width=1000, height=600)

            st.success("✅ Coordenadas corrigidas automaticamente!")

        else:
            st.error("❌ O CSV deve conter as colunas: LON, LAT e ANNUAL.")
    except Exception as e:
        st.error(f"Erro ao ler o arquivo CSV: {e}")
else:
    st.info("Por favor, faça o upload de um arquivo CSV contendo as colunas: LON, LAT e ANNUAL.")
