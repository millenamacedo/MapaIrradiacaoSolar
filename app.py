import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
# Importado para injetar HTML customizado (legenda) no mapa Folium
# Removido o import 'Element' de branca.element pois não será mais usado
# from branca.element import Element

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
        # Tenta ler o CSV, detectando o separador automaticamente
        df = pd.read_csv(uploaded_file, sep=None, engine="python")

        st.subheader("📋 Pré-visualização dos Dados")
        st.dataframe(df.head())

        if all(col in df.columns for col in ["LON", "LAT", "ANNUAL"]):

            # --- Correção de coordenadas ---
            def corrigir_coordenada(valor):
                """Normaliza as coordenadas (latitude ou longitude) se estiverem fora do intervalo [-180, 180]."""
                try:
                    valor = float(valor)
                except Exception:
                    # Retorna o valor original se não for um número (Folium irá ignorar)
                    return valor 
                if abs(valor) > 180:
                    valor = valor / 10
                    if abs(valor) > 180:
                        valor = valor / 10
                return valor

            df["LON"] = df["LON"].apply(corrigir_coordenada)
            df["LAT"] = df["LAT"].apply(corrigir_coordenada)

            # --- Cria o mapa (cálculo do centroide para iniciar o zoom) ---
            m = folium.Map(location=[df["LAT"].mean(), df["LON"].mean()], zoom_start=5)

            # --- Mapeamento discreto de cores por faixa ---
            def cor_por_faixa(valor):
                """Define a cor do marcador com base no valor de irradiação anual (ANNUAL)."""
                try:
                    v = float(valor)
                except Exception:
                    return "#808080"  # cinza para valores inválidos
                if v < 4000:
                    return "#313695"    # azul escuro (< 4000)
                elif v < 4200:
                    return "#74add1"    # azul claro / transição (4000 - 4199)
                elif v < 4400:
                    return "#fee090"    # amarelo claro (4200 - 4399)
                elif v < 4600:
                    return "#fdae61"    # laranja (4400 - 4599)
                else:
                    return "#d73027"    # vermelho (>= 4600)

            # --- Adiciona marcadores ao mapa ---
            for _, row in df.iterrows():
                color = cor_por_faixa(row["ANNUAL"])
                folium.CircleMarker(
                    location=[row["LAT"], row["LON"]],
                    radius=6,
                    color=color,
                    fill=True,
                    fill_color=color,
                    fill_opacity=0.8,
                    popup=f"Irradiação: {row['ANNUAL']} kWh/m²/ano"
                ).add_to(m)

            # --- Adiciona a Legenda como Tabela (Acima do mapa) ---
            legend_data = {
                "Faixa de Irradiação (kWh/m²/ano)": [
                    "< 4.000",
                    "4.000 – 4.199",
                    "4.200 – 4.399",
                    "4.400 – 4.599",
                    "≥ 4.600"
                ],
                "Cor": [
                    "Azul Escuro",
                    "Azul Claro",
                    "Amarelo Claro",
                    "Laranja",
                    "Vermelho"
                ]
            }
            legend_df = pd.DataFrame(legend_data)

            st.subheader("📊 Legenda de Cores")
            # Usa st.table para exibição clara da legenda
            st.table(legend_df) 


            # --- Exibe o mapa ---
            st.subheader("🗺️ Mapa de Irradiação Solar")
            st_folium(m, width=1000, height=600)


        else:
            st.error("❌ O CSV deve conter as colunas: LON, LAT e ANNUAL.")
    except Exception as e:
        st.error(f"Erro ao ler o arquivo CSV: {e}")
else:
    st.info("Por favor, faça o upload de um arquivo CSV contendo as colunas: LON, LAT e ANNUAL.")
