import streamlit as st
import pandas as pd

# ---------------------------------------------------------
# 1. CONFIGURAÇÃO VISUAL (CSS PREMIUM)
# ---------------------------------------------------------
st.markdown("""
<style>
    .stApp {background-color: #0e1117;}
    .block-container {padding-top: 2rem;}

    /* --- ESTILO DO CONTAINER DO CARD --- */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #161b22; /* Fundo mais escuro */
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 0px !important; /* Removemos padding padrão para controlar via CSS interno */
        transition: transform 0.2s, border-color 0.2s;
    }
    [data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color: #58a6ff; /* Borda azul ao passar o mouse */
        transform: translateY(-2px); /* Leve flutuação */
    }

    /* --- CABEÇALHO DO CARD --- */
    .card-header-box {
        padding: 15px 15px 10px 15px;
        border-bottom: 1px solid #21262d;
    }
    .project-title {
        color: white;
        font-weight: 700;
        font-size: 1rem;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        margin-bottom: 4px;
    }
    .project-sub {
        color: #8b949e;
        font-size: 0.75rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    /* --- BADGE DE STATUS --- */
    .status-badge {
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.65rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* --- CORPO DO CARD (MÉTRICAS) --- */
    .card-body-box {
        padding: 15px;
    }
    .metric-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 10px;
        margin-bottom: 15px;
    }
    .metric-item {
        background-color: #0d1117;
        padding: 8px;
        border-radius: 6px;
        text-align: center;
        border: 1px solid #30363d;
    }
    .metric-lbl {
        font-size: 0.65rem;
        color: #8b949e;
        text-transform: uppercase;
        margin-bottom: 2px;
    }
    .metric-val {
        font-family: 'Courier New', Courier, monospace; /* Fonte técnica */
        font-size: 0.95rem;
        font-weight: 700;
        color: #e6edf3;
    }

    /* --- BARRA DE PROGRESSO CUSTOMIZADA --- */
    .progress-container {
        width: 100%;
        background-color: #21262d;
        border-radius: 4px;
        height: 6px;
        margin-top: 5px;
        overflow: hidden;
    }
    .progress-bar {
        height: 100%;
        border-radius: 4px;
        transition: width 0.5s ease-in-out;
    }
    .progress-txt {
        font-size: 0.7rem;
        color: #8b949e;
        margin-bottom: 4px;
        display: flex;
        justify-content: space-between;
    }

    /* --- BOTÃO ESTILIZADO (Rodapé) --- */
    div[data-testid="stVerticalBlockBorderWrapper"] button {
        background-color: transparent;
        color: #58a6ff;
        border: none;
        border-top: 1px solid #30363d;
        border-radius: 0 0 8px 8px; /* Arredonda só em baixo */
        width: 100%;
        padding: 10px;
        font-size: 0.85rem;
        font-weight: 600;
        transition: background 0.2s;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] button:hover {
        background-color: #1f6feb20; /* Azul bem clarinho no fundo */
        color: #58a6ff;
    }
    
    /* Remove padding interno das colunas do Streamlit */
    div[data-testid="column"] { padding: 0 8px; }

    /* KPIs Globais */
    .big-kpi {
        background-color: #161b22;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #30363d;
        text-align: center;
    }
    .big-kpi-val { font-size: 1.8rem; font-weight: bold; color: white; }
    .big-kpi-lbl { font-size: 0.9rem; color: #8b949e; }
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
st.markdown("Visão consolidada do portfólio de obras.")

# KPIs Globais
k1, k2, k3, k4 = st.columns(4)
k1.markdown(f"<div class='big-kpi'><div class='big-kpi-lbl'>Total Carteira</div><div class='big-kpi-val'>R$ {df['Vendido'].sum()/1e6:.1f}M</div></div>", unsafe_allow_html=True)
k2.markdown(f"<div class='big-kpi'><div class='big-kpi-lbl'>Faturamento</div><div class='big-kpi-val'>R$ {df['Faturado'].sum()/1e6:.1f}M</div></div>", unsafe_allow_html=True)
k3.markdown(f"<div class='big-kpi'><div class='big-kpi-lbl'>Obras Ativas</div><div class='big-kpi-val'>{len(df[df['Status']=='Em andamento'])}</div></div>", unsafe_allow_html=True)
k4.markdown(f"<div class='big-kpi'><div class='big-kpi-lbl'>Margem Média</div><div class='big-kpi-val'>{df['Margem_%'].mean():.1f}%</div></div>", unsafe_allow_html=True)

st.divider()

# Filtros
filtro_status = st.radio("Visualização:", ["Todas", "Em andamento", "Finalizadas", "🚨 Críticas"], horizontal=True)

df_show = df.copy()
if filtro_status == "Em andamento": df_show = df_show[df_show['Status'] == 'Em andamento']
elif filtro_status == "Finalizadas": df_show = df_show[df_show['Status'] == 'Finalizado']
elif filtro_status == "🚨 Críticas": df_show = df_show[df_show['E_Critico'] == True]

st.write(f"**{len(df_show)}** projetos encontrados")
st.write("")

# ---------------------------------------------------------
# 5. GRID DE CARDS (REWORK)
# ---------------------------------------------------------
cols = st.columns(3)

for index, row in df_show.iterrows():
    with cols[index % 3]:
        
        # Definições Visuais
        pct = int(row['Conclusao_%'])
        
        # Cores e Status
        if pct >= 100:
            cor_tema = "#238636" # Verde
            txt_status = "CONCLUÍDO"
            bg_badge = "rgba(35, 134, 54, 0.2)"
            color_badge = "#3fb950"
        elif pct > 50:
            cor_tema = "#1f6feb" # Azul
            txt_status = "EM ANDAMENTO"
            bg_badge = "rgba(31, 111, 235, 0.2)"
            color_badge = "#58a6ff"
        else:
            cor_tema = "#8957e5" # Roxo
            txt_status = "INÍCIO"
            bg_badge = "rgba(137, 87, 229, 0.2)"
            color_badge = "#d2a8ff"

        cor_margem = "#da3633" if row['Margem_%'] < META_MARGEM else "#3fb950"
        
        # --- CARD CONTAINER ---
        with st.container(border=True):
            
            # PARTE 1: Cabeçalho (Título + Badge)
            # Usamos CSS flexbox inline para alinhar Cliente e Status
            html_header = f"""
            <div class="card-header-box" style="border-left: 4px solid {cor_tema};">
                <div class="project-title" title="{row['Projeto']} - {row['Descricao']}">{row['Projeto']} - {row['Descricao']}</div>
                <div class="project-sub">
                    <span>🏢 {row['Cliente']}</span>
                    <span class="status-badge" style="background-color: {bg_badge}; color: {color_badge}; border: 1px solid {cor_tema};">
                        {txt_status}
                    </span>
                </div>
            </div>
            """
            st.markdown(html_header, unsafe_allow_html=True)
            
            # PARTE 2: Corpo (Métricas + Progresso)
            html_body = f"""
            <div class="card-body-box">
                <div class="metric-grid">
                    <div class="metric-item">
                        <div class="metric-lbl">VALOR TOTAL</div>
                        <div class="metric-val">R$ {row['Vendido']/1000:,.0f}k</div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-lbl">MARGEM REAL</div>
                        <div class="metric-val" style="color: {cor_margem};">{row['Margem_%']:.1f}%</div>
                    </div>
                </div>

                <div class="progress-txt">
                    <span>Avanço Físico</span>
                    <span style="color: {color_badge}; font-weight:bold;">{pct}%</span>
                </div>
                <div class="progress-container">
                    <div class="progress-bar" style="width: {pct}%; background-color: {cor_tema};"></div>
                </div>
            </div>
            """
            st.markdown(html_body, unsafe_allow_html=True)

            # PARTE 3: Botão de Ação (Full Width no rodapé)
            if st.button("ABRIR DASHBOARD DETALHADO", key=f"btn_{row['Projeto']}", use_container_width=True):
                st.session_state["projeto_foco"] = row['Projeto']
                st.switch_page("dashboard_detalhado.py")
