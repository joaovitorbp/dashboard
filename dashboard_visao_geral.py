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
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        border: 1px solid #30363d;
    }
    .card-header {
        font-size: 1.1rem;
        font-weight: 700;
        color: white;
        margin-bottom: 4px;
    }
    .card-sub {
        font-size: 0.85rem;
        color: #8b949e;
        margin-bottom: 12px;
    }
    .card-metrics {
        display: flex;
        justify-content: space-between;
        margin-top: 10px;
        padding-top: 10px;
        border-top: 1px solid #30363d;
        font-size: 0.9rem;
    }
    .metric-box {
        text-align: center;
    }
    .metric-label { font-size: 0.75rem; color: #8b949e; }
    .metric-val { font-weight: 600; color: #e6edf3; }
    
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
# Usando concatenação simples para evitar quebras de linha no HTML dos KPIs
k1.markdown(f"<div class='big-kpi'><div class='big-kpi-lbl'>Total em Carteira</div><div class='big-kpi-val'>R$ {total_carteira/1000000:.1f}M</div></div>", unsafe_allow_html=True)
k2.markdown(f"<div class='big-kpi'><div class='big-kpi-lbl'>Faturamento Real</div><div class='big-kpi-val'>R$ {total_faturado/1000000:.1f}M</div></div>", unsafe_allow_html=True)
k3.markdown(f"<div class='big-kpi'><div class='big-kpi-lbl'>Obras Ativas</div><div class='big-kpi-val'>{obras_ativas}</div></div>", unsafe_allow_html=True)
k4.markdown(f"<div class='big-kpi'><div class='big-kpi-lbl'>Margem Média</div><div class='big-kpi-val'>{media_margem:.1f}%</div></div>", unsafe_allow_html=True)

st.divider()

# Filtros
col_status, col_check, col_spacer = st.columns([2, 1.5, 3])

with col_status:
    filtro_status = st.radio(
        "Filtrar por Status:",
        ["Todas", "Em andamento", "Finalizadas"],
        horizontal=True,
        label_visibility="collapsed"
    )

with col_check:
    st.write("") 
    ver_apenas_criticas = st.checkbox("⚠️ Apenas Obras Críticas")

# Aplicar Filtros
df_show = df.copy()

if filtro_status == "Em andamento":
    df_show = df_show[df_show['Status'] == 'Em andamento']
elif filtro_status == "Finalizadas":
    df_show = df_show[df_show['Status'] == 'Finalizado']

if ver_apenas_criticas:
    df_show = df_show[df_show['E_Critico'] == True]

st.write(f"Mostrando **{len(df_show)}** projetos")

# Grid de Cards
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

        # --- CORREÇÃO TÉCNICA AQUI ---
        # Montamos o HTML linha a linha em uma lista e juntamos tudo em uma única linha de texto.
        # Isso impede que o Python insira quebras de linha (\n) ou espaços que quebrem o layout.
        html_parts = [
            f'<div class="project-card" style="border-left: 5px solid {border_color};">',
            f'<div class="card-header">{row["Projeto"]}</div>',
            f'<div class="card-sub">{row["Cliente"]} | {row["Cidade"]}</div>',
            '<div style="display:flex; justify-content:space-between; font-size:0.8rem; color:#a0aec0; margin-bottom:5px;">',
            '<span>Avanço Físico</span>',
            f'<span>{int(pct)}%</span>',
            '</div>',
            '<div style="background-color: #30363d; height: 6px; border-radius: 3px;">',
            f'<div style="background-color: {border_color}; width: {pct}%; height: 100%; border-radius: 3px;"></div>',
            '</div>',
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
        
        # Junta tudo numa string só, sem espaços extras
        final_html = "".join(html_parts)
        
        st.markdown(final_html, unsafe_allow_html=True)
        
        # Botão de Navegação
        if st.button(f"🔎 Detalhes", key=f"btn_{row['Projeto']}", use_container_width=True):
            st.session_state["projeto_foco"] = row['Projeto']
            st.switch_page("dashboard_detalhado.py")
