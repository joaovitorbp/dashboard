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

    /* --- NOVO CSS DOS KPIS (CABEÇALHO) --- */
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

    /* --- CSS ORIGINAL DOS CARDS DE PROJETO (MANTIDO INTACTO) --- */
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

    /* Header e Textos do Card */
    .tile-header { padding: 15px 15px 10px 15px; }
    .tile-title {
        color: white; font-family: "Source Sans Pro", sans-serif;
        font-weight: 700; font-size: 1rem;
        white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
        margin-bottom: 2px;
    }
    .tile-sub { color: #8b949e; font-size: 0.75rem; font-family: "Source Sans Pro", sans-serif; }
    
    /* Faixa de Dados (Meio do Card) */
    .data-strip {
        background-color: #0d1117; border-top: 1px solid #21262d; border-bottom: 1px solid #21262d;
        padding: 10px 15px; display: flex; justify-content: space-between; align-items: center;
    }
    .data-col { display: flex; flex-direction: column; align-items: center; width: 25%; }
    .data-col:not(:last-child) { border-right: 1px solid #30363d; }
    .data-lbl { font-size: 0.6rem; color: #8b949e; text-transform: uppercase; margin-bottom: 2px; }
    .data-val { font-size: 0.85rem; font-weight: 700; color: #e6edf3; font-family: "Source Sans Pro", sans-serif; }

    /* Rodapé do Card */
    .tile-footer { padding: 10px 15px; }
    .progress-track {
        background-color: #21262d; height: 4px; border-radius: 2px;
        width: 100%; margin-bottom: 10px; overflow: hidden;
    }
    .progress-fill { height: 100%; border-radius: 2px; }
    .footer-row { display: flex; justify-content: space-between; align-items: center; height: 20px; }
    
    .badge-status {
        font-size: 0.65rem; font-weight: 700; text-transform: uppercase;
        padding: 2px 8px; border-radius: 4px; letter-spacing: 0.5px; line-height: 1.2;
    }
    .footer-pct {
        font-size: 0.8rem; font-weight: 700; font-family: "Source Sans Pro", sans-serif;
        line-height: 1; display: flex; align-items: center;
    }

    /* Botão "Abrir" */
    div[data-testid="stVerticalBlockBorderWrapper"] button {
        background-color: transparent; color: #58a6ff; border: 1px solid #30363d; border-radius: 4px;
        font-size: 0.65rem !important; padding: 0px 0px !important;
        height: 24px !important; min-height: 24px !important; line-height: 1 !important;
        margin: 0; width: 100%;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] button:hover {
        background-color: #1f242c; border-color: #30363d; text-decoration: none;
    }
    div[data-testid="column"] { padding: 0 8px; }

    /* Customização das Tags do Multiselect (Cinza Neutro + Texto Branco) */
    span[data-baseweb="tag"] {
        background-color: #30363d !important;
        color: white !important;
        border: 1px solid #8b949e;
    }
    span[data-baseweb="tag"] svg {
        fill: white !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. DADOS E LIMPEZA
# ---------------------------------------------------------
@st.cache_data(ttl=0)
def load_data():
    return pd.read_excel("dados_obras_v5.xlsx")

try:
    df_raw = load_data()
except FileNotFoundError:
    st.error("⚠️ Base de dados 'dados_obras_v5.xlsx' não encontrada.")
    st.stop()

# Funções de limpeza e formatação
def clean_currency_brazil(x):
    if isinstance(x, (int, float)): return x
    try:
        s = str(x).replace('R$', '').replace('%', '').replace(' ', '')
        s = s.replace('.', '').replace(',', '.')
        return float(s)
    except: return 0.0

# Limpeza nas colunas monetárias
cols_monetarias = ['Vendido', 'Mat_Real', 'Desp_Real', 'HH_Real_Vlr', 'Impostos', 'Mat_Orc']
for col in cols_monetarias:
    if col in df_raw.columns:
        df_raw[col] = df_raw[col].apply(clean_currency_brazil)

def formatar_valor_ptbr(valor):
    if valor >= 1_000_000:
        val = valor / 1_000_000
        s = f"{val:.1f}".replace(".", ",")
        if s.endswith(",0"): s = s[:-2]
        return f"{s}M"
    elif valor >= 1_000:
        val = valor / 1_000
        s = f"{val:.1f}".replace(".", ",")
        if s.endswith(",0"): s = s[:-2]
        return f"{s}k"
    else:
        return f"{valor:,.0f}".replace(",", ".")

# ---------------------------------------------------------
# 3. LÓGICA DE NEGÓCIO (FIXOS vs OBRAS)
# ---------------------------------------------------------
# Separação dos projetos de custo fixo
IDS_FIXOS = [5009.2025, 5010.2025, 5011.2025]

df_fixos = df_raw[df_raw['Projeto'].isin(IDS_FIXOS)].copy()
df = df_raw[~df_raw['Projeto'].isin(IDS_FIXOS)].copy() # df agora contém APENAS obras produtivas

# Função para calcular custo total (Mat + Desp + HH + Impostos)
def get_custo_total(row):
    return row['Mat_Real'] + row['Desp_Real'] + row['HH_Real_Vlr'] + row['Impostos']

# Totais Globais
custo_fixo_total = df_fixos.apply(get_custo_total, axis=1).sum()
custo_obras_total = df.apply(get_custo_total, axis=1).sum()
valor_vendido_total = df['Vendido'].sum()

# Lucro Líquido Real = Vendas - (Custo Obras + Custo Fixos)
lucro_real_total = valor_vendido_total - (custo_obras_total + custo_fixo_total)

# Dados de Pipeline (Projetos Apresentados)
df_apresentado = df[df['Status'] == 'Apresentado']
valor_apresentado = df_apresentado['Vendido'].sum()

# Margem média do pipeline
def calc_margem_orcada(row):
    custo_est = row['Mat_Orc'] # Estimativa simples baseada no material orçado
    return ((row['Vendido'] - custo_est) / row['Vendido'] * 100) if row['Vendido'] > 0 else 0
margem_media_apresentado = df_apresentado.apply(calc_margem_orcada, axis=1).mean() if not df_apresentado.empty else 0

# --- CÁLCULOS POR PROJETO (GRID) ---
META_MARGEM = 20.0

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

# Aplica cálculos no dataframe principal (Obras)
cols_extras = df.apply(calcular_dados_extras, axis=1)
df['Margem_%'] = cols_extras[0]
df['E_Critico'] = cols_extras[1]
df['HH_Progresso'] = cols_extras[2]

# --- METAS ANUAIS ---
META_VENDAS_ANO = 5000000.00
META_LUCRO_ANO = 1000000.00

# ---------------------------------------------------------
# 4. INTERFACE - CABEÇALHO (ATUALIZADO)
# ---------------------------------------------------------
st.title("Dashboard de Resultados")

# Grid de KPIs atualizado
col1, col2, col3, col4 = st.columns(4)

# CARD 1: META DE VENDAS
pct_v = min((valor_vendido_total / META_VENDAS_ANO), 1.0)
with col1:
    st.markdown(f"""
    <div class="kpi-card" style="border-left: 3px solid #58a6ff;">
        <div>
            <div class="kpi-title">Valor Vendido (Ano)</div>
            <div class="kpi-val">{formatar_valor_ptbr(valor_vendido_total)}</div>
        </div>
        <div class="kpi-sub">
            Meta: {formatar_valor_ptbr(META_VENDAS_ANO)} ({pct_v*100:.0f}%)
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.progress(pct_v)

# CARD 2: META DE LUCRO
pct_l = max(min((lucro_real_total / META_LUCRO_ANO), 1.0), 0.0)
cor_lucro = "#3fb950" if lucro_real_total > 0 else "#da3633"
with col2:
    st.markdown(f"""
    <div class="kpi-card" style="border-left: 3px solid {cor_lucro};">
        <div>
            <div class="kpi-title">Lucro Líquido Real</div>
            <div class="kpi-val" style="color: {cor_lucro}">{formatar_valor_ptbr(lucro_real_total)}</div>
        </div>
        <div class="kpi-sub">
            Meta: {formatar_valor_ptbr(META_LUCRO_ANO)} ({pct_l*100:.0f}%)
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
            <div class="kpi-val">{formatar_valor_ptbr(valor_apresentado)}</div>
        </div>
        <div class="kpi-sub" style="display:flex; justify-content:space-between;">
            <span>Qtd: {len(df_apresentado)}</span>
            <span style="color:#a371f7; font-weight:bold">Mg: {margem_media_apresentado:.1f}%</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# CARD 4: CUSTOS FIXOS
with col4:
    st.markdown(f"""
    <div class="kpi-card" style="border-left: 3px solid #d29922;">
        <div>
            <div class="kpi-title">Custos Estruturais</div>
            <div class="kpi-val">{formatar_valor_ptbr(custo_fixo_total)}</div>
        </div>
        <div class="kpi-sub">
            Ferramental, Comercial e Interno<br>
            <span style="font-style:italic; opacity:0.7">(Já descontado do lucro)</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ---------------------------------------------------------
# 5. BARRA DE FERRAMENTAS E GRID (MANTIDOS)
# ---------------------------------------------------------
col_filtro, col_sort_criterio, col_sort_ordem = st.columns([3, 1, 1])

with col_filtro:
    status_options = ["Não iniciado", "Em andamento", "Finalizado", "Apresentado"]
    status_selecionados = st.multiselect(
        "Filtrar por:", 
        options=status_options, 
        default=status_options 
    )

with col_sort_criterio:
    criterio_sort = st.selectbox(
        "Ordenar por:", 
        ["Projeto", "Valor Vendido", "Margem", "Andamento", "Criticidade"]
    )

with col_sort_ordem:
    direcao_sort = st.selectbox(
        "Ordem:", 
        ["Decrescente", "Crescente"]
    )

# --- LÓGICA DE EXIBIÇÃO ---
if not status_selecionados:
    st.info("Selecione pelo menos um status acima para visualizar os projetos.")
    st.stop() 

df_show = df[df['Status'].isin(status_selecionados)].copy()

# --- LÓGICA DE ORDENAÇÃO ---
df_show['Conclusao_%'] = pd.to_numeric(df_show['Conclusao_%'], errors='coerce').fillna(0)
df_show['Projeto'] = pd.to_numeric(df_show['Projeto'], errors='coerce').fillna(0)

# Define True/False baseado na seleção
eh_crescente = True if "Crescente" in direcao_sort else False

if criterio_sort == "Projeto":
    df_show = df_show.sort_values(by="Projeto", ascending=eh_crescente)
elif criterio_sort == "Valor Vendido":
    df_show = df_show.sort_values(by="Vendido", ascending=eh_crescente)
elif criterio_sort == "Margem":
    df_show = df_show.sort_values(by="Margem_%", ascending=eh_crescente)
elif criterio_sort == "Andamento":
    df_show = df_show.sort_values(by="Conclusao_%", ascending=eh_crescente)
elif criterio_sort == "Criticidade":
    df_show = df_show.sort_values(by="E_Critico", ascending=eh_crescente)

st.write(f"**{len(df_show)}** projetos encontrados")
st.write("")

# ---------------------------------------------------------
# 6. GRID DE CARDS (VISUAL ORIGINAL PRESERVADO)
# ---------------------------------------------------------
cols = st.columns(3)

for i, (index, row) in enumerate(df_show.iterrows()):
    with cols[i % 3]:
        
        pct = int(row['Conclusao_%'])
        status_raw = str(row['Status']).strip()
        
        # Definição das cores do card baseada no status
        if status_raw == "Finalizado":
            cor_tema, bg_badge, color_badge = "#238636", "rgba(35, 134, 54, 0.2)", "#3fb950"
        elif status_raw == "Apresentado":
            cor_tema, bg_badge, color_badge = "#1f6feb", "rgba(31, 111, 235, 0.2)", "#58a6ff"
        elif status_raw == "Em andamento":
            cor_tema, bg_badge, color_badge = "#d29922", "rgba(210, 153, 34, 0.2)", "#e3b341"
        else: 
            cor_tema, bg_badge, color_badge = "#da3633", "rgba(218, 54, 51, 0.2)", "#f85149"

        cor_margem = "#da3633" if row['Margem_%'] < META_MARGEM else "#3fb950"
        
        hh_orc, hh_real = float(row['HH_Orc_Qtd']), float(row['HH_Real_Qtd'])
        pct_horas = (hh_real / hh_orc * 100) if hh_orc > 0 else 0
        cor_horas = "#da3633" if pct_horas > 100 else "#e6edf3"
        
        mat_orc, mat_real = float(row['Mat_Orc']), float(row['Mat_Real'])
        pct_mat = (mat_real / mat_orc * 100) if mat_orc > 0 else 0
        cor_mat = "#da3633" if pct_mat > 100 else "#e6edf3"
        
        valor_formatado = formatar_valor_ptbr(row['Vendido'])
        
        with st.container(border=True):
            st.markdown(f"""
            <div class="tile-header" style="border-left: 3px solid {cor_tema}">
                <div class="tile-title" title="{row['Projeto']} - {row['Descricao']}">{row['Projeto']} - {row['Descricao']}</div>
                <div class="tile-sub">{row['Cliente']} | {row['Cidade']}</div>
            </div>
            <div class="data-strip">
                <div class="data-col"><span class="data-lbl">Valor</span><span class="data-val">{valor_formatado}</span></div>
                <div class="data-col"><span class="data-lbl">Margem</span><span class="data-val" style="color: {cor_margem}">{row['Margem_%']:.0f}%</span></div>
                <div class="data-col"><span class="data-lbl">Horas</span><span class="data-val" style="color: {cor_horas}">{pct_horas:.0f}%</span></div>
                <div class="data-col"><span class="data-lbl">Mat</span><span class="data-val" style="color: {cor_mat}">{pct_mat:.0f}%</span></div>
            </div>
            <div class="tile-footer">
                <div class="progress-track"><div class="progress-fill" style="width: {pct}%; background-color: {cor_tema};"></div></div>
                <div class="footer-row">
                    <span class="badge-status" style="background-color: {bg_badge}; color: {color_badge}">{status_raw}</span>
                    <span class="footer-pct" style="color: {color_badge}">{pct}%</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            col_spacer, col_btn = st.columns([2, 1])
            with col_btn:
                if st.button("Abrir ↗", key=f"btn_{row['Projeto']}", use_container_width=True):
                    st.session_state["projeto_foco"] = row['Projeto']
                    st.switch_page("dashboard_detalhado.py")
