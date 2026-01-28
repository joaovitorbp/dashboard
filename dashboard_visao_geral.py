import streamlit as st
import pandas as pd

# ---------------------------------------------------------
# 1. CONFIGURAÇÃO VISUAL (CSS)
# ---------------------------------------------------------
st.markdown("""
<style>
    .stApp {background-color: #0e1117;}
    .block-container {padding-top: 2rem;}
    
    /* Estiliza o Container Nativo para parecer um Card Escuro */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #1c1f26;
        border-color: #30363d;
        padding: 15px;
    }
    
    /* Tira o padding extra de dentro das colunas */
    [data-testid="column"] {
        padding: 0px;
    }

    /* Estilo dos Textos Personalizados */
    .card-title {
        color: white;
        font-weight: 700;
        font-size: 1.05rem;
        margin-bottom: 2px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .card-subtitle {
        color: #8b949e;
        font-size: 0.8rem;
        margin-bottom: 8px;
    }
    .metric-label {
        font-size: 0.7rem;
        color: #8b949e;
        text-transform: uppercase;
    }
    .metric-value {
        font-size: 0.95rem;
        font-weight: 600;
        color: #e6edf3;
    }

    /* Botão Pequeno e Personalizado */
    div[data-testid="stVerticalBlockBorderWrapper"] button {
        border: 1px solid #30363d;
        background-color: #21262d;
        color: #58a6ff;
        font-size: 0.8rem;
        padding: 4px 10px;
        height: auto;
        min-height: 0px;
        line-height: 1.2;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] button:hover {
        border-color: #8b949e;
        background-color: #30363d;
        color: white;
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

# Filtros
filtro_status = st.radio(
    "Filtrar Visualização:",
    ["Todas", "Em andamento", "Finalizadas", "🚨 Apenas Críticas"],
    horizontal=True
)

df_show = df.copy()

if filtro_status == "Em andamento":
    df_show = df_show[df_show['Status'] == 'Em andamento']
elif filtro_status == "Finalizadas":
    df_show = df_show[df_show['Status'] == 'Finalizado']
elif filtro_status == "🚨 Apenas Críticas":
    df_show = df_show[df_show['E_Critico'] == True]

st.write(f"Mostrando **{len(df_show)}** projetos")
st.write("") 

# ---------------------------------------------------------
# 6. GRID DE CARDS (HÍBRIDO)
# ---------------------------------------------------------
cols = st.columns(3)

for index, row in df_show.iterrows():
    with cols[index % 3]:
        
        # Definição de Cores
        pct = row['Conclusao_%']
        if pct >= 100:
            bar_color = "#238636" # Verde
        elif pct > 50:
            bar_color = "#1f6feb" # Azul
        else:
            bar_color = "#8957e5" # Roxo

        cor_margem = "#da3633" if row['Margem_%'] < META_MARGEM else "#2ea043"
        titulo_completo = f"{row['Projeto']} - {row['Descricao']}"

        # --- INÍCIO DO CARD ---
        with st.container(border=True):
            
            # 1. Barra Colorida Superior (Simula a borda colorida)
            st.markdown(f"""
                <div style="height: 4px; background-color: {bar_color}; margin: -15px -15px 10px -15px;"></div>
                <div class="card-title" title="{titulo_completo}">{titulo_completo}</div>
                <div class="card-subtitle">{row['Cliente']} | {row['Cidade']}</div>
            """, unsafe_allow_html=True)

            # 2. Barra de Progresso Nativa
            st.progress(int(pct) / 100, text=f"Avanço: {int(pct)}%")
            
            # 3. Grid Interno: Métricas na Esquerda | Botão na Direita
            c_val, c_mar, c_btn = st.columns([1.2, 1.2, 0.8])
            
            with c_val:
                st.markdown(f"""
                <div class="metric-label">VALOR</div>
                <div class="metric-value">R$ {row['Vendido']/1000:,.0f}k</div>
                """, unsafe_allow_html=True)
                
            with c_mar:
                st.markdown(f"""
                <div class="metric-label">MARGEM</div>
                <div class="metric-value" style="color: {cor_margem};">{row['Margem_%']:.1f}%</div>
                """, unsafe_allow_html=True)
            
            with c_btn:
                st.write("") # Espaço para alinhar verticalmente
                if st.button("Abrir ➚", key=f"btn_{row['Projeto']}", use_container_width=True):
                    st.session_state["projeto_foco"] = row['Projeto']
                    st.switch_page("dashboard_detalhado.py")
