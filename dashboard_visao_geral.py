import streamlit as st
import pandas as pd

# ---------------------------------------------------------
# 1. CONFIGURAÇÃO E ESTILO (Minimalista e Profissional)
# ---------------------------------------------------------
st.set_page_config(page_title="Gestão TE", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    /* Ajustes Gerais */
    .stApp { background-color: #0e1117; }
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
    
    /* KPIs Topo - Estilo 'Stat Box' limpo */
    div[data-testid="metric-container"] {
        background-color: #161b22;
        border: 1px solid #30363d;
        padding: 10px;
        border-radius: 6px;
        transition: 0.2s;
    }
    div[data-testid="metric-container"]:hover {
        border-color: #58a6ff;
    }
    
    /* Título das Metas */
    .meta-label { font-size: 0.8rem; color: #8b949e; margin-bottom: 4px; text-transform: uppercase; letter-spacing: 0.5px;}
    .meta-val { font-size: 1.4rem; font-weight: 700; color: #e6edf3; font-family: monospace;}
    
    /* Ajuste da Tabela */
    [data-testid="stDataFrame"] { width: 100%; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. DADOS (Carregamento e Lógica Financeira)
# ---------------------------------------------------------
@st.cache_data(ttl=0)
def load_data():
    # Substitua pelo seu arquivo real
    try:
        return pd.read_excel("dados_obras_v5.xlsx")
    except:
        return pd.DataFrame() # Retorna vazio se der erro pra não quebrar

df_raw = load_data()

if df_raw.empty:
    st.error("⚠️ Arquivo 'dados_obras_v5.xlsx' não encontrado ou vazio.")
    st.stop()

# Limpeza de moeda
def clean_currency(x):
    if isinstance(x, (int, float)): return x
    try: return float(str(x).replace('R$', '').replace('.', '').replace(',', '.'))
    except: return 0.0

cols_monetarias = ['Vendido', 'Mat_Real', 'Desp_Real', 'HH_Real_Vlr', 'Impostos']
for col in cols_monetarias:
    if col in df_raw.columns:
        df_raw[col] = df_raw[col].apply(clean_currency)

# --- SEPARAÇÃO DE CUSTOS FIXOS vs OBRAS ---
IDS_FIXOS = [5009.2025, 5010.2025, 5011.2025]

# Dataframes separados
df_fixos = df_raw[df_raw['Projeto'].isin(IDS_FIXOS)].copy()
df_obras = df_raw[~df_raw['Projeto'].isin(IDS_FIXOS)].copy() # Apenas projetos de venda

# CÁLCULOS GERAIS
def get_custo_total(df):
    if df.empty: return 0.0
    return (df['Mat_Real'] + df['Desp_Real'] + df['HH_Real_Vlr'] + df['Impostos']).sum()

custo_obras = get_custo_total(df_obras)
custo_fixos = get_custo_total(df_fixos)
venda_total = df_obras['Vendido'].sum()

# Lucro Real (Venda - Custo Obra - Custo Fixo)
lucro_real = venda_total - (custo_obras + custo_fixos)

# Pipeline (Apresentados)
df_apresentado = df_obras[df_obras['Status'] == 'Apresentado']
venda_pipeline = df_apresentado['Vendido'].sum()

# Metas
META_VENDAS = 5000000.00
META_LUCRO = 1000000.00
pct_meta_vendas = (venda_total / META_VENDAS) if META_VENDAS > 0 else 0
pct_meta_lucro = (lucro_real / META_LUCRO) if META_LUCRO > 0 else 0

# Formatação auxiliar
def fmt_m(v): return f"R$ {v/1e6:.2f}M" if v >= 1e6 else f"R$ {v/1e3:.0f}k"

# ---------------------------------------------------------
# 3. SIDEBAR (FILTROS)
# ---------------------------------------------------------
with st.sidebar:
    st.header("🔍 Filtros de Visualização")
    
    # Filtro de Status
    status_opcoes = df_obras['Status'].unique()
    status_sel = st.multiselect(
        "Status do Projeto:",
        options=status_opcoes,
        default=[s for s in status_opcoes if s != "Finalizado"] # Padrão: esconde finalizados pra limpar a tela
    )
    
    st.divider()
    
    # Filtro de Cliente (Opcional, mas útil em listas)
    clientes_opcoes = df_obras['Cliente'].unique()
    clientes_sel = st.multiselect("Cliente:", options=clientes_opcoes, default=clientes_opcoes)

    st.info(f"ℹ️ **Custo Fixo (YTD):** {fmt_m(custo_fixos)}\n\n(Ferramental, Comercial, Interno)")

# ---------------------------------------------------------
# 4. PAINEL SUPERIOR (HEAD UP DISPLAY)
# ---------------------------------------------------------
st.title("Visão Estratégica TE")

# Linha 1: Metas e Resultados Macro
c1, c2, c3, c4 = st.columns(4)

with c1:
    delta_v = f"{(pct_meta_vendas*100):.1f}% da Meta"
    st.metric(label="Valor Vendido (YTD)", value=fmt_m(venda_total), delta=delta_v, delta_color="normal")

with c2:
    delta_l = f"{(pct_meta_lucro*100):.1f}% da Meta"
    st.metric(label="Lucro Líquido Real", value=fmt_m(lucro_real), delta=delta_l)

with c3:
    # Mostra o Pipeline
    st.metric(label="Em Proposta (Apresentado)", value=fmt_m(venda_pipeline), delta=f"{len(df_apresentado)} projetos", delta_color="off")

with c4:
    # Margem média ponderada das obras EM ANDAMENTO
    df_andamento = df_obras[df_obras['Status'] == 'Em andamento']
    if not df_andamento.empty:
        # Margem simples média para o KPI rápido
        custo_and = df_andamento['Mat_Real'] + df_andamento['Desp_Real'] + df_andamento['HH_Real_Vlr'] + df_andamento['Impostos']
        margem_med = ((df_andamento['Vendido'].sum() - custo_and.sum()) / df_andamento['Vendido'].sum()) * 100
    else:
        margem_med = 0
    st.metric(label="Margem Atual (Obras)", value=f"{margem_med:.1f}%")

st.divider()

# ---------------------------------------------------------
# 5. TABELA DE GESTÃO (DATAFRAME INTERATIVO)
# ---------------------------------------------------------
# Preparação dos dados para a tabela
# Filtra baseado na sidebar
df_show = df_obras[
    (df_obras['Status'].isin(status_sel)) & 
    (df_obras['Cliente'].isin(clientes_sel))
].copy()

# Recalcula margem linha a linha para exibição
def calc_live_margin(row):
    custo = row['Mat_Real'] + row['Desp_Real'] + row['HH_Real_Vlr'] + row['Impostos']
    return ((row['Vendido'] - custo) / row['Vendido'] * 100) if row['Vendido'] > 0 else 0

df_show['Margem_Real_%'] = df_show.apply(calc_live_margin, axis=1)

# Seleciona e renomeia colunas para ficar bonito
cols_view = ['Projeto', 'Descricao', 'Cliente', 'Status', 'Vendido', 'Margem_Real_%', 'Conclusao_%']
df_display = df_show[cols_view].copy()

# Configuração da Tabela (O Pulo do Gato Visual)
st.dataframe(
    df_display,
    column_config={
        "Projeto": st.column_config.NumberColumn(
            "ID", format="%d", width="small"
        ),
        "Descricao": st.column_config.TextColumn(
            "Projeto / Obra", width="large"
        ),
        "Cliente": st.column_config.TextColumn(
            "Cliente", width="medium"
        ),
        "Status": st.column_config.SelectboxColumn(
            "Status", width="medium",
            options=["Em andamento", "Finalizado", "Apresentado", "Paralisado"],
            required=True
        ),
        "Vendido": st.column_config.NumberColumn(
            "Valor (R$)", format="R$ %.0f", width="medium"
        ),
        "Margem_Real_%": st.column_config.ProgressColumn(
            "Margem Real", 
            format="%.1f%%", 
            min_value=-10, max_value=40, # Ajuste conforme sua realidade (ex: negativo fica vermelho auto)
            width="medium"
        ),
        "Conclusao_%": st.column_config.ProgressColumn(
            "Avanço Físico", 
            format="%d%%", 
            min_value=0, max_value=100,
            width="medium"
        )
    },
    use_container_width=True,
    hide_index=True,
    height=500 # Tabela alta para ver bastante coisa
)

# ---------------------------------------------------------
# 6. GRÁFICOS DE APOIO (OPCIONAL - RODAPÉ)
# ---------------------------------------------------------
if not df_show.empty:
    st.caption("Visão Gráfica Rápida")
    c_chart1, c_chart2 = st.columns(2)
    
    with c_chart1:
        # Gráfico de Barras simples: Venda por Status
        chart_data = df_show.groupby("Status")["Vendido"].sum().reset_index()
        st.bar_chart(chart_data, x="Status", y="Vendido", color="#1f6feb", height=200)
    
    with c_chart2:
        # Scatter Plot: Margem vs Venda (Onde estão os riscos?)
        st.scatter_chart(
            df_show, 
            x="Margem_Real_%", 
            y="Vendido", 
            color="Status", 
            size="Vendido", # Bolinha maior = projeto maior
            height=200
        )
