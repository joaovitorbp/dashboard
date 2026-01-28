import streamlit as st
import pandas as pd

# ---------------------------------------------------------
# 1. CONFIGURAÇÃO VISUAL (CSS)
# ---------------------------------------------------------
st.markdown("""
<style>
    .stApp {background-color: #0e1117;}
    .block-container {padding-top: 2rem;}
    
    /* Card Visual */
    .project-card {
        background-color: #1c1f26;
        border-radius: 8px 8px 0 0; /* Arredonda só em cima */
        padding: 16px;
        border-top: 1px solid #30363d;
        border-right: 1px solid #30363d;
        border-left: 1px solid #30363d;
        /* A borda de baixo fica por conta do botão */
    }
    .card-header {
        font-size: 1.1rem;
        font-weight: 700;
        color: white;
        margin-bottom: 4px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .card-sub {
        font-size: 0.85rem;
        color: #8b949e;
        margin-bottom: 12px;
    }
    .card-metrics {
        display: flex;
        justify-content: space-between;
        margin-top: 15px;
        padding-top: 10px;
        border-top: 1px solid #30363d;
        font-size: 0.9rem;
    }
    .metric-box {
        text-align: center;
    }
    .metric-label { font-size: 0.75rem; color: #8b949e; text-transform: uppercase; letter-spacing: 1px; }
    .metric-val { font-weight: 600; color: #e6edf3; font-size: 1rem; }
    
    /* KPIs do Topo */
    .big-kpi {
        background-color: #161b22;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #30363d;
        text-align: center;
    }
    .big-kpi-val { font-size: 1.8rem; font-weight: bold; color: white; }
    .big-kpi-lbl { font-size: 0.9rem; color: #8b949e; }
    
    /* Ajuste para o botão parecer rodapé */
    div[data-testid="stVerticalBlock"] > div > button {
        border-radius: 0 0 8px 8px !important;
        border-top: none !important;
    }
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
# 3. LÓGICA DE DADOS
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
total_carteira = df['Vendido'].sum()
total_faturado = df['Faturado'].sum()
media_margem = df['Margem_%'].mean()
obras_ativas = len(df[df['Status'] == 'Em andamento'])

k1, k2, k3, k4 = st.columns(4)
k1.markdown(f"<div class='big-kpi'><div class='big-kpi-lbl'>Total em Carteira</div><div class='big-kpi-val'>R$ {total_carteira/1000000:.1f}M</div></div>", unsafe_allow_html=True)
k2.markdown(f"<div class='big-kpi'><div class='big-kpi-lbl'>Faturamento Real</div><div class='big-kpi-val'>R$ {total_faturado/1000000:.1f}M</div></div>", unsafe_allow_html=True)
k3.markdown(f"<div class='big-kpi'><div class='big-kpi-lbl'>Obras Ativas</div><div class='big-kpi-val'>{obras_ativas}</div></div>", unsafe_allow_html=True)
k4.markdown(f"<div class='big-kpi'><div class='big-kpi-lbl'>Margem Média</div><div class='big-kpi-val'>{media_margem:.1f}%</div></div>", unsafe_allow_html=True)

st.divider()

# ---------------------------------------------------------
# 5. FILTROS (INTEGRADOS EM UMA ÚNICA LINHA)
# ---------------------------------------------------------
filtro_status = st.radio(
    "Filtrar Visualização:",
    ["Todas", "Em andamento", "Finalizadas", "🚨 Apenas Críticas"],
    horizontal=True
)

# Aplicar Filtros
df_show = df.copy()

if filtro_status == "Em andamento":
    df_show = df_show[df_show['Status'] == 'Em andamento']
elif filtro_status == "Finalizadas":
    df_show = df_show[df_show['Status'] == 'Finalizado']
elif filtro_status == "🚨 Apenas Críticas":
    df_show = df_show[df_show['E_Critico'] == True]

st.write(f"Mostrando **{len(df_show)}** projetos")
st.write("") # Espaço extra

# ---------------------------------------------------------
# 6. GRID DE CARDS
# ---------------------------------------------------------
cols = st.columns(3)

for index, row in df_show.iterrows():
    with cols[index % 3]:
        
        # Variáveis
        pct = row['Conclusao_%']
        
        if pct >= 100:
            border_color = "#238636"
        elif pct > 50:
            border_color = "#1f6feb"
        else:
            border_color = "#8957e5"

        cor_margem = "#da3633" if row['Margem_%'] < META_MARGEM else "#2ea043"
        val_fmt = f"R$ {row['Vendido']/1000:,.0f}k"
        margem_fmt = f"{row['Margem_%']:.1f}%"
        
        # ITEM 3: Descrição concatenada no título
        titulo_card = f"{row['Projeto']} - {row['Descricao']}"

        # HTML (Visual do Card - Parte Superior)
        html_parts = [
            f'<div class="project-card" style="border-left: 5px solid {border_color};">',
            f'<div class="card-header" title="{titulo_card}">{titulo_card}</div>',
            f'<div class="card-sub">{row["Cliente"]} | {row["Cidade"]}</div>',
            
            # Barra de Progresso
            '<div style="display:flex; justify-content:space-between; font-size:0.8rem; color:#a0aec0; margin-bottom:5px;">',
            '<span>Avanço Físico</span>',
            f'<span>{int(pct)}%</span>',
            '</div>',
            '<div style="background-color: #30363d; height: 6px; border-radius: 3px;">',
            f'<div style="background-color: {border_color}; width: {pct}%; height: 100%; border-radius: 3px;"></div>',
            '</div>',

            # Métricas
            '<div class="card-metrics">',
            '<div class="metric-box">',
            '<div class="metric-label">VALOR</div>',
            f'<div class="metric-val">{val_fmt}</div>',
            '</div>',
            '<div class="metric-box">',
            '<div class="metric-label">MARGEM</div>',
            f'<div class="metric-val" style="color: {cor_margem};">{margem_fmt}</div>',
            '</div>',
            '</div>',
            '</div>'
        ]
        
        st.markdown("".join(html_parts), unsafe_allow_html=True)
        
        # ITEM 2: Botão transformado em Rodapé
        if st.button("Abrir Painel ➔", key=f"btn_{row['Projeto']}", use_container_width=True):
            st.session_state["projeto_foco"] = row['Projeto']
            st.switch_page("dashboard_detalhado.py")
