import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# Configurações da página
st.set_page_config(layout="wide")
st.title("☀️ Mapa Interativo - Irradiação Solar Anual")

st.write("""
Este aplicativo exibe um mapa interativo mostrando os níveis de irradiação solar anual 
com base em dados geográficos.  
Faça upload de um arquivo CSV contendo as colunas **LON**, **LAT** e **ANNUAL**.
""")

# Upload do CSV
uploaded_file = st.file_uploader("📂 Faça upload do arquivo CSV de irradiação solar", type=["csv"])

if uploaded_file is not None:
    try:
        # Leitura do CSV (suporta delimitadores comuns)
        df = pd.read_csv(uploaded_file, sep=None, engine='python')

        st.subheader("📋 Pré-visualização dos Dados")
        st.dataframe(df.head())

        # Verificação das colunas esperadas
        if all(col in df.columns for col in ['LON', 'LAT', 'ANNUAL']):
            
            # Cria o mapa centralizado na média das coordenadas
            m = folium.Map(location=[df['LAT'].mean(), df['LON'].mean()], zoom_start=5)

            # Função para definir cor conforme o valor de ANNUAL
            def cor_irradiacao(valor):
                if valor < 4400:
                    return 'blue'
                elif 4400 <= valor < 4550:
                    return 'green'
                elif 4550 <= valor < 4650:
                    return 'orange'
                else:
                    return 'red'

            # Adiciona os pontos ao mapa
            for _, row in df.iterrows():
                folium.CircleMarker(
                    location=[row['LAT'], row['LON']],
                    radius=6,
                    color=cor_irradiacao(row['ANNUAL']),
                    fill=True,
                    fill_opacity=0.7,
                    popup=f"Irradiação: {row['ANNUAL']} kWh/m²/ano"
                ).add_to(m)

            # Adiciona legenda
            legend_html = '''
            <div style="
                position: fixed; 
                bottom: 50px; left: 50px; width: 200px; height: 140px; 
                background-color: white; border:2px solid grey; z-index:9999; font-size:14px;
                padding: 10px; border-radius: 8px;
            ">
            <b>Legenda - Irradiação (kWh/m²/ano)</b><br>
            <i style="background:blue;color:blue;">⬤</i> < 4400<br>
            <i style="background:green;color:green;">⬤</i> 4400–4549<br>
            <i style="background:orange;color:orange;">⬤</i> 4550–4649<br>
            <i style="background:red;color:red;">⬤</i> ≥ 4650<br>
            </div>
            '''
            m.get_root().html.add_child(folium.Element(legend_html))

            # Exibe o mapa no Streamlit
            st.subheader("🗺️ Mapa de Irradiação Solar Anual")
            st_folium(m, width=1000, height=600)

        else:
            st.error("❌ O CSV deve conter as colunas: LON, LAT e ANNUAL.")
    except Exception as e:
        st.error(f"Erro ao ler o arquivo CSV: {e}")
else:
    st.info("Por favor, faça o upload de um arquivo CSV contendo as colunas: LON, LAT e ANNUAL.")
