import streamlit as st
import pandas as pd

# ---------------------------------------------------------
# 1. CONFIGURAÇÃO VISUAL
# ---------------------------------------------------------
st.set_page_config(page_title="Dashboard TE", layout="wide")

st.markdown("""
<style>
    .stApp {background-color: #0e1117;}
    .block-container {padding-top: 2rem;}

    /* --- CSS DOS KPIS (CABEÇALHO) --- */
    .kpi-card {
        background-color: #161b22; 
        border: 1px solid #30363d; 
        border-radius: 8px; 
        padding: 15px;
        height: 100%;
        display: flex; flex-direction: column; justify-content: space-between;
    }
    .kpi-title { color: #8b949e; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 5px; }
    .kpi-val { font-size: 1.5rem; font-weight: 700; color: white; font-family: "Source Sans Pro", sans-serif; }
    .kpi-sub { font-size: 0.75rem; color: #8b949e; margin-top: 5px; }
    
    /* --- CSS DOS CARDS DE PROJETO (MANTIDO) --- */
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
    .tile-header { padding: 15px 15px 10px 15px; }
    .tile-title {
        color: white; font-family: "Source Sans Pro", sans-serif;
        font-weight: 700; font-size: 1rem;
        white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
        margin-bottom: 2px;
    }
    .tile-sub { color: #8b949e; font-size: 0.75rem; font-family: "Source Sans Pro", sans-serif; }
    .data-strip {
        background-color: #0d1117; border-top: 1px solid #21262d; border-bottom: 1px solid #21262d;
        padding: 10px 15px; display: flex; justify-content: space-between; align-items: center;
    }
    .data-col { display: flex; flex-direction: column; align-items: center; width: 25%; }
    .data-col:not(:last-child) { border-right: 1px solid #30363d; }
    .data-lbl { font-size: 0.6rem; color: #8b949e; text-transform: uppercase; margin-bottom: 2px; }
    .data-val { font-size: 0.85rem; font-weight: 700; color: #e6edf3; font-family: "Source Sans Pro", sans-serif; }
    .tile-footer { padding: 10px 15px; }
    .progress-track {
        background-color: #21262d; height: 4px; border-radius: 2px;
        width: 100%; margin-bottom: 10px; overflow: hidden;
    }
    .badge-status {
        font-size: 0.65rem; font-weight: 700; text-transform: uppercase;
        padding: 2px 8px; border-radius: 4px; letter-spacing: 0.5px; line-height: 1.2;
    }
    .footer-pct {
        font-size: 0.8rem; font-weight: 700; font-family: "Source Sans Pro", sans-serif;
        line-height: 1; display: flex; align-items: center;
    }
    /* Botão Abrir */
    div[data-testid="stVerticalBlockBorderWrapper"] button {
        background-color: transparent; color: #58a6ff; border: 1px solid #30363d; border-radius: 4px;
        font-size: 0.65rem !important; padding: 0px 0px !important;
        height: 24px !important; min-height: 24px !important; line-height: 1 !important;
        margin: 0; width: 100%;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] button:hover {
        background-color: #1f242c; border-color: #30363d; text-decoration: none;
    }
    
    /* Customização Tags Multiselect */
    span[data-baseweb="tag"] {
        background-color: #30363d !important; color: white !important; border: 1px solid #8b949e;
    }
    span[data-baseweb="tag"] svg { fill: white !important; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. DADOS E CÁLCULOS
# ---------------------------------------------------------
@st.cache_data(ttl=0)
def load_data():
    return pd.read_excel("dados_obras_v5.xlsx")

try:
    df_raw = load_data()
except FileNotFoundError:
    st.error("⚠️ Base de dados não encontrada.")
    st.stop()

# Limpeza Monetária
def clean_currency(x):
    if isinstance(x, (int, float)): return x
    try: return float(str(x).replace('R$', '').replace('.', '').replace(',', '.'))
    except: return 0.0

cols_mony = ['Vendido', 'Mat_Real', 'Desp_Real', 'HH_Real_Vlr', 'Impostos']
for col in cols_mony:
    df_raw[col] = df_raw[col].apply(clean_currency)

# --- SEPARAÇÃO DE DADOS ---
# IDs dos projetos de custo estrutural
IDS_FIXOS = [5009.2025, 5010.2025, 5011.2025]

df_fixos = df_raw[df_raw['Projeto'].isin(IDS_FIXOS)].copy()
df_obras = df_raw[~df_raw['Projeto'].isin(IDS_FIXOS)].copy() # Apenas obras "produtivas"

# --- CÁLCULOS FINANCEIROS GLOBAIS ---
def get_custo_total(df):
    return (df['Mat_Real'] + df['Desp_Real'] + df['HH_Real_Vlr'] + df['Impostos']).sum()

custo_fixo_total = get_custo_total(df_fixos)
custo_obras_total = get_custo_total(df_obras)
valor_vendido_total = df_obras['Vendido'].sum()

# Lucro Líquido Real = (Vendas) - (Custos Obras + Custos Fixos)
lucro_real_total = valor_vendido_total - (custo_obras_total + custo_fixo_total)

# Dados de Pipeline (Apresentado)
df_apresentado = df_obras[df_obras['Status'] == 'Apresentado']
valor_apresentado = df_apresentado['Vendido'].sum()

# Cálculo de Margem Média dos Apresentados
def calc_margem_orcada(row):
    custo_est = row['Mat_Orc'] # Aqui poderia somar HH_Orc se tiver o valor em R$
    return ((row['Vendido'] - custo_est) / row['Vendido'] * 100) if row['Vendido'] > 0 else 0

margem_media_apresentado = df_apresentado.apply(calc_margem_orcada, axis=1).mean() if not df_apresentado.empty else 0

# --- METAS (Defina seus valores aqui) ---
META_VENDAS = 5000000.00
META_LUCRO = 1000000.00

# Formatação
def fmt_k(v): 
    if v >= 1e6: return f"R$ {v/1e6:.1f}M"
    if v >= 1e3: return f"R$ {v/1e3:.0f}k"
    return f"R$ {v:,.0f}"

# ---------------------------------------------------------
# 3. INTERFACE - CABEÇALHO (NOVO LAYOUT)
# ---------------------------------------------------------
st.title("Dashboard de Resultados")

# Topo dividido em 4 colunas principais
col1, col2, col3, col4 = st.columns(4)

# CARD 1: META DE VENDAS
pct_v = min((valor_vendido_total / META_VENDAS), 1.0)
with col1:
    st.markdown(f"""
    <div class="kpi-card" style="border-left: 3px solid #58a6ff;">
        <div>
            <div class="kpi-title">Valor Vendido (Ano)</div>
            <div class="kpi-val">{fmt_k(valor_vendido_total)}</div>
        </div>
        <div class="kpi-sub">
            Meta: {fmt_k(META_VENDAS)} ({pct_v*100:.0f}%)
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.progress(pct_v)

# CARD 2: META DE LUCRO
pct_l = max(min((lucro_real_total / META_LUCRO), 1.0), 0.0)
cor_lucro = "#3fb950" if lucro_real_total > 0 else "#da3633"
with col2:
    st.markdown(f"""
    <div class="kpi-card" style="border-left: 3px solid {cor_lucro};">
        <div>
            <div class="kpi-title">Lucro Líquido Real</div>
            <div class="kpi-val" style="color: {cor_lucro}">{fmt_k(lucro_real_total)}</div>
        </div>
        <div class="kpi-sub">
            Meta: {fmt_k(META_LUCRO)} ({pct_l*100:.0f}%)
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.progress(pct_l)

# CARD 3: PIPELINE (APRESENTADO)
with col3:
    st.markdown(f"""
    <div class="kpi-card" style="border-left: 3px solid #a371f7;">
        <div>
            <div class="kpi-title">Propostas (Apresentado)</div>
            <div class="kpi-val">{fmt_k(valor_apresentado)}</div>
        </div>
        <div class="kpi-sub" style="display:flex; justify-content:space-between;">
            <span>Qtd: {len(df_apresentado)}</span>
            <span style="color:#a371f7; font-weight:bold">Mg: {margem_media_apresentado:.1f}%</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# CARD 4: CUSTOS ESTRUTURAIS (FIXOS)
with col4:
    st.markdown(f"""
    <div class="kpi-card" style="border-left: 3px solid #d29922;">
        <div>
            <div class="kpi-title">Custos Estruturais</div>
            <div class="kpi-val">{fmt_k(custo_fixo_total)}</div>
        </div>
        <div class="kpi-sub">
            Ferramental, Comercial e Interno<br>
            <span style="font-style:italic; opacity:0.7">(Já descontado do lucro)</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ---------------------------------------------------------
# 4. CARDS DE PROJETOS (GRID ORIGINAL)
# ---------------------------------------------------------

# Cálculos linha a linha para os cards
def calc_extras(row):
    custo = get_custo_total(pd.DataFrame([row]))
    lucro = row['Vendido'] - custo
    margem = (lucro / row['Vendido'] * 100) if row['Vendido'] > 0 else 0
    
    hh_orc, hh_real = float(row['HH_Orc_Qtd']), float(row['HH_Real_Qtd'])
    hh_perc = (hh_real / hh_orc * 100) if hh_orc > 0 else 0
    
    fisico = float(row['Conclusao_%'])
    critico = False
    if (margem < 20 and row['Status'] != 'Apresentado') or (hh_perc > fisico + 10):
        critico = True
    return pd.Series([margem, critico, hh_perc])

# Aplica cálculos apenas nas OBRAS (ignorando fixos)
cols_calc = df_obras.apply(calc_extras, axis=1)
df_obras['Margem_%'] = cols_calc[0]
df_obras['E_Critico'] = cols_calc[1]
df_obras['HH_Progresso'] = cols_calc[2]

# --- BARRA DE FILTROS ---
col_filtro, col_sort_criterio, col_sort_ordem = st.columns([3, 1, 1])

with col_filtro:
    status_options = ["Não iniciado", "Em andamento", "Finalizado", "Apresentado"]
    status_selecionados = st.multiselect(
        "Filtrar por:", 
        options=status_options, 
        default=status_options 
    )

with col_sort_criterio:
    criterio_sort = st.selectbox("Ordenar por:", ["Projeto", "Valor Vendido", "Margem", "Andamento"])

with col_sort_ordem:
    direcao_sort = st.selectbox("Ordem:", ["Decrescente", "Crescente"])

# --- RENDERIZAÇÃO ---
if not status_selecionados:
    st.info("Selecione pelo menos um status acima para visualizar os projetos.")
    st.stop()

df_show = df_obras[df_obras['Status'].isin(status_selecionados)].copy()

# Ordenação
eh_crescente = True if direcao_sort == "Crescente" else False
mapa_sort = {"Projeto": "Projeto", "Valor Vendido": "Vendido", "Margem": "Margem_%", "Andamento": "Conclusao_%"}
df_show = df_show.sort_values(by=mapa_sort[criterio_sort], ascending=eh_crescente)

st.write(f"**{len(df_show)}** projetos encontrados")
st.write("")

cols = st.columns(3)

# Loop Original dos Cards
for i, (index, row) in enumerate(df_show.iterrows()):
    with cols[i % 3]:
        pct = int(row['Conclusao_%'])
        status_raw = str(row['Status']).strip()
        
        # Cores
        if status_raw == "Finalizado": cor_t, bg_b, cl_b = "#238636", "rgba(35,134,54,0.2)", "#3fb950"
        elif status_raw == "Apresentado": cor_t, bg_b, cl_b = "#a371f7", "rgba(163,113,247,0.2)", "#d2a8ff" # Roxo p/ Apresentado
        elif status_raw == "Em andamento": cor_t, bg_b, cl_b = "#d29922", "rgba(210,153,34,0.2)", "#e3b341"
        else: cor_t, bg_b, cl_b = "#da3633", "rgba(218,54,51,0.2)", "#f85149"

        cor_margem = "#da3633" if row['Margem_%'] < 20 else "#3fb950"
        hh_orc, hh_real = float(row['HH_Orc_Qtd']), float(row['HH_Real_Qtd'])
        pct_horas = (hh_real / hh_orc * 100) if hh_orc > 0 else 0
        cor_horas = "#da3633" if pct_horas > 100 else "#e6edf3"
        mat_orc, mat_real = float(row['Mat_Orc']), float(row['Mat_Real'])
        pct_mat = (mat_real / mat_orc * 100) if mat_orc > 0 else 0
        cor_mat = "#da3633" if pct_mat > 100 else "#e6edf3"
        
        with st.container(border=True):
            st.markdown(f"""
            <div class="tile-header" style="border-left: 3px solid {cor_t}">
                <div class="tile-title" title="{row['Projeto']}">{row['Projeto']} - {row['Descricao']}</div>
                <div class="tile-sub">{row['Cliente']} | {row['Cidade']}</div>
            </div>
            <div class="data-strip">
                <div class="data-col"><span class="data-lbl">Venda</span><span class="data-val">{fmt_k(row['Vendido'])}</span></div>
                <div class="data-col"><span class="data-lbl">Margem</span><span class="data-val" style="color: {cor_margem}">{row['Margem_%']:.0f}%</span></div>
                <div class="data-col"><span class="data-lbl">Horas</span><span class="data-val" style="color: {cor_horas}">{pct_horas:.0f}%</span></div>
                <div class="data-col"><span class="data-lbl">Mat</span><span class="data-val" style="color: {cor_mat}">{pct_mat:.0f}%</span></div>
            </div>
            <div class="tile-footer">
                <div class="progress-track"><div style="width: {pct}%; height: 100%; background-color: {cor_t};"></div></div>
                <div class="footer-row">
                    <span class="badge-status" style="background-color: {bg_b}; color: {cl_b}">{status_raw}</span>
                    <span class="footer-pct" style="color: {cl_b}">{pct}%</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            col_sp, col_btn = st.columns([2, 1])
            with col_btn:
                if st.button("Abrir ↗", key=f"btn_{row['Projeto']}", use_container_width=True):
                    st.session_state["projeto_foco"] = row['Projeto']
                    st.switch_page("dashboard_detalhado.py")
