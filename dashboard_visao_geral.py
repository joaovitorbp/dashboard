import streamlit as st
import pandas as pd
import textwrap

# ---------------------------------------------------------
# 1. CONFIGURAÇÃO VISUAL (CSS - TILES MODERNOS)
# ---------------------------------------------------------
st.markdown("""
<style>
    .stApp {background-color: #0e1117;}
    .block-container {padding-top: 2rem;}

    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 0px !important;
        transition: transform 0.2s;
    }
    [data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color: #58a6ff;
        transform: translateY(-2px);
    }

    .tile-header {
        padding: 15px 15px 10px 15px;
    }
    .tile-title {
        color: white;
        font-family: "Source Sans Pro", sans-serif;
        font-weight: 700;
        font-size: 1rem;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        margin-bottom: 2px;
    }
    .tile-sub {
        color: #8b949e;
        font-size: 0.75rem;
        font-family: "Source Sans Pro", sans-serif;
    }

    .data-strip {
        background-color: #0d1117;
        border-top: 1px solid #21262d;
        border-bottom: 1px solid #21262d;
        padding: 10px 15px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .data-col {
        display: flex;
        flex-direction: column;
        align-items: center;
        width: 25%;
    }
    .data-col:not(:last-child) {
        border-right: 1px solid #30363d;
    }
    .data-lbl {
        font-size: 0.6rem;
        color: #8b949e;
        text-transform: uppercase;
        margin-bottom: 2px;
    }
    .data-val {
        font-size: 0.85rem;
        font-weight: 700;
        color: #e6edf3;
        font-family: "Source Sans Pro", sans-serif;
    }

    .tile-footer {
        padding: 10px 15px;
    }
    .progress-track {
        background-color: #21262d;
        height: 4px;
        border-radius: 2px;
        width: 100%;
        margin-bottom: 10px;
        overflow: hidden;
    }
    .progress-fill {
        height: 100%;
        border-radius: 2px;
    }

    .footer-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        height: 20px;
    }

    .badge-status {
        font-size: 0.65rem;
        font-weight: 700;
        text-transform: uppercase;
        padding: 2px 8px;
        border-radius: 4px;
        letter-spacing: 0.5px;
        line-height: 1.2;
    }

    .footer-pct {
        font-size: 0.8rem;
        font-weight: 700;
        font-family: "Source Sans Pro", sans-serif;
        line-height: 1;
        display: flex;
        align-items: center;
    }

    /* --- BOTÃO (ESCALA REAL 80%) --- */
    div[data-testid="stVerticalBlockBorderWrapper"] button {
        background-color: transparent;
        border: 1px solid transparent;
        color: #58a6ff;
        padding: 0;
        margin: 0;
    }

    /* 🔥 AQUI É O SEGREDO */
    div[data-testid="stVerticalBlockBorderWrapper"] button > div {
        transform: scale(0.8);
        transform-origin: right center;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] button:hover {
        background-color: #1f242c;
        border-color: #30363d;
    }

    div[data-testid="column"] { padding: 0 8px; }

    .big-kpi {
        background-color: #161b22;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #30363d;
        text-align: center;
    }
    .big-kpi-val {
        font-size: 1.8rem;
        font-weight: bold;
        color: white;
    }
    .big-kpi-lbl {
        font-size: 0.9rem;
        color: #8b949e;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. DADOS
# ---------------------------------------------------------
@st.cache_data
def load_data():
    return pd.read_excel("dados_obras_v5.xlsx")

df = load_data()

# ---------------------------------------------------------
# 3. CÁLCULOS
# ---------------------------------------------------------
META_MARGEM = 20.0

def calcular_dados_extras(row):
    custo = row['Mat_Real'] + row['Desp_Real'] + row['HH_Real_Vlr'] + row['Impostos']
    lucro = row['Vendido'] - custo
    margem = (lucro / row['Vendido'] * 100) if row['Vendido'] > 0 else 0
    hh_perc = (row['HH_Real_Qtd'] / row['HH_Orc_Qtd'] * 100) if row['HH_Orc_Qtd'] > 0 else 0
    fisico = row['Conclusao_%']
    critico = margem < META_MARGEM or hh_perc > (fisico + 10)
    return pd.Series([margem, critico])

df[['Margem_%', 'E_Critico']] = df.apply(calcular_dados_extras, axis=1)

# ---------------------------------------------------------
# 4. INTERFACE
# ---------------------------------------------------------
st.title("🏢 Painel de Controle")

cols = st.columns(3)

for i, row in df.iterrows():
    with cols[i % 3]:
        with st.container(border=True):
            st.markdown(f"<b>{row['Projeto']}</b>", unsafe_allow_html=True)

            if st.button("Abrir ↗", key=f"btn_{row['Projeto']}"):
                st.session_state["projeto_foco"] = row['Projeto']
                st.switch_page("dashboard_detalhado.py")
