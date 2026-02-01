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
        min-height: 110px;
    }
    .kpi-title { color: #8b949e; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 5px; font-weight: 600;}
    .kpi-val { font-size: 1.4rem; font-weight: 700; color: white; font-family: "Source Sans Pro", sans-serif; }
    .kpi-sub { font-size: 0.75rem; color: #8b949e; margin-top: 5px; display: flex; justify-content: space-between; align-items: center;}
    
    /* Cores de Texto Auxiliares */
    .txt-green { color: #3fb950; }
    .txt-red { color: #da3633; }
    .txt-blue { color: #58a6ff; }
    .txt-purple { color: #a371f7; }
    .txt-orange { color: #d29922; }

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
    
    /* Tags e Botões */
    div[data-testid="stVerticalBlockBorderWrapper"] button {
        background-color: transparent; color: #58a6ff; border: 1px solid #30363d; border-radius: 4px;
        font-size: 0.65rem !important; padding: 0px 0px !important; height: 24px !important; min-height: 24px !important; line-height: 1 !important; margin: 0; width: 100%;
    }
    span[data-baseweb="tag"] { background-color: #30363d !important; color: white !important; border: 1px solid #8b949e; }
    span[data-baseweb="tag"] svg { fill: white !important; }
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

# Limpeza Monetária
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
# IDs dos custos administrativos (Overhead)
IDS_ADM = [5009.2025, 5010.2025, 5011.2025]

# Separação
df_adm = df_raw[df_raw['Projeto'].isin(IDS_ADM)].copy()
df_obras = df_raw[~df_raw['Projeto'].isin(IDS_ADM)].copy()

# Função de Custo Total
def get_custo_total(row):
    return row['Mat_Real'] + row['Desp_Real'] + row['HH_Real_Vlr'] + row['Impostos']

# --- CÁLCULOS MACRO (VOLUME) ---

# 1. Valor Vendido Total
status_venda = ['Não iniciado', 'Em andamento', 'Finalizado', 'Apresentado']
df_carteira_total = df_obras[df_obras['Status'].isin(status_venda)]
valor_vendido_total = df_carteira_total['Vendido'].sum()

# 2. Valor Concluído
df_concluido = df_obras[df_obras['Status'].isin(['Finalizado', 'Apresentado'])]
valor_concluido = df_concluido['Vendido'].sum()

# 3. Valor Faturado
valor_faturado_total = df_obras['Faturado'].sum()

# 4. Custos Administrativos
custo_adm_total = df_adm.apply(get_custo_total, axis=1).sum()
overhead_pct = (custo_adm_total / valor_vendido_total * 100) if valor_vendido_total > 0 else 0

# --- CÁLCULOS DE EFICIÊNCIA (MARGENS) ---
def get_margem_ponderada(df_in):
    if df_in.empty: return 0.0
    venda = df_in['Vendido'].sum()
    custo = df_in.apply(get_custo_total, axis=1).sum()
    return ((venda - custo) / venda * 100) if venda > 0 else 0

# 1. Margem Geral (Bruta)
mg_geral = get_margem_ponderada(df_obras)

# 2. Margem Concluída (Bruta)
mg_concluida = get_margem_ponderada(df_concluido)

# 3. Margem Líquida (Pós Administrativo)
custo_obras_total = df_obras.apply(get_custo_total, axis=1).sum()
lucro_bruto_total = valor_vendido_total - custo_obras_total
lucro_liquido_final = lucro_bruto_total - custo_adm_total
mg_liquida_pos_adm = (lucro_liquido_final / valor_vendido_total * 100) if valor_vendido_total > 0 else 0

# Contagem de Obras
df_aberto = df_obras[df_obras['Status'].isin(['Em andamento', 'Não iniciado'])]
qtd_aberto = len(df_aberto)
qtd_total = len(df_obras) 

# --- METAS ---
META_VENDAS = 5000000.00
META_MARGEM = 25.0

# ---------------------------------------------------------
# 4. INTERFACE - CABEÇALHO
# ---------------------------------------------------------
st.title("Dashboard de Resultados")

# LINHA 1: Volume Financeiro (3 Cards)
st.markdown("### 📊 Indicadores de Volume (Financeiro)")
row1_c1, row1_c2, row1_c3 = st.columns(3)

# CARD 1.1: VALOR VENDIDO
pct_meta_venda = (valor_vendido_total / META_VENDAS * 100)
with row1_c1:
    st.markdown(f"""
    <div class="kpi-card" style="border-left: 3px solid #58a6ff;">
        <div class="kpi-title">Valor Vendido (Carteira)</div>
        <div class="kpi-val">{formatar_valor_ptbr(valor_vendido_total)}</div>
        <div class="kpi-sub">
            <span>Meta: {pct_meta_venda:.0f}%</span>
            <span class="txt-blue">Faturado: {formatar_valor_ptbr(valor_faturado_total)}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# CARD 1.2: VALOR CONCLUÍDO
pct_concluido = (valor_concluido / valor_vendido_total * 100) if valor_vendido_total > 0 else 0
with row1_c2:
    st.markdown(f"""
    <div class="kpi-card" style="border-left: 3px solid #3fb950;">
        <div class="kpi-title">Valor Concluído (Fin + Apr)</div>
        <div class="kpi-val">{formatar_valor_ptbr(valor_concluido)}</div>
        <div class="kpi-sub">
            <span>Produção Entregue</span>
            <span class="txt-green">{pct_concluido:.0f}% da carteira</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# CARD 1.3: CUSTO ADM
with row1_c3:
    st.markdown(f"""
    <div class="kpi-card" style="border-left: 3px solid #d29922;">
        <div class="kpi-title">Custo Administrativo</div>
        <div class="kpi-val">{formatar_valor_ptbr(custo_adm_total)}</div>
        <div class="kpi-sub">
            <span>Overhead:</span>
            <span class="txt-orange" style="font-weight:bold">{overhead_pct:.1f}% da Receita</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# LINHA 2: Eficiência e Margens (4 Cards)
st.markdown("### 📈 Indicadores de Eficiência (Margens & Status)")
row2_c1, row2_c2, row2_c3, row2_c4 = st.columns(4)

# CARD 2.1: MARGEM GERAL (Carteira)
cor_m_geral = "txt-green" if mg_geral >= META_MARGEM else "txt-red"
with row2_c1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Margem Geral (Carteira)</div>
        <div class="kpi-val {cor_m_geral}">{mg_geral:.1f}%</div>
        <div class="kpi-sub">
            <span>Média Ponderada Total</span>
            <span>Meta: 25%</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# CARD 2.2: MARGEM CONCLUÍDA
cor_m_conc = "txt-green" if mg_concluida >= META_MARGEM else "txt-red"
with row2_c2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Margem Concluída (Fin + Apr)</div>
        <div class="kpi-val {cor_m_conc}">{mg_concluida:.1f}%</div>
        <div class="kpi-sub">
            <span>Resultado Entregue</span>
            <span>Meta: 25%</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# CARD 2.3: MARGEM LÍQUIDA (PÓS ADM)
cor_m_liq = "txt-green" if mg_liquida_pos_adm >= (META_MARGEM - 10) else "txt-red"
with row2_c3:
    st.markdown(f"""
    <div class="kpi-card" style="border-left: 3px solid #a371f7;">
        <div class="kpi-title">Margem Líquida (Pós Adm)</div>
        <div class="kpi-val {cor_m_liq}">{mg_liquida_pos_adm:.1f}%</div>
        <div class="kpi-sub">
            <span>Descontado Overhead</span>
            <span class="txt-purple">Real Final</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# CARD 2.4: STATUS DE PRODUÇÃO
with row2_c4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Status de Produção</div>
        <div class="kpi-val">{qtd_aberto} <span style='font-size:1rem; color:#8b949e'>/ {qtd_total}</span></div>
        <div class="kpi-sub">
            <span>Aberto (Não Ini + Andam)</span>
            <span class="txt-blue">Foco Operacional</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ---------------------------------------------------------
# 5. CARDS DE PROJETOS (GRID INTACTO)
# ---------------------------------------------------------

def calcular_dados_extras(row):
    vendido = float(row['Vendido'])
    custo = float(row['Mat_Real'] + row['Desp_Real'] + row['HH_Real_Vlr'] + row['Impostos'])
    lucro = vendido - custo
    margem = (lucro / vendido * 100) if vendido > 0 else 0
    hh_orc, hh_real = float(row['HH_Orc_Qtd']), float(row['HH_Real_Qtd'])
    hh_perc = (hh_real / hh_orc * 100) if hh_orc > 0 else 0
    fisico = float(row['Conclusao_%'])
    critico = False
    
    if (margem < META_MARGEM and row['Status'] != 'Apresentado') or (hh_perc > fisico + 10):
        critico = True
    return pd.Series([margem, critico, hh_perc])

# Aplica cálculos
cols_extras = df_obras.apply(calcular_dados_extras, axis=1)
df_obras['Margem_%'] = cols_extras[0]
df_obras['E_Critico'] = cols_extras[1]
df_obras['HH_Progresso'] = cols_extras[2]

# --- BARRA DE FILTROS ---
col_filtro, col_sort_criterio, col_sort_ordem = st.columns([3, 1, 1])

with col_filtro:
    status_options = ["Não iniciado", "Em andamento", "Finalizado", "Apresentado"]
    status_selecionados = st.multiselect("Filtrar por:", options=status_options, default=status_options)

with col_sort_criterio:
    criterio_sort = st.selectbox("Ordenar por:", ["Projeto", "Valor Vendido", "Margem", "Andamento"])

with col_sort_ordem:
    direcao_sort = st.selectbox("Ordem:", ["Decrescente", "Crescente"])

# --- EXIBIÇÃO ---
if not status_selecionados:
    st.info("Selecione pelo menos um status acima.")
    st.stop() 

df_show = df_obras[df_obras['Status'].isin(status_selecionados)].copy()

# Ordenação
eh_crescente = True if direcao_sort == "Crescente" else False
mapa_sort = {"Projeto": "Projeto", "Valor Vendido": "Vendido", "Margem": "Margem_%", "Andamento": "Conclusao_%"}
df_show = df_show.sort_values(by=mapa_sort[criterio_sort], ascending=eh_crescente)

st.write(f"**{len(df_show)}** projetos encontrados")
st.write("")

cols = st.columns(3)

for i, (index, row) in enumerate(df_show.iterrows()):
    with cols[i % 3]:
        pct = int(row['Conclusao_%'])
        status_raw = str(row['Status']).strip()
        
        # Cores e Estilos
        if status_raw == "Finalizado": cor_t, bg_b, cl_b = "#3fb950", "rgba(63,185,80,0.2)", "#3fb950"
        elif status_raw == "Apresentado": cor_t, bg_b, cl_b = "#a371f7", "rgba(163,113,247,0.2)", "#d2a8ff"
        elif status_raw == "Em andamento": cor_t, bg_b, cl_b = "#d29922", "rgba(210,153,34,0.2)", "#e3b341"
        else: cor_t, bg_b, cl_b = "#da3633", "rgba(218,54,51,0.2)", "#f85149"

        cor_margem = "#da3633" if row['Margem_%'] < META_MARGEM else "#3fb950"
        
        # Métricas internas do card
        hh_orc, hh_real = float(row['HH_Orc_Qtd']), float(row['HH_Real_Qtd'])
        pct_horas = (hh_real / hh_orc * 100) if hh_orc > 0 else 0
        cor_horas = "#da3633" if pct_horas > 100 else "#e6edf3"
        
        mat_orc, mat_real = float(row['Mat_Orc']), float(row['Mat_Real'])
        pct_mat = (mat_real / mat_orc * 100) if mat_orc > 0 else 0
        cor_mat = "#da3633" if pct_mat > 100 else "#e6edf3"
        
        valor_formatado = formatar_valor_ptbr(row['Vendido'])
        
        with st.container(border=True):
            st.markdown(f"""
            <div class="tile-header" style="border-left: 3px solid {cor_t}">
                <div class="tile-title" title="{row['Projeto']}">{row['Projeto']} - {row['Descricao']}</div>
                <div class="tile-sub">{row['Cliente']} | {row['Cidade']}</div>
            </div>
            <div class="data-strip">
                <div class="data-col"><span class="data-lbl">Valor</span><span class="data-val">{valor_formatado}</span></div>
                <div class="data-col"><span class="data-lbl">Margem</span><span class="data-val" style="color: {cor_margem}">{row['Margem_%']:.0f}%</span></div>
                <div class="data-col"><span class="data-lbl">Horas</span><span class="data-val" style="color: {cor_horas}">{pct_horas:.0f}%</span></div>
                <div class="data-col"><span class="data-lbl">Mat</span><span class="data-val" style="color: {cor_mat}">{pct_mat:.0f}%</span></div>
            </div>
            <div class="tile-footer">
                <div class="progress-track"><div class="progress-fill" style="width: {pct}%; background-color: {cor_t};"></div></div>
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
