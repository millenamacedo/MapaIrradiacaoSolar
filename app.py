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
                try:
                    valor = float(valor)
                except Exception:
                    return valor
                if abs(valor) > 180:
                    valor = valor / 10
                    if abs(valor) > 180:
                        valor = valor / 10
                return valor

            df["LON"] = df["LON"].apply(corrigir_coordenada)
            df["LAT"] = df["LAT"].apply(corrigir_coordenada)

            # --- Cria o mapa ---
            m = folium.Map(location=[df["LAT"].mean(), df["LON"].mean()], zoom_start=5)

            # --- Mapeamento discreto de cores por faixa ---
            def cor_por_faixa(valor):
                try:
                    v = float(valor)
                except Exception:
                    return "#808080"  # cinza para valores inválidos
                if v < 4000:
                    return "#313695"   # azul escuro
                elif v < 4200:
                    return "#74add1"   # azul claro / transição
                elif v < 4400:
                    return "#fee090"   # amarelo claro
                elif v < 4600:
                    return "#fdae61"   # laranja
                else:
                    return "#d73027"   # vermelho (valores mais altos)

            # --- Adiciona marcadores ---
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

            # --- Exibe legenda como Streamlit ---
            st.subheader("📊 Legenda - Irradiação (kWh/m²/ano)")
            st.markdown("""
            <div style="font-size:14px; color:black;">
                <div style="display:flex; align-items:center; margin-bottom:4px;">
                    <div style="background:#313695; width:24px; height:18px; margin-right:8px;"></div>
                    <span>&lt; 4.000</span>
                </div>
                <div style="display:flex; align-items:center; margin-bottom:4px;">
                    <div style="background:#74add1; width:24px; height:18px; margin-right:8px;"></div>
                    <span>4.000 – 4.199</span>
                </div>
                <div style="display:flex; align-items:center; margin-bottom:4px;">
                    <div style="background:#fee090; width:24px; height:18px; margin-right:8px;"></div>
                    <span>4.200 – 4.399</span>
                </div>
                <div style="display:flex; align-items:center; margin-bottom:4px;">
                    <div style="background:#fdae61; width:24px; height:18px; margin-right:8px;"></div>
                    <span>4.400 – 4.599</span>
                </div>
                <div style="display:flex; align-items:center;">
                    <div style="background:#d73027; width:24px; height:18px; margin-right:8px;"></div>
                    <span>&ge; 4.600</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # --- Exibe o mapa ---
            st.subheader("🗺️ Mapa de Irradiação Solar (faixas discretas)")
            st_folium(m, width=1000, height=600)

            st.success("✅ Visualização atualizada com legenda preta via Streamlit.")

        else:
            st.error("❌ O CSV deve conter as colunas: LON, LAT e ANNUAL.")
    except Exception as e:
        st.error(f"Erro ao ler o arquivo CSV: {e}")
else:
    st.info("Por favor, faça o upload de um arquivo CSV contendo as colunas: LON, LAT e ANNUAL.")
