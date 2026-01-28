import streamlit as st
import pandas as pd

# ---------------------------------------------------------
# 1. CONFIGURAÇÃO VISUAL (CSS)
# ---------------------------------------------------------
st.markdown("""
<style>
    .stApp {background-color: #0e1117;}
    .block-container {padding-top: 2rem;}

    /* --- CONTAINER DO CARD --- */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 6px; /* Cantos levemente arredondados */
        padding: 0px !important;
        transition: all 0.2s ease-in-out;
    }
    [data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color: #58a6ff;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        transform: translateY(-2px);
    }

    /* --- CABEÇALHO --- */
    .card-header-box {
        padding: 15px 15px 10px 15px;
        border-bottom: 1px solid #21262d;
    }
    .project-title {
        color: white;
        font-family: "Source Sans Pro", sans-serif;
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
        font-weight: 400;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    /* --- BADGE DE STATUS (Sem emojis) --- */
    .status-badge {
        padding: 2px 8px;
        border-radius: 10px;
        font-size: 0.6rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* --- CORPO (MÉTRICAS) --- */
    .card-body-box {
        padding: 15px;
    }
    .metric-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 12px;
        margin-bottom: 15px;
    }
    .metric-item {
        background-color: #0d1117; /* Fundo mais escuro para destaque */
        padding: 8px;
        border-radius: 4px;
        border: 1px solid #30363d;
    }
    .metric-lbl {
        font-size: 0.65rem;
        color: #8b949e;
        text-transform: uppercase;
        margin-bottom: 2px;
        font-family: "Source Sans Pro", sans-serif;
    }
    .metric-val {
        font-size: 0.95rem;
        font-weight: 600;
        color: #e6edf3;
        font-family: "Source Sans Pro", sans-serif;
    }

    /* --- BARRA DE PROGRESSO --- */
    .progress-container {
        width: 100%;
        background-color: #21262d;
        border-radius: 2px;
        height: 4px; /* Mais fina */
        margin-top: 6px;
        overflow: hidden;
    }
    .progress-bar {
        height: 100%;
        border-radius: 2px;
    }
    .progress-txt {
        font-size: 0.7rem;
        color: #8b949e;
        margin-bottom: 2px;
        display: flex;
        justify-content: space-between;
    }

    /* --- BOTÃO DISCRETO (Rodapé) --- */
    div[data-testid="stVerticalBlockBorderWrapper"] button {
        background-color: transparent;
        color: #7d8590; /* Cinza discreto */
        border: none;
        border-top: 1px solid #21262d; /* Linha divisória muito sutil */
        border-radius: 0 0 6px 6px;
        width: 100%;
        padding: 8px;
        font-size: 0.8rem;
        font-weight: 400;
        transition: all 0.2s;
        font-family: "Source Sans Pro", sans-serif;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] button:hover {
        background-color: #1f242c;
        color: #58a6ff; /* Azul ao passar o mouse */
    }
    
    div[data-testid="column"] { padding: 0 8px; }

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
st.markdown("Visão consolidada do portfólio de obras.")

# KPIs Globais (Sem quebra de linha no HTML)
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
# 5. GRID DE CARDS
# ---------------------------------------------------------
cols = st.columns(3)

for index, row in df_show.iterrows():
    with cols[index % 3]:
        
        # Variáveis Visuais
        pct = int(row['Conclusao_%'])
        
        if pct >= 100:
            cor_tema = "#238636" # Verde
            txt_status = "Concluído"
            bg_badge = "rgba(35, 134, 54, 0.15)"
            color_badge = "#3fb950"
        elif pct > 50:
            cor_tema = "#1f6feb" # Azul
            txt_status = "Em Andamento"
            bg_badge = "rgba(31, 111, 235, 0.15)"
            color_badge = "#58a6ff"
        else:
            cor_tema = "#8957e5" # Roxo
            txt_status = "Início"
            bg_badge = "rgba(137, 87, 229, 0.15)"
            color_badge = "#d2a8ff"

        cor_margem = "#da3633" if row['Margem_%'] < META_MARGEM else "#3fb950"
        
        # --- CARD ---
        with st.container(border=True):
            
            # HEADER (Sem Emojis, com Empresa | Cidade)
            html_header = [
                f'<div class="card-header-box" style="border-left: 3px solid {cor_tema};">',
                f'<div class="project-title" title="{row["Projeto"]} - {row["Descricao"]}">{row["Projeto"]} - {row["Descricao"]}</div>',
                '<div class="project-sub">',
                f'<span>{row["Cliente"]} | {row["Cidade"]}</span>', # <--- MUDANÇA AQUI
                f'<span class="status-badge" style="background-color: {bg_badge}; color: {color_badge};">{txt_status}</span>',
                '</div>',
                '</div>'
            ]
            st.markdown("".join(html_header), unsafe_allow_html=True)
            
            # BODY
            html_body = [
                '<div class="card-body-box">',
                '<div class="metric-grid">',
                '<div class="metric-item">',
                '<div class="metric-lbl">Valor Total</div>',
                f'<div class="metric-val">R$ {row["Vendido"]/1000:,.0f}k</div>',
                '</div>',
                '<div class="metric-item">',
                '<div class="metric-lbl">Margem Real</div>',
                f'<div class="metric-val" style="color: {cor_margem};">{row["Margem_%"]:.1f}%</div>',
                '</div>',
                '</div>',
                '<div class="progress-txt">',
                '<span>Avanço Físico</span>',
                f'<span style="color: {color_badge}; font-weight:600;">{pct}%</span>',
                '</div>',
                '<div class="progress-container">',
                f'<div class="progress-bar" style="width: {pct}%; background-color: {cor_tema};"></div>',
                '</div>',
                '</div>'
            ]
            st.markdown("".join(html_body), unsafe_allow_html=True)

            # BOTÃO (Nomenclatura Nova e Discreto)
            if st.button("Acessar Detalhes", key=f"btn_{row['Projeto']}", use_container_width=True):
                st.session_state["projeto_foco"] = row['Projeto']
                st.switch_page("dashboard_detalhado.py")
