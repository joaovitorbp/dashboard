import streamlit as st
import pandas as pd
import textwrap

# ---------------------------------------------------------
# 1. CONFIGURAÇÃO VISUAL (CSS - MODO LISTA)
# ---------------------------------------------------------
st.markdown("""
<style>
    .stApp {background-color: #0e1117;}
    .block-container {padding-top: 2rem;}

    /* --- CONTAINER DA LINHA (ROW) --- */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 0px !important;
        transition: all 0.2s;
    }
    [data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color: #7d8590;
        background-color: #1c2128;
    }

    /* --- TIPOGRAFIA DA LISTA --- */
    .row-title {
        font-family: "Source Sans Pro", sans-serif;
        color: white;
        font-weight: 700;
        font-size: 0.95rem;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        margin-bottom: 2px;
    }
    .row-sub {
        font-family: "Source Sans Pro", sans-serif;
        color: #8b949e;
        font-size: 0.75rem;
        display: flex;
        align-items: center;
        gap: 6px;
    }

    /* --- BADGE DE STATUS (Pequeno) --- */
    .mini-badge {
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.6rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        white-space: nowrap;
    }

    /* --- MÉTRICAS (Compactas) --- */
    .metric-box {
        display: flex;
        flex-direction: column;
        justify-content: center;
        height: 100%;
    }
    .metric-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 0.8rem;
        margin-bottom: 2px;
    }
    .lbl { color: #8b949e; font-size: 0.7rem; margin-right: 8px; }
    .val { color: #e6edf3; font-weight: 600; }

    /* --- PROGRESSO --- */
    .prog-box {
        display: flex;
        flex-direction: column;
        justify-content: center;
        height: 100%;
        padding-right: 10px;
    }
    .prog-track {
        background-color: #30363d;
        height: 6px;
        width: 100%;
        border-radius: 3px;
        overflow: hidden;
        margin-top: 4px;
    }
    .prog-fill { height: 100%; border-radius: 3px; }
    .prog-text { font-size: 0.75rem; color: #8b949e; display: flex; justify-content: space-between; }

    /* --- BOTÃO (Compacto) --- */
    div[data-testid="stVerticalBlockBorderWrapper"] button {
        background-color: transparent;
        color: #58a6ff;
        border: 1px solid #30363d;
        border-radius: 6px;
        height: 35px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-top: 5px; /* Alinha verticalmente com o resto */
    }
    div[data-testid="stVerticalBlockBorderWrapper"] button:hover {
        background-color: #1f6feb;
        color: white;
        border-color: #1f6feb;
    }

    div[data-testid="column"] { padding: 0 5px; }
    
    /* Remove padding vertical extra dentro dos containers */
    .element-container { margin-bottom: 0px !important; }

    /* KPIs Globais */
    .big-kpi {
        background-color: #161b22;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #30363d;
        text-align: center;
    }
    .big-kpi-val { font-size: 1.8rem; font-weight: bold; color: white; font-family: "Source Sans Pro", sans-serif; }
    .big-kpi-lbl { font-size: 0.9rem; color: #8b949e; font-family: "Source Sans Pro", sans-serif; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. CARREGAR DADOS
# ---------------------------------------------------------
@st.cache_data
def load_data():
    return pd.read_excel("dados_obras_v5.xlsx")

try:
    df = load_data()
except FileNotFoundError:
    st.error("⚠️ Base de dados 'dados_obras_v5.xlsx' não encontrada.")
    st.stop()

# ---------------------------------------------------------
# 3. LÓGICA DE CÁLCULO
# ---------------------------------------------------------
META_MARGEM = 20.0

def calcular_dados_extras(row):
    custo = row['Mat_Real'] + row['Desp_Real'] + row['HH_Real_Vlr'] + row['Impostos']
    lucro = row['Vendido'] - custo
    margem = (lucro / row['Vendido'] * 100) if row['Vendido'] > 0 else 0
    
    hh_perc = (row['HH_Real_Qtd'] / row['HH_Orc_Qtd'] * 100) if row['HH_Orc_Qtd'] > 0 else 0
    fisico = row['Conclusao_%']
    
    critico = False
    if margem < META_MARGEM or hh_perc > (fisico + 10):
        critico = True
        
    return pd.Series([margem, critico])

df[['Margem_%', 'E_Critico']] = df.apply(calcular_dados_extras, axis=1)

# ---------------------------------------------------------
# 4. INTERFACE
# ---------------------------------------------------------
st.title("🏢 Painel de Controle")

# KPIs Globais
k1, k2, k3, k4 = st.columns(4)
k1.markdown(f"<div class='big-kpi'><div class='big-kpi-lbl'>Total Carteira</div><div class='big-kpi-val'>R$ {df['Vendido'].sum()/1e6:.1f}M</div></div>", unsafe_allow_html=True)
k2.markdown(f"<div class='big-kpi'><div class='big-kpi-lbl'>Faturamento</div><div class='big-kpi-val'>R$ {df['Faturado'].sum()/1e6:.1f}M</div></div>", unsafe_allow_html=True)
k3.markdown(f"<div class='big-kpi'><div class='big-kpi-lbl'>Obras Ativas</div><div class='big-kpi-val'>{len(df[df['Status']=='Em andamento'])}</div></div>", unsafe_allow_html=True)
k4.markdown(f"<div class='big-kpi'><div class='big-kpi-lbl'>Margem Média</div><div class='big-kpi-val'>{df['Margem_%'].mean():.1f}%</div></div>", unsafe_allow_html=True)

st.divider()

# Filtros
status_options = ["Todas", "Não iniciado", "Em andamento", "Apresentado", "Finalizado", "🚨 Críticas"]
filtro_status = st.radio("Visualização:", status_options, horizontal=True)

df_show = df.copy()

if filtro_status == "Não iniciado": 
    df_show = df_show[df_show['Status'].str.strip().str.lower() == 'não iniciado']
elif filtro_status == "Em andamento":
    df_show = df_show[df_show['Status'] == 'Em andamento']
elif filtro_status == "Apresentado":
    df_show = df_show[df_show['Status'] == 'Apresentado']
elif filtro_status == "Finalizado":
    df_show = df_show[df_show['Status'] == 'Finalizado']
elif filtro_status == "🚨 Críticas":
    df_show = df_show[df_show['E_Critico'] == True]

st.write(f"**{len(df_show)}** projetos encontrados")

# Cabeçalho da Lista (Opcional, para dar cara de tabela)
h1, h2, h3, h4, h5, h6 = st.columns([0.1, 2.5, 1.5, 1.5, 2, 1])
h2.caption("PROJETO / CLIENTE")
h3.caption("FINANCEIRO")
h4.caption("EFICIÊNCIA")
h5.caption("PROGRESSO")
h6.caption("AÇÃO")

# ---------------------------------------------------------
# 5. LISTA DE PROJETOS (LAYOUT HORIZONTAL)
# ---------------------------------------------------------
for index, row in df_show.iterrows():
    
    # --- CÁLCULOS E CORES ---
    pct = int(row['Conclusao_%'])
    status_raw = str(row['Status']).strip()
    
    if row['HH_Orc_Qtd'] > 0: pct_horas = (row['HH_Real_Qtd'] / row['HH_Orc_Qtd']) * 100
    else: pct_horas = 0
        
    if row['Mat_Orc'] > 0: pct_mat = (row['Mat_Real'] / row['Mat_Orc']) * 100
    else: pct_mat = 0

    # Cores de Status
    if status_raw == "Finalizado":
        cor_tema = "#238636"
        bg_badge = "rgba(35, 134, 54, 0.2)"
        color_badge = "#3fb950"
    elif status_raw == "Apresentado":
        cor_tema = "#1f6feb"
        bg_badge = "rgba(31, 111, 235, 0.2)"
        color_badge = "#58a6ff"
    elif status_raw == "Em andamento":
        cor_tema = "#d29922"
        bg_badge = "rgba(210, 153, 34, 0.2)"
        color_badge = "#e3b341"
    else: 
        cor_tema = "#da3633"
        bg_badge = "rgba(218, 54, 51, 0.2)"
        color_badge = "#f85149"

    cor_margem = "#da3633" if row['Margem_%'] < META_MARGEM else "#3fb950"
    cor_horas = "#da3633" if pct_horas > 100 else "#e6edf3"
    cor_mat = "#da3633" if pct_mat > 100 else "#e6edf3"

    # --- ROW CONTAINER ---
    with st.container(border=True):
        
        # Colunas: 
        # C1: Faixa Colorida (Status)
        # C2: Info (Nome, Cliente, Badge)
        # C3: Financeiro (Valor, Margem)
        # C4: Eficiência (%Horas, %Mat)
        # C5: Progresso (Barra)
        # C6: Botão
        c_strip, c_info, c_fin, c_efi, c_prog, c_btn = st.columns([0.1, 2.5, 1.5, 1.5, 2, 1], vertical_alignment="center")

        # Coluna 1: Faixa lateral
        with c_strip:
            st.markdown(f"<div style='height: 45px; width: 4px; background-color: {cor_tema}; border-radius: 2px;'></div>", unsafe_allow_html=True)

        # Coluna 2: Informações Principais
        with c_info:
            st.markdown(f"""
                <div class="row-title" title="{row['Descricao']}">{row['Projeto']}</div>
                <div class="row-sub">
                    <span>{row['Cliente']}</span>
                    <span style="color: #30363d;">|</span>
                    <span class="mini-badge" style="background-color: {bg_badge}; color: {color_badge};">{status_raw}</span>
                </div>
            """, unsafe_allow_html=True)

        # Coluna 3: Financeiro
        with c_fin:
            st.markdown(f"""
                <div class="metric-box">
                    <div class="metric-row"><span class="lbl">VAL</span> <span class="val">R$ {row['Vendido']/1000:,.0f}k</span></div>
                    <div class="metric-row"><span class="lbl">MRG</span> <span class="val" style="color: {cor_margem}">{row['Margem_%']:.1f}%</span></div>
                </div>
            """, unsafe_allow_html=True)

        # Coluna 4: Eficiência
        with c_efi:
            st.markdown(f"""
                <div class="metric-box">
                    <div class="metric-row"><span class="lbl">HRS</span> <span class="val" style="color: {cor_horas}">{pct_horas:.0f}%</span></div>
                    <div class="metric-row"><span class="lbl">MAT</span> <span class="val" style="color: {cor_mat}">{pct_mat:.0f}%</span></div>
                </div>
            """, unsafe_allow_html=True)
            
        # Coluna 5: Barra de Progresso
        with c_prog:
            st.markdown(f"""
                <div class="prog-box">
                    <div class="prog-text"><span>Avanço</span> <span style="color:{color_badge}; font-weight:bold;">{pct}%</span></div>
                    <div class="prog-track"><div class="prog-fill" style="width: {pct}%; background-color: {cor_tema};"></div></div>
                </div>
            """, unsafe_allow_html=True)

        # Coluna 6: Botão
        with c_btn:
            if st.button("Ver ➜", key=f"btn_{row['Projeto']}", use_container_width=True):
                st.session_state["projeto_foco"] = row['Projeto']
                st.switch_page("dashboard_detalhado.py")
