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

    /* KPIs de Metas (Topo) */
    .goal-card {
        background-color: #161b22; padding: 15px; border-radius: 8px;
        border: 1px solid #30363d; margin-bottom: 10px;
    }
    .goal-title { color: #8b949e; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1px; }
    .goal-value { color: white; font-size: 1.6rem; font-weight: bold; font-family: "Source Sans Pro"; }
    .goal-sub { color: #8b949e; font-size: 0.8rem; margin-top: 5px; }

    /* Cards de Projetos (Grid) */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #161b22; border: 1px solid #30363d; border-radius: 8px;
        transition: transform 0.2s;
    }
    [data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color: #58a6ff; transform: translateY(-2px);
    }
    
    /* Customização Tags Multiselect */
    span[data-baseweb="tag"] {
        background-color: #30363d !important; color: white !important; border: 1px solid #8b949e;
    }
    span[data-baseweb="tag"] svg { fill: white !important; }

    /* Estilos Gerais */
    .tile-header { padding: 15px 15px 10px 15px; }
    .tile-title { color: white; font-weight: 700; font-size: 1rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .tile-sub { color: #8b949e; font-size: 0.75rem; }
    .data-strip { background-color: #0d1117; padding: 10px 15px; display: flex; justify-content: space-between; border-top: 1px solid #21262d; border-bottom: 1px solid #21262d; }
    .data-col { display: flex; flex-direction: column; align-items: center; width: 25%; }
    .data-lbl { font-size: 0.6rem; color: #8b949e; text-transform: uppercase; }
    .data-val { font-size: 0.85rem; font-weight: 700; color: #e6edf3; }
    .tile-footer { padding: 10px 15px; }
    .progress-track { background-color: #21262d; height: 4px; width: 100%; border-radius: 2px; overflow: hidden; margin-bottom: 8px;}
    .badge-status { font-size: 0.65rem; font-weight: 700; text-transform: uppercase; padding: 2px 8px; border-radius: 4px; }
    .footer-row { display: flex; justify-content: space-between; align-items: center; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. DADOS E SIMULAÇÃO
# ---------------------------------------------------------
@st.cache_data(ttl=0)
def load_data():
    # Carrega seu excel real
    return pd.read_excel("dados_obras_v5.xlsx")

try:
    df_raw = load_data()
except FileNotFoundError:
    # Se não tiver o arquivo, cria um dummy para visualizarmos a lógica
    data_dummy = {
        'Projeto': [101, 102, 103, 104, 5009.2025, 5010.2025, 5011.2025],
        'Descricao': ['Obra A', 'Obra B', 'Proposta X', 'Obra C', 'Ferramental', 'Desp. Comercial', 'Demandas Int.'],
        'Status': ['Em andamento', 'Em andamento', 'Apresentado', 'Finalizado', 'Em andamento', 'Em andamento', 'Em andamento'],
        'Cliente': ['Cli A', 'Cli B', 'Cli C', 'Cli A', 'Interno', 'Interno', 'Interno'],
        'Cidade': ['SP', 'MG', 'RJ', 'SP', '-', '-', '-'],
        'Vendido': [150000, 200000, 500000, 100000, 0, 0, 0], # Fixos não vendem
        'Mat_Orc': [50000, 60000, 200000, 30000, 10000, 5000, 2000],
        'Mat_Real': [45000, 10000, 0, 28000, 15000, 5000, 2000], # Fixos têm custo
        'Desp_Real': [5000, 2000, 0, 1000, 2000, 12000, 1000],
        'HH_Real_Vlr': [20000, 5000, 0, 15000, 5000, 10000, 30000],
        'Impostos': [15000, 20000, 0, 10000, 0, 0, 0],
        'HH_Orc_Qtd': [100, 150, 300, 80, 0, 0, 0],
        'HH_Real_Qtd': [80, 20, 0, 80, 50, 100, 200],
        'Conclusao_%': [80, 10, 0, 100, 0, 0, 0]
    }
    df_raw = pd.DataFrame(data_dummy)

# --- LIMPEZA BÁSICA ---
def clean_currency(x):
    if isinstance(x, (int, float)): return x
    try: return float(str(x).replace('R$', '').replace('.', '').replace(',', '.'))
    except: return 0.0

cols_monetarias = ['Vendido', 'Mat_Real', 'Desp_Real', 'HH_Real_Vlr', 'Impostos']
for col in cols_monetarias:
    df_raw[col] = df_raw[col].apply(clean_currency)

# ---------------------------------------------------------
# 3. LÓGICA DE NEGÓCIO (SEPARAÇÃO)
# ---------------------------------------------------------
# IDs dos projetos estruturais (Custo puro)
IDS_FIXOS = [5009.2025, 5010.2025, 5011.2025]

# Separa o DataFrame
df_estrutural = df_raw[df_raw['Projeto'].isin(IDS_FIXOS)].copy()
df_obras = df_raw[~df_raw['Projeto'].isin(IDS_FIXOS)].copy() # Apenas obras "produtivas"

# CÁLCULO DE CUSTOS E MARGEM
# Função para calcular custo total de uma linha
def get_custo(row):
    return row['Mat_Real'] + row['Desp_Real'] + row['HH_Real_Vlr'] + row['Impostos']

# 1. Total Vendido (Só considera obras, pois fixos não vendem)
total_vendido = df_obras['Vendido'].sum()

# 2. Custo Total da Empresa (Custo Obras + Custo Fixos)
custo_obras = df_obras.apply(get_custo, axis=1).sum()
custo_fixos = df_estrutural.apply(get_custo, axis=1).sum()
custo_total_geral = custo_obras + custo_fixos

# 3. Lucro Líquido Real
lucro_liquido_real = total_vendido - custo_total_geral

# 4. Dados "Apresentados" (Pipeline)
df_apresentado = df_obras[df_obras['Status'] == 'Apresentado']
total_apresentado = df_apresentado['Vendido'].sum()
# Margem média projetada das obras apresentadas
# (Cálculo simplificado de margem individual para média)
def calc_margem_row(row):
    custo_est = row['Mat_Orc'] # + outros custos orçados se tiver
    return ((row['Vendido'] - custo_est) / row['Vendido'] * 100) if row['Vendido'] > 0 else 0

margem_media_apresentada = df_apresentado.apply(calc_margem_row, axis=1).mean() if not df_apresentado.empty else 0

# ---------------------------------------------------------
# 4. INTERFACE - TOPO (METAS E BIG NUMBERS)
# ---------------------------------------------------------
st.title("Dashboard de Resultados")

# --- DEFINIÇÃO DE METAS ANUAIS (EDITÁVEIS AQUI) ---
META_VENDAS_ANO = 5000000.00  # Ex: 5 Milhões
META_LUCRO_ANO = 1000000.00   # Ex: 1 Milhão

col_metas, col_pipeline = st.columns([2, 1])

# FORMATAÇÃO PT-BR
def fmt(v): 
    if v >= 1e6: return f"R$ {v/1e6:.1f}M"
    if v >= 1e3: return f"R$ {v/1e3:.1f}k"
    return f"R$ {v:,.0f}"

with col_metas:
    st.markdown("### 🎯 Acompanhamento de Metas")
    m1, m2 = st.columns(2)
    
    # CARD META VENDAS
    pct_vendas = (total_vendido / META_VENDAS_ANO) if META_VENDAS_ANO > 0 else 0
    with m1:
        st.markdown(f"""
        <div class="goal-card">
            <div class="goal-title">Valor Vendido (YTD)</div>
            <div class="goal-value" style="color: #58a6ff">{fmt(total_vendido)}</div>
            <div class="goal-sub">Meta: {fmt(META_VENDAS_ANO)} ({pct_vendas*100:.1f}%)</div>
        </div>
        """, unsafe_allow_html=True)
        st.progress(min(pct_vendas, 1.0))

    # CARD META LUCRO (Considerando descontos dos fixos)
    pct_lucro = (lucro_liquido_real / META_LUCRO_ANO) if META_LUCRO_ANO > 0 else 0
    cor_lucro = "#3fb950" if lucro_liquido_real > 0 else "#da3633"
    with m2:
        st.markdown(f"""
        <div class="goal-card">
            <div class="goal-title">Lucro Líquido Real</div>
            <div class="goal-value" style="color: {cor_lucro}">{fmt(lucro_liquido_real)}</div>
            <div class="goal-sub">Meta: {fmt(META_LUCRO_ANO)} ({pct_lucro*100:.1f}%)</div>
        </div>
        """, unsafe_allow_html=True)
        st.progress(min(pct_lucro if pct_lucro > 0 else 0, 1.0))

    # Aviso sobre os custos fixos
    st.caption(f"📉 *O Lucro Líquido já desconta R$ {fmt(custo_fixos)} referentes a Ferramental, Comercial e Demandas Internas.*")

with col_pipeline:
    st.markdown("### 💼 Pipeline Comercial")
    # Card único para "Apresentado"
    st.markdown(f"""
    <div class="goal-card" style="border-left: 4px solid #a371f7;">
        <div class="goal-title">Propostas Apresentadas</div>
        <div class="goal-value">{fmt(total_apresentado)}</div>
        <div style="margin-top: 10px; display: flex; justify-content: space-between;">
            <span style="color: #8b949e; font-size: 0.8rem;">Qtd: <b>{len(df_apresentado)}</b></span>
            <span style="color: #a371f7; font-weight: bold; font-size: 0.9rem;">Margem: {margem_media_apresentada:.1f}%</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.info("💡 Esses valores ainda não constam no 'Valor Vendido'.")

st.divider()

# ---------------------------------------------------------
# 5. FILTROS E GRID DE PROJETOS (Apenas Obras Produtivas)
# ---------------------------------------------------------
# Recalcula margens para o dataframe de exibição
def calcular_dados_extras(row):
    custo = get_custo(row)
    lucro = row['Vendido'] - custo
    margem = (lucro / row['Vendido'] * 100) if row['Vendido'] > 0 else 0
    
    hh_orc, hh_real = row['HH_Orc_Qtd'], row['HH_Real_Qtd']
    hh_perc = (hh_real / hh_orc * 100) if hh_orc > 0 else 0
    
    fisico = row['Conclusao_%']
    critico = True if (margem < 20 and row['Status'] != 'Apresentado') or (hh_perc > fisico + 10) else False
    
    return pd.Series([margem, critico, hh_perc])

# Aplica cálculos apenas nas obras (Ignora fixos na lista visual)
cols_extras = df_obras.apply(calcular_dados_extras, axis=1)
df_obras['Margem_%'] = cols_extras[0]
df_obras['E_Critico'] = cols_extras[1]
df_obras['HH_Progresso'] = cols_extras[2]

# --- BARRA DE FERRAMENTAS ---
col_filtro, col_sort_criterio, col_sort_ordem = st.columns([3, 1, 1])

with col_filtro:
    status_options = df_obras['Status'].unique()
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
mapa_colunas = {"Projeto": "Projeto", "Valor Vendido": "Vendido", "Margem": "Margem_%", "Andamento": "Conclusao_%"}
df_show = df_show.sort_values(by=mapa_colunas[criterio_sort], ascending=eh_crescente)

st.write(f"**{len(df_show)}** projetos listados (Excluindo fixos)")
st.write("")

cols = st.columns(3)
for i, (index, row) in enumerate(df_show.iterrows()):
    with cols[i % 3]:
        pct = int(row['Conclusao_%'])
        status_raw = str(row['Status']).strip()
        
        # Cores
        if status_raw == "Finalizado": cor_tema, bg_b, cl_b = "#238636", "rgba(35,134,54,0.2)", "#3fb950"
        elif status_raw == "Apresentado": cor_tema, bg_b, cl_b = "#a371f7", "rgba(163,113,247,0.2)", "#d2a8ff"
        elif status_raw == "Em andamento": cor_tema, bg_b, cl_b = "#d29922", "rgba(210,153,34,0.2)", "#e3b341"
        else: cor_tema, bg_b, cl_b = "#da3633", "rgba(218,54,51,0.2)", "#f85149"

        cor_margem = "#da3633" if row['Margem_%'] < 20 else "#3fb950"
        
        with st.container(border=True):
            st.markdown(f"""
            <div class="tile-header" style="border-left: 3px solid {cor_tema}">
                <div class="tile-title">{row['Projeto']} - {row['Descricao']}</div>
                <div class="tile-sub">{row['Cliente']} | {row['Cidade']}</div>
            </div>
            <div class="data-strip">
                <div class="data-col"><span class="data-lbl">Venda</span><span class="data-val">{fmt(row['Vendido'])}</span></div>
                <div class="data-col"><span class="data-lbl">Margem</span><span class="data-val" style="color:{cor_margem}">{row['Margem_%']:.0f}%</span></div>
                <div class="data-col"><span class="data-lbl">Mat</span><span class="data-val">{fmt(row['Mat_Real'])}</span></div>
            </div>
            <div class="tile-footer">
                <div class="progress-track"><div style="width:{pct}%; height:100%; background-color:{cor_tema}"></div></div>
                <div class="footer-row">
                    <span class="badge-status" style="background-color:{bg_b}; color:{cl_b}">{status_raw}</span>
                    <span style="font-weight:bold; color:{cl_b}; font-size:0.8rem">{pct}%</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Abrir ↗", key=f"btn_{row['Projeto']}", use_container_width=True):
                pass
