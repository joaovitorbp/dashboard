import streamlit as st
import pandas as pd
import textwrap

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
        border-radius: 12px;
        padding: 0px !important;
        transition: all 0.2s ease-in-out;
    }
    [data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color: #7d8590;
        box-shadow: 0 8px 24px rgba(0,0,0,0.4);
        transform: translateY(-3px);
    }

    /* --- CABEÇALHO --- */
    .card-header-stack {
        padding: 16px 16px 12px 16px;
        border-bottom: 1px solid #21262d;
        display: flex;
        flex-direction: column;
        gap: 6px;
    }
    .project-title {
        color: white;
        font-family: "Source Sans Pro", sans-serif;
        font-weight: 700;
        font-size: 1.1rem;
        line-height: 1.2;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .client-sub {
        font-size: 0.85rem;
        color: #8b949e;
        display: flex;
        align-items: center;
        gap: 8px;
        font-weight: 400;
        font-family: "Source Sans Pro", sans-serif;
    }

    /* --- CORPO --- */
    .card-body-box {
        padding: 16px 16px 0px 16px;
    }
    .metrics-row {
        display: flex;
        gap: 20px;
        margin-bottom: 15px;
    }
    .metric-group {
        display: flex;
        flex-direction: column;
    }
    .metric-lbl {
        font-size: 0.7rem;
        color: #8b949e;
        text-transform: uppercase;
        font-family: "Source Sans Pro", sans-serif;
        margin-bottom: 2px;
    }
    .metric-val {
        font-size: 1.1rem;
        font-weight: 600;
        color: #e6edf3;
        font-family: "Source Sans Pro", sans-serif;
    }

    /* --- PROGRESSO --- */
    .progress-wrapper {
        margin-bottom: 12px;
    }
    .progress-header {
        display: flex;
        justify-content: space-between;
        font-size: 0.75rem;
        color: #8b949e;
        margin-bottom: 4px;
    }
    .progress-track {
        background-color: #21262d;
        height: 4px;
        width: 100%;
        border-radius: 2px;
        overflow: hidden;
    }
    .progress-fill {
        height: 100%;
        border-radius: 2px;
    }

    /* --- RODAPÉ ALINHADO --- */
    
    /* Container do Badge (Força alinhamento vertical exato) */
    .badge-wrapper {
        display: flex;
        align-items: center;     /* Centraliza verticalmente */
        height: 32px;            /* Mesma altura do botão */
    }
    
    .status-badge {
        padding: 0px 12px;       /* Padding lateral */
        height: 24px;            /* Altura visual da pílula */
        line-height: 24px;       /* Centraliza texto na pílula */
        border-radius: 12px;
        font-size: 0.65rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        white-space: nowrap;
        display: inline-block;
        font-family: "Source Sans Pro", sans-serif;
    }

    /* Botão (Força altura para igualar o container do badge) */
    div[data-testid="stVerticalBlockBorderWrapper"] button {
        background-color: #21262d;
        color: #e6edf3;
        border: 1px solid #30363d;
        border-radius: 6px;
        width: 100%;
        
        /* ALINHAMENTO MILIMÉTRICO */
        height: 32px !important;      /* Altura fixa */
        min-height: 32px !important;
        padding: 0px !important;      /* Remove padding interno para não engordar */
        line-height: 1 !important;    /* Texto centralizado */
        
        font-size: 0.8rem;
        font-weight: 600;
        margin-top: 0px; 
        font-family: "Source Sans Pro", sans-serif;
        
        /* Flex para centralizar o texto/ícone dentro do botão */
        display: flex;
        align-items: center;
        justify-content: center;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] button:hover {
        background-color: #1f6feb;
        border-color: #1f6feb;
        color: white;
    }
    
    /* Ajuste fino das colunas do rodapé */
    div[data-testid="column"] { padding: 0 5px; }

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
st.write("")

# ---------------------------------------------------------
# 5. GRID DE CARDS
# ---------------------------------------------------------
cols = st.columns(3)

for index, row in df_show.iterrows():
    with cols[index % 3]:
        
        # Dados e Cores
        pct = int(row['Conclusao_%'])
        status_raw = str(row['Status']).strip()
        
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
        else: # Não iniciado
            cor_tema = "#da3633"
            bg_badge = "rgba(218, 54, 51, 0.2)"
            color_badge = "#f85149"

        cor_margem = "#da3633" if row['Margem_%'] < META_MARGEM else "#3fb950"
        
        # --- CARD ---
        with st.container(border=True):
            
            # 1. HEADER
            html_header = [
                '<div class="card-header-stack">',
                f'<div class="project-title" title="{row["Projeto"]} - {row["Descricao"]}">{row["Projeto"]} - {row["Descricao"]}</div>',
                f'<div class="client-sub"><span>{row["Cliente"]}</span> <span>|</span> <span>{row["Cidade"]}</span></div>',
                '</div>'
            ]
            st.markdown("".join(html_header), unsafe_allow_html=True)

            # 2. BODY
            html_body = [
                '<div class="card-body-box">',
                
                # Métricas
                '<div class="metrics-row">',
                    '<div class="metric-group">',
                        '<span class="metric-lbl">Valor</span>',
                        f'<span class="metric-val">R$ {row["Vendido"]/1000:,.0f}k</span>',
                    '</div>',
                    '<div class="metric-group">',
                        '<span class="metric-lbl">Margem</span>',
                        f'<span class="metric-val" style="color: {cor_margem};">{row["Margem_%"]:.1f}%</span>',
                    '</div>',
                '</div>',

                # Progresso
                '<div class="progress-wrapper">',
                    '<div class="progress-header">',
                        '<span>Progresso</span>',
                        f'<span style="color: {color_badge}; font-weight:bold;">{pct}%</span>',
                    '</div>',
                    '<div class="progress-track">',
                        f'<div class="progress-fill" style="width: {pct}%; background-color: {cor_tema};"></div>',
                    '</div>',
                '</div>',
                '</div>'
            ]
            st.markdown("".join(html_body), unsafe_allow_html=True)

            # 3. FOOTER ALINHADO
            # O truque aqui é usar uma div .badge-wrapper com altura fixa de 32px
            # e forçar o botão a ter também altura de 32px no CSS.
            col_left, col_right = st.columns([1.5, 1], vertical_alignment="center")
            
            with col_left:
                st.markdown(f"""
                <div class="badge-wrapper">
                    <div class="status-badge" style="background-color: {bg_badge}; color: {color_badge}; border: 1px solid {cor_tema};">
                        {status_raw}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
            with col_right:
                if st.button("Detalhes ➜", key=f"btn_{row['Projeto']}", use_container_width=True):
                    st.session_state["projeto_foco"] = row['Projeto']
                    st.switch_page("dashboard_detalhado.py")
            
            st.write("") # Espaço final para respiro
