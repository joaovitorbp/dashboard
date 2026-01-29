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

    /* --- CORPO (Grid 2x2) --- */
    .card-body-box {
        padding: 16px 16px 0px 16px;
    }
    
    /* Grid para organizar 4 métricas */
    .metrics-grid {
        display: grid;
        grid-template-columns: 1fr 1fr; /* 2 Colunas Iguais */
        gap: 12px; /* Espaço entre elas */
        margin-bottom: 15px;
    }
    
    .metric-item {
        background-color: #0d1117;
        border: 1px solid #30363d;
        border-radius: 6px;
        padding: 8px 12px;
        display: flex;
        flex-direction: column;
    }

    .metric-lbl {
        font-size: 0.65rem;
        color: #8b949e;
        text-transform: uppercase;
        font-family: "Source Sans Pro", sans-serif;
        margin-bottom: 4px;
        letter-spacing: 0.5px;
    }
    .metric-val {
        font-size: 1rem;
        font-weight: 600;
        color: #e6edf3;
        font-family: "Source Sans Pro", sans-serif;
    }

    /* --- PROGRESSO --- */
    .progress-wrapper {
        margin-bottom: 15px;
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

    /* --- RODAPÉ --- */
    .badge-wrapper {
        height: 32px;
        display: flex;
        align-items: center;
    }
    
    .status-badge {
        padding: 0 10px;
        height: 24px;
        line-height: 24px;
        border-radius: 4px;
        font-size: 0.65rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        white-space: nowrap;
        font-family: "Source Sans Pro", sans-serif;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] button {
        background-color: #21262d;
        color: #e6edf3;
        border: 1px solid #30363d;
        border-radius: 6px;
        width: 100%;
        height: 32px !important;
        min-height: 32px !important;
        margin: 0 !important;
        padding: 0 !important;
        font-size: 0.8rem;
        font-weight: 600;
        font-family: "Source Sans Pro", sans-serif;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] button:hover {
        background-color: #1f6feb;
        border-color: #1f6feb;
        color: white;
    }
    
    div[data-testid="column"] { padding: 0 6px; }

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
        
        # --- CÁLCULOS E CORES ---
        pct = int(row['Conclusao_%'])
        status_raw = str(row['Status']).strip()
        
        # Cálculo de Consumo de Horas (%)
        if row['HH_Orc_Qtd'] > 0:
            pct_horas = (row['HH_Real_Qtd'] / row['HH_Orc_Qtd']) * 100
        else:
            pct_horas = 0
            
        # Cálculo de Consumo de Materiais (%)
        if row['Mat_Orc'] > 0:
            pct_mat = (row['Mat_Real'] / row['Mat_Orc']) * 100
        else:
            pct_mat = 0

        # Cores de Status
        if status_raw == "Finalizado":
            cor_tema = "#238636" # Verde
            bg_badge = "rgba(35, 134, 54, 0.2)"
            color_badge = "#3fb950"
        elif status_raw == "Apresentado":
            cor_tema = "#1f6feb" # Azul
            bg_badge = "rgba(31, 111, 235, 0.2)"
            color_badge = "#58a6ff"
        elif status_raw == "Em andamento":
            cor_tema = "#d29922" # Laranja
            bg_badge = "rgba(210, 153, 34, 0.2)"
            color_badge = "#e3b341"
        else: # Não iniciado
            cor_tema = "#da3633" # Vermelho
            bg_badge = "rgba(218, 54, 51, 0.2)"
            color_badge = "#f85149"

        # Cores Condicionais das Métricas
        cor_margem = "#da3633" if row['Margem_%'] < META_MARGEM else "#3fb950" # Vermelho se baixa
        cor_horas = "#da3633" if pct_horas > 100 else "#e6edf3" # Vermelho se estourou
        cor_mat = "#da3633" if pct_mat > 100 else "#e6edf3" # Vermelho se estourou
        
        # --- ESTRUTURA DO CARD ---
        with st.container(border=True):
            
            # 1. HEADER
            html_header = [
                '<div class="card-header-stack">',
                f'<div class="project-title" title="{row["Projeto"]} - {row["Descricao"]}">{row["Projeto"]} - {row["Descricao"]}</div>',
                f'<div class="client-sub"><span>{row["Cliente"]}</span> <span>|</span> <span>{row["Cidade"]}</span></div>',
                '</div>'
            ]
            st.markdown("".join(html_header), unsafe_allow_html=True)

            # 2. BODY (Grid 2x2 + Progresso)
            html_body = [
                '<div class="card-body-box">',
                
                # GRID 2x2
                '<div class="metrics-grid">',
                    # Item 1: Valor
                    '<div class="metric-item">',
                        '<span class="metric-lbl">Valor</span>',
                        f'<span class="metric-val">R$ {row["Vendido"]/1000:,.0f}k</span>',
                    '</div>',
                    # Item 2: Margem
                    '<div class="metric-item">',
                        '<span class="metric-lbl">Margem</span>',
                        f'<span class="metric-val" style="color: {cor_margem};">{row["Margem_%"]:.1f}%</span>',
                    '</div>',
                    # Item 3: Horas Consumidas
                    '<div class="metric-item">',
                        '<span class="metric-lbl">% Horas</span>',
                        f'<span class="metric-val" style="color: {cor_horas};">{pct_horas:.0f}%</span>',
                    '</div>',
                    # Item 4: Materiais Consumidos
                    '<div class="metric-item">',
                        '<span class="metric-lbl">% Material</span>',
                        f'<span class="metric-val" style="color: {cor_mat};">{pct_mat:.0f}%</span>',
                    '</div>',
                '</div>',

                # Barra de Progresso
                '<div class="progress-wrapper">',
                    '<div class="progress-header">',
                        '<span>Avanço Físico</span>',
                        f'<span style="color: {color_badge}; font-weight:bold;">{pct}%</span>',
                    '</div>',
                    '<div class="progress-track">',
                        f'<div class="progress-fill" style="width: {pct}%; background-color: {cor_tema};"></div>',
                    '</div>',
                '</div>',
                '</div>'
            ]
            st.markdown("".join(html_body), unsafe_allow_html=True)

            # 3. FOOTER
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
            
            st.write("")
