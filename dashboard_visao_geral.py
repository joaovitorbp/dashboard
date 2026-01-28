import streamlit as st
import pandas as pd

# CSS Personalizado para os Cards
st.markdown("""
<style>
    .stApp {background-color: #0e1117;}
    /* Ajuste de padding para não ficar colado no topo */
    .block-container {padding-top: 2rem;}
    
    /* Estilo do Card de Projeto */
    .project-card {
        background-color: #1c1f26;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        transition: transform 0.2s;
        height: 100%;
    }
    .project-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
    }
    .card-title {
        color: white;
        font-weight: 700;
        font-size: 1.1rem;
        margin-bottom: 5px;
    }
    .card-client {
        color: #8b949e;
        font-size: 0.9rem;
        margin-bottom: 10px;
    }
    .card-footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 10px;
        font-size: 0.85rem;
        color: #e6edf3;
    }
    .status-badge {
        padding: 2px 8px;
        border-radius: 10px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    
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
# CARREGAR DADOS
# ---------------------------------------------------------
@st.cache_data
def load_data():
    return pd.read_excel("dados_obras_v5.xlsx")

try:
    df = load_data()
except FileNotFoundError:
    st.error("⚠️ Base de dados não encontrada.")
    st.stop()

# ---------------------------------------------------------
# LÓGICA DE ALERTA
# ---------------------------------------------------------
META_MARGEM = 20.0

def verificar_alerta(row):
    custo = row['Mat_Real'] + row['Desp_Real'] + row['HH_Real_Vlr'] + row['Impostos']
    lucro = row['Vendido'] - custo
    margem = (lucro / row['Vendido'] * 100) if row['Vendido'] > 0 else 0
    
    hh_perc = (row['HH_Real_Qtd'] / row['HH_Orc_Qtd'] * 100) if row['HH_Orc_Qtd'] > 0 else 0
    fisico = row['Conclusao_%']
    
    if margem < META_MARGEM: return "margin_low"
    if hh_perc > (fisico + 5): return "hh_high"
    return "ok"

df['Alerta'] = df.apply(verificar_alerta, axis=1)

# ---------------------------------------------------------
# INTERFACE
# ---------------------------------------------------------
st.markdown("## 🏢 Painel de Controle - Visão Geral")
st.markdown("Monitoramento consolidado de todas as obras da TE Engenharia.")
st.write("")

# KPIs Globais
total_carteira = df['Vendido'].sum()
total_faturado = df['Faturado'].sum()
total_obras = len(df)
obras_andamento = len(df[df['Status'] == 'Em andamento'])

k1, k2, k3, k4 = st.columns(4)
k1.markdown(f"<div class='big-kpi'><div class='big-kpi-lbl'>Total em Carteira</div><div class='big-kpi-val'>R$ {total_carteira/1000000:.1f}M</div></div>", unsafe_allow_html=True)
k2.markdown(f"<div class='big-kpi'><div class='big-kpi-lbl'>Faturamento Real</div><div class='big-kpi-val'>R$ {total_faturado/1000000:.1f}M</div></div>", unsafe_allow_html=True)
k3.markdown(f"<div class='big-kpi'><div class='big-kpi-lbl'>Obras Ativas</div><div class='big-kpi-val'>{obras_andamento}</div></div>", unsafe_allow_html=True)
k4.markdown(f"<div class='big-kpi'><div class='big-kpi-lbl'>Total de Obras</div><div class='big-kpi-val'>{total_obras}</div></div>", unsafe_allow_html=True)

st.divider()

# Filtros
c_filter, c_legend = st.columns([2, 2])
with c_filter:
    filtro_status = st.radio(
        "Filtrar Visualização:",
        ["Todas", "Em andamento", "Finalizadas", "🚨 Críticas"],
        horizontal=True
    )

with c_legend:
    st.markdown("""
    <div style="text-align: right; padding-top: 10px; font-size: 0.9rem; color: #8b949e;">
        <span style="color: #da3633;">❚</span> Margem Baixa &nbsp;&nbsp;
        <span style="color: #d29922;">❚</span> Estouro HH &nbsp;&nbsp;
        <span style="color: #238636;">❚</span> Saudável
    </div>
    """, unsafe_allow_html=True)

# Aplicação do Filtro
df_show = df.copy()
if filtro_status == "Em andamento":
    df_show = df[df['Status'] == 'Em andamento']
elif filtro_status == "Finalizadas":
    df_show = df[df['Status'] == 'Finalizado']
elif filtro_status == "🚨 Críticas":
    df_show = df[df['Alerta'] != 'ok']

st.write("")

# Grid de Cards
cols = st.columns(3)
for index, row in df_show.iterrows():
    if row['Alerta'] == 'margin_low':
        border_color = "#da3633"
        msg_alerta = "📉 Margem Baixa"
    elif row['Alerta'] == 'hh_high':
        border_color = "#d29922"
        msg_alerta = "⚠️ Estouro HH"
    else:
        border_color = "#238636"
        msg_alerta = "✅ Saudável"
        
    bg_status = "#1f6feb" if row['Status'] == 'Em andamento' else "#238636" if row['Status'] == 'Finalizado' else "#30363d"
    
    card_html = f"""
    <div class="project-card" style="border-left: 5px solid {border_color};">
        <div class="card-title">{row['Projeto']}</div>
        <div class="card-client">
            🏢 {row['Cliente']} | 📍 {row['Cidade']}
        </div>
        <div style="margin: 10px 0;">
            <div style="display:flex; justify-content:space-between; color: #a0aec0; font-size: 0.8rem;">
                <span>Físico: {row['Conclusao_%']}%</span>
                <span>{msg_alerta}</span>
            </div>
            <div style="background-color: #30363d; height: 6px; border-radius: 3px; margin-top: 5px;">
                <div style="background-color: {border_color}; width: {row['Conclusao_%']}%; height: 100%; border-radius: 3px;"></div>
            </div>
        </div>
        <div class="card-footer">
            <span class="status-badge" style="background-color: {bg_status}40; color: {bg_status}ff; border: 1px solid {bg_status};">
                {row['Status'].upper()}
            </span>
            <span style="font-weight:bold;">R$ {row['Vendido']/1000:,.0f}k</span>
        </div>
    </div>
    """
    with cols[index % 3]:
        st.markdown(card_html, unsafe_allow_html=True)

if len(df_show) == 0:
    st.info("Nenhuma obra encontrada com esse filtro.")
