import streamlit as st
import pandas as pd
import textwrap

# ---------------------------------------------------------
# 1. CONFIGURAÇÃO VISUAL
# ---------------------------------------------------------
st.markdown("""
<style>
    .stApp {background-color: #0e1117;}
    .block-container {padding-top: 2rem;}

    /* Cards */
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

    /* Header */
    .tile-header { padding: 15px 15px 10px 15px; }
    .tile-title {
        color: white; font-family: "Source Sans Pro", sans-serif;
        font-weight: 700; font-size: 1rem;
        white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
        margin-bottom: 2px;
    }
    .tile-sub { color: #8b949e; font-size: 0.75rem; font-family: "Source Sans Pro", sans-serif; }

    /* Metrics Strip */
    .data-strip {
        background-color: #0d1117; border-top: 1px solid #21262d; border-bottom: 1px solid #21262d;
        padding: 10px 15px; display: flex; justify-content: space-between; align-items: center;
    }
    .data-col { display: flex; flex-direction: column; align-items: center; width: 25%; }
    .data-col:not(:last-child) { border-right: 1px solid #30363d; }
    .data-lbl { font-size: 0.6rem; color: #8b949e; text-transform: uppercase; margin-bottom: 2px; }
    .data-val { font-size: 0.85rem; font-weight: 700; color: #e6edf3; font-family: "Source Sans Pro", sans-serif; }

    /* Footer */
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

    /* BOTÃO PEQUENO */
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

    /* KPIs Globais */
    .big-kpi {
        background-color: #161b22; padding: 15px; border-radius: 8px;
        border: 1px solid #30363d; text-align: center;
    }
    .big-kpi-val { font-size: 1.8rem; font-weight: bold; color: white; font-family: "Source Sans Pro", sans-serif; }
    .big-kpi-lbl { font-size: 0.9rem; color: #8b949e; font-family: "Source Sans Pro", sans-serif; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. DADOS E LIMPEZA
# ---------------------------------------------------------
@st.cache_data
def load_data():
    return pd.read_excel("dados_obras_v5.xlsx")

try:
    df = load_data()
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

# Limpeza das colunas principais
df['Vendido'] = df['Vendido'].apply(clean_currency_brazil)
df['Mat_Real'] = df['Mat_Real'].apply(clean_currency_brazil)

# --- NOVA FUNÇÃO DE FORMATAÇÃO INTELIGENTE (BR) ---
def formatar_valor_ptbr(valor):
    if valor >= 1_000_000:
        val = valor / 1_000_000
        # Ex: 1.5M (com 1 casa decimal) ou 12M (se for redondo)
        s = f"{val:.1f}".replace(".", ",")
        # Remove ,0 se existir (ex: 12,0M vira 12M)
        if s.endswith(",0"): s = s[:-2]
        return f"{s}M"
    elif valor >= 1_000:
        val = valor / 1_000
        s = f"{val:.1f}".replace(".", ",")
        if s.endswith(",0"): s = s[:-2]
        return f"{s}k"
    else:
        # Menor que 1000, mostra normal (ex: 500)
        return f"{valor:,.0f}".replace(",", ".")

# ---------------------------------------------------------
# 3. CÁLCULOS
# ---------------------------------------------------------
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
    if margem < META_MARGEM or hh_perc > (fisico + 10):
        critico = True
    return pd.Series([margem, critico, hh_perc])

cols_extras = df.apply(calcular_dados_extras, axis=1)
df['Margem_%'] = cols_extras[0]
df['E_Critico'] = cols_extras[1]
df['HH_Progresso'] = cols_extras[2]

# ---------------------------------------------------------
# 4. INTERFACE
# ---------------------------------------------------------
st.title("🏢 Painel de Controle")

# KPIs Globais (Usando a nova formatação)
k1, k2, k3, k4 = st.columns(4)
total_cart = df['Vendido'].sum()
total_fat = df['Faturado'].apply(clean_currency_brazil).sum()

k1.markdown(f"<div class='big-kpi'><div class='big-kpi-lbl'>Total Carteira</div><div class='big-kpi-val'>R$ {formatar_valor_ptbr(total_cart)}</div></div>", unsafe_allow_html=True)
k2.markdown(f"<div class='big-kpi'><div class='big-kpi-lbl'>Faturamento</div><div class='big-kpi-val'>R$ {formatar_valor_ptbr(total_fat)}</div></div>", unsafe_allow_html=True)
k3.markdown(f"<div class='big-kpi'><div class='big-kpi-lbl'>Obras Ativas</div><div class='big-kpi-val'>{len(df[df['Status']=='Em andamento'])}</div></div>", unsafe_allow_html=True)
k4.markdown(f"<div class='big-kpi'><div class='big-kpi-lbl'>Margem Média</div><div class='big-kpi-val'>{df['Margem_%'].mean():.1f}%</div></div>", unsafe_allow_html=True)

st.divider()

# --- CONTROLES ---
col_filtro, col_sort = st.columns([3, 1])
with col_filtro:
    status_options = ["Todas", "Não iniciado", "Em andamento", "Apresentado", "Finalizado"]
    filtro_status = st.radio("Visualização:", status_options, horizontal=True)

with col_sort:
    opcoes_ordem = [
        "Padrão", 
        "Valor ⬇️ (Maior ➜ Menor)", 
        "Valor ⬆️ (Menor ➜ Maior)",
        "Margem ⬇️ (Maior ➜ Menor)", 
        "Margem ⬆️ (Menor ➜ Maior)",
        "Andamento ⬇️ (Maior ➜ Menor)",
        "Andamento ⬆️ (Menor ➜ Maior)",
        "Criticidade (Críticos 1º)"
    ]
    ordenar_por = st.selectbox("Ordenar por:", opcoes_ordem)

# --- FILTRAGEM ---
df_show = df.copy()

if filtro_status == "Não iniciado": 
    df_show = df_show[df_show['Status'].str.strip().str.lower() == 'não iniciado']
elif filtro_status == "Em andamento":
    df_show = df_show[df_show['Status'] == 'Em andamento']
elif filtro_status == "Apresentado":
    df_show = df_show[df_show['Status'] == 'Apresentado']
elif filtro_status == "Finalizado":
    df_show = df_show[df_show['Status'] == 'Finalizado']

# --- ORDENAÇÃO ---
df_show['Conclusao_%'] = pd.to_numeric(df_show['Conclusao_%'], errors='coerce').fillna(0)

if ordenar_por == "Valor ⬇️ (Maior ➜ Menor)":
    df_show = df_show.sort_values(by="Vendido", ascending=False)
elif ordenar_por == "Valor ⬆️ (Menor ➜ Maior)":
    df_show = df_show.sort_values(by="Vendido", ascending=True)

elif ordenar_por == "Margem ⬇️ (Maior ➜ Menor)":
    df_show = df_show.sort_values(by="Margem_%", ascending=False)
elif ordenar_por == "Margem ⬆️ (Menor ➜ Maior)":
    df_show = df_show.sort_values(by="Margem_%", ascending=True)

elif ordenar_por == "Andamento ⬇️ (Maior ➜ Menor)":
    df_show = df_show.sort_values(by="Conclusao_%", ascending=False)
elif ordenar_por == "Andamento ⬆️ (Menor ➜ Maior)":
    df_show = df_show.sort_values(by="Conclusao_%", ascending=True)

elif ordenar_por == "Criticidade (Críticos 1º)":
    df_show = df_show.sort_values(by="E_Critico", ascending=False)

st.write(f"**{len(df_show)}** projetos encontrados")
st.write("")

# ---------------------------------------------------------
# 5. GRID DE CARDS
# ---------------------------------------------------------
cols = st.columns(3)

for i, (index, row) in enumerate(df_show.iterrows()):
    with cols[i % 3]:
        
        pct = int(row['Conclusao_%'])
        status_raw = str(row['Status']).strip()
        
        # Cores
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
        
        # --- APLICAÇÃO DA NOVA FORMATAÇÃO AQUI ---
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
