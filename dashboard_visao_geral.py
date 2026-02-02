import streamlit as st
import pandas as pd
import json
import os

# ---------------------------------------------------------
# 1. CONFIGURAÇÃO VISUAL
# ---------------------------------------------------------
# REMOVEMOS O st.set_page_config PARA NÃO DAR CONFLITO COM O MAIN

st.markdown("""
<style>
    /* REMOVEMOS O .block-container DAQUI.
       Agora ele obedece a regra global do main.py (padding-top: 1rem),
       o que fará esta página colar no topo igual a Configurações.
    */

    /* --- LAYOUT DOS KPIS (CABEÇALHO) --- */
    .kpi-card {
        background-color: #161b22; 
        border: 1px solid #30363d; 
        border-radius: 10px; 
        padding: 20px 15px;
        height: 100%;
        display: flex; flex-direction: column; justify-content: space-between; align-items: center;
        text-align: center;
        min-height: 130px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .kpi-title { 
        color: #8b949e; font-size: 0.8rem; text-transform: uppercase; 
        letter-spacing: 1px; font-weight: 600; margin-bottom: 8px;
    }
    
    .kpi-val { 
        font-size: 1.8rem; font-weight: 800; color: white; 
        font-family: "Source Sans Pro", sans-serif; margin-bottom: 8px;
    }
    
    .kpi-sub { 
        font-size: 0.75rem; color: #8b949e; width: 100%;
        border-top: 1px solid #21262d;
        padding-top: 8px; margin-top: auto;
        display: flex; justify-content: space-around;
    }
    
    .txt-green { color: #3fb950; font-weight: bold; }
    .txt-red { color: #da3633; font-weight: bold; }
    .txt-blue { color: #58a6ff; font-weight: bold; }
    .txt-purple { color: #a371f7; font-weight: bold; }
    .txt-orange { color: #d29922; font-weight: bold; }

    /* --- CSS DOS CARDS DE PROJETO --- */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 0px !important; transition: transform 0.2s;
    }
    [data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color: #58a6ff; transform: translateY(-2px);
    }
    .tile-header { padding: 15px 15px 10px 15px; }
    .tile-title { color: white; font-weight: 700; font-size: 1rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-bottom: 2px; }
    .tile-sub { color: #8b949e; font-size: 0.75rem; }
    .data-strip { background-color: #0d1117; border-top: 1px solid #21262d; border-bottom: 1px solid #21262d; padding: 10px 15px; display: flex; justify-content: space-between; align-items: center; }
    .data-col { display: flex; flex-direction: column; align-items: center; width: 25%; }
    .data-col:not(:last-child) { border-right: 1px solid #30363d; }
    .data-lbl { font-size: 0.6rem; color: #8b949e; text-transform: uppercase; margin-bottom: 2px; }
    .data-val { font-size: 0.85rem; font-weight: 700; color: #e6edf3; }
    .tile-footer { padding: 10px 15px; }
    .progress-track { background-color: #21262d; height: 4px; border-radius: 2px; width: 100%; margin-bottom: 10px; overflow: hidden; }
    .badge-status { font-size: 0.65rem; font-weight: 700; text-transform: uppercase; padding: 2px 8px; border-radius: 4px; }
    .footer-pct { font-size: 0.8rem; font-weight: 700; }
    
    div[data-testid="stVerticalBlockBorderWrapper"] button {
        background-color: transparent; color: #58a6ff; border: 1px solid #30363d; border-radius: 4px;
        font-size: 0.65rem !important; padding: 0px 0px !important; height: 24px !important; min-height: 24px !important; line-height: 1 !important; margin: 0; width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. DADOS E TRATAMENTO
# ---------------------------------------------------------
@st.cache_data(ttl=0)
def load_data():
    return pd.read_excel("dados_obras_v5.xlsx")

try:
    df_raw = load_data()
except FileNotFoundError:
    st.error("⚠️ Base de dados 'dados_obras_v5.xlsx' não encontrada.")
    st.stop()

def clean_currency_brazil(x):
    if isinstance(x, (int, float)): return x
    try:
        s = str(x).replace('R$', '').replace('%', '').replace(' ', '')
        s = s.replace('.', '').replace(',', '.')
        return float(s)
    except: return 0.0

cols_monetarias = ['Vendido', 'Faturado', 'Mat_Real', 'Desp_Real', 'HH_Real_Vlr', 'Impostos', 'Mat_Orc']
for col in cols_monetarias:
    if col in df_raw.columns:
        df_raw[col] = df_raw[col].apply(clean_currency_brazil)
    else:
        df_raw[col] = 0.0

def formatar_valor_ptbr(valor):
    if valor >= 1_000_000: return f"R$ {valor/1_000_000:.1f}M".replace(".", ",")
    elif valor >= 1_000: return f"R$ {valor/1_000:.1f}k".replace(".", ",")
    else: return f"{valor:,.0f}".replace(",", ".")

# ---------------------------------------------------------
# 3. LÓGICA DE NEGÓCIO
# ---------------------------------------------------------
IDS_ADM = [5009.2025, 5010.2025, 5011.2025]
df_adm = df_raw[df_raw['Projeto'].isin(IDS_ADM)].copy()
df_obras = df_raw[~df_raw['Projeto'].isin(IDS_ADM)].copy()

def get_custo_total(row):
    return row['Mat_Real'] + row['Desp_Real'] + row['HH_Real_Vlr'] + row['Impostos']

# Cálculos Macro
status_venda = ['Não iniciado', 'Em andamento', 'Finalizado', 'Apresentado']
df_carteira_total = df_obras[df_obras['Status'].isin(status_venda)]
valor_vendido_total = df_carteira_total['Vendido'].sum()

df_concluido = df_obras[df_obras['Status'].isin(['Finalizado', 'Apresentado'])]
valor_concluido = df_concluido['Vendido'].sum()
valor_faturado_total = df_obras['Faturado'].sum()

custo_adm_total = df_adm.apply(get_custo_total, axis=1).sum()
overhead_pct = (custo_adm_total / valor_vendido_total * 100) if valor_vendido_total > 0 else 0

# Cálculos de Margem
def get_margem_ponderada(df_in):
    if df_in.empty: return 0.0
    venda = df_in['Vendido'].sum()
    custo = df_in.apply(get_custo_total, axis=1).sum()
    return ((venda - custo) / venda * 100) if venda > 0 else 0

mg_geral = get_margem_ponderada(df_obras)
mg_concluida = get_margem_ponderada(df_concluido)

custo_obras_total = df_obras.apply(get_cust
