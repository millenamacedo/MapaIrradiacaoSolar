import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# Configurações iniciais da página
st.set_page_config(layout="wide")
st.title("☀️ Mapa Interativo - Irradiação Solar")

st.write("Este aplicativo exibe um mapa interativo com os níveis de irradiação solar em diferentes localidades do Brasil (ou do seu conjunto de dados).")

# Upload do arquivo CSV
uploaded_file = st.file_uploader("📂 Faça upload do arquivo CSV com dados de irradiação solar", type=["csv"])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)

        st.subheader("📋 Pré-visualização dos Dados")
        st.dataframe(df.head())

        # Verifica se as colunas esperadas existem
        if all(col in df.columns for col in ['latitude', 'longitude', 'irradiacao']):
            
            # Criação do mapa
            m = folium.Map(location=[df['latitude'].mean(), df['longitude'].mean()], zoom_start=5)

            # Função para definir cor conforme o nível de irradiação
            def cor_irradiacao(valor):
                if valor < 3:
                    return 'blue'
                elif 3 <= valor < 5:
                    return 'green'
                elif 5 <= valor < 6:
                    return 'orange'
                else:
                    return 'red'

            # Adiciona os marcadores
            for _, row in df.iterrows():
                folium.CircleMarker(
                    location=[row['latitude'], row['longitude']],
