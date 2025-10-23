import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

st.set_page_config(layout="wide")
st.title("☀️ Mapa Interativo - Irradiação Solar Anual")

st.write("""
Este aplicativo exibe um mapa com a **irradiação solar anual (kWh/m²/ano)** em diferentes localidades.
Você pode usar CSV com **vírgula decimal (padrão BR)** — o app converte automaticamente.
""")

uploaded_file = st.file_uploader("📤 Faça upload do arquivo CSV de irradiação solar", type=["csv"])

if uploaded_file is not None:
    try:
        # Tenta ler com separador ponto e vírgula
        df = pd.read_csv(uploaded_file, sep=';')

        # Substitui vírgula decimal por ponto (para garantir leitura correta)
        for col in df.columns:
            df[col] = df[col].astype(str).str.replace(',', '.').astype(str)

        # Converte colunas numéricas
        df['LON'] = pd.to_numeric(df['LON'], errors='coerce')
        df['LAT'] = pd.to_numeric(df['LAT'], errors='coerce')
        df['ANNUAL'] = pd.to_numeric(df['ANNUAL'], errors='coerce')

        st.subheader("📋 Pré-visualização dos Dados")
        st.dataframe(df.head())

        if all(col in df.columns for col in ['LON', 'LAT', 'ANNUAL']):
            m = folium.Map(location=[-14.235, -51.9253], zoom_start=4)

            for _, row in df.iterrows():
                valor = row['ANNUAL']
                if valor < 4400:
                    cor = 'blue'
                elif valor < 4550:
                    cor = 'green'
                elif valor < 4650:
                    cor = 'orange'
                else:
                    cor = 'red'

                folium.CircleMarker(
                    location=[row['LAT'], row['LON']],
                    radius=5,
                    color=cor,
                    fill=True,
                    fill_opacity=0.8,
                    popup=f"Irradiação: {valor} kWh/m²/ano"
                ).add_to(m)

            legenda = """
            <div style="position: fixed; 
                        bottom: 30px; left: 30px; width: 200px; height: 120px;
                        border:2px solid grey; z-index:9999; font-size:14px;
                        background-color: white; padding: 10px;">
            <b>Legenda - Irradiação (kWh/m²/ano)</b><br>
            <i style="color:blue;">●</i> < 4400<br>
            <i style="color:green;">●</i> 4400–4549<br>
            <i style="color:orange;">●</i> 4550–4649<br>
            <i style="color:red;">●</i> ≥ 4650
            </div>
            """
            m.get_root().html.add_child(folium.Element(legenda))

            st.subheader("🗺️ Mapa de Irradiação Solar")
            st_folium(m, width=1000, height=600)
        else:
            st.error("❌ O CSV deve conter as colunas: LON, LAT e ANNUAL.")
    except Exception as e:
        st.error(f"Ocorreu um erro ao ler o arquivo: {e}")
else:
    st.info("📎 Envie um arquivo CSV para visualizar o mapa.")
