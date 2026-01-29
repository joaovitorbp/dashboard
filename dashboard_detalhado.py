import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ---------------------------------------------------------
# ESTILO CSS PREMIUM (Idêntico à Home)
# ---------------------------------------------------------
st.markdown("""
<style>
    .stApp {background-color: #0e1117;}
    
    .block-container {
        padding-top: 3rem !important; 
        padding-bottom: 3rem;
    }
    
    .js-plotly-plot .plotly .modebar {display: none !important;}
    
    /* --- HEADER DA OBRA --- */
    .header-box {
        background-color: #161b22;
        border-radius: 8px;
        padding: 20px;
        border: 1px solid #30363d;
        margin-bottom: 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
    }
    .header-title {
        color: #ffffff;
        font-family: "Source Sans Pro", sans-serif;
        font-size: 1.5rem;
        font-weight: 700;
        margin: 0;
        line-height: 1.2;
    }
    .header-subtitle {
        color: #8b949e;
        font-family: "Source Sans Pro", sans-serif;
        font-size: 0.9rem;
        margin-top: 5px;
    }
    .header-badge {
        font-weight: 700;
        padding: 4px 12px;
        border-radius: 12px;
        color: white;
        font-size: 0.75rem;
        text-transform: uppercase;
        font-family: "Source Sans Pro", sans-serif;
        letter-spacing: 0.5px;
    }

    /* --- CARDS KPI --- */
    .kpi-card {
        background-color: #161b22;
        border-radius: 6px;
        padding: 20px;
        border: 1px solid #30363d;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .kpi-label {
        color: #8b949e;
        font-size: 0.75rem;
        font-weight: 400;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 5px;
        font-family: "Source Sans Pro", sans-serif;
    }
    .kpi-value {
        font-size: 1.6rem;
        font-weight: 700;
        color: #ffffff;
        font-family: "Source Sans Pro", sans-serif;
    }
    
    /* Ajustes Gerais */
    h1, h2, h3 { color: #f0f6fc !important; font-family: "Source Sans Pro", sans-serif; }
    p, label, span, div { font-family: "Source Sans Pro", sans-serif; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# FUNÇÕES E DADOS
# ---------------------------------------------------------
def format_currency(value):
    if pd.isna(value): return "R$ 0,00"
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def format_percent(value):
    if pd.isna(value): return "0,0%"
    return f"{value:.1f}%".replace(".", ",")

@st.cache_data
def load_data():
    return pd.read_excel("dados_obras_v5.xlsx")

try:
    df_raw = load_data()
except FileNotFoundError:
    st.error("⚠️ Arquivo 'dados_obras_v5.xlsx' não encontrado.")
    st.stop()

# ---------------------------------------------------------
# SIDEBAR COM LÓGICA DE NAVEGAÇÃO
# ---------------------------------------------------------
st.sidebar.markdown("### Seleção de Obra")
lista_projetos = sorted(df_raw['Projeto'].unique())

# Recupera o projeto da memória (se houver)
index_padrao = 0
if "projeto_foco" in st.session_state:
    try:
        index_padrao = lista_projetos.index(st.session_state["projeto_foco"])
    except ValueError:
        index_padrao = 0

id_projeto = st.sidebar.selectbox("Projeto:", lista_projetos, index=index_padrao)
dados = df_raw[df_raw['Projeto'] == id_projeto].iloc[0]

# ---------------------------------------------------------
# CÁLCULOS
# ---------------------------------------------------------
custo_total = dados['Mat_Real'] + dados['Desp_Real'] + dados['HH_Real_Vlr'] + dados['Impostos']
lucro_liquido = dados['Vendido'] - custo_total
margem_real_pct = (lucro_liquido / dados['Vendido']) * 100 if dados['Vendido'] > 0 else 0
META_MARGEM = 20.0 # Ajustado para 20 conforme Home

# ---------------------------------------------------------
# HEADER (COM CORES NOVAS)
# ---------------------------------------------------------
status_raw = str(dados['Status']).strip()

# Nova Paleta de Cores
if status_raw == "Finalizado":
    cor_status = "#238636" # Verde
elif status_raw == "Apresentado":
    cor_status = "#1f6feb" # Azul
elif status_raw == "Em andamento":
    cor_status = "#d29922" # Laranja
else:
    cor_status = "#da3633" # Vermelho (Não iniciado)

st.markdown(f"""
<div class="header-box" style="border-left: 4px solid {cor_status};">
    <div>
        <div class="header-title">{dados['Projeto']} - {dados['Descricao']}</div>
        <div class="header-subtitle">
            {dados['Cliente']} | {dados['Cidade']}
        </div>
    </div>
    <div class="header-badge" style="background-color: {cor_status};">
        {status_raw.upper()}
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# KPI CARDS
# ---------------------------------------------------------
def criar_card_destaque(titulo, valor, cor_texto="#ffffff"):
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">{titulo}</div>
        <div class="kpi-value" style="color: {cor_texto}">{valor}</div>
    </div>
    """, unsafe_allow_html=True)

k1, k2, k3, k4 = st.columns(4)

cor_neutra = "#e6edf3"
cor_sucesso = "#3fb950"
cor_erro = "#da3633"
cor_dinamica = cor_sucesso if margem_real_pct >= META_MARGEM else cor_erro

with k1: criar_card_destaque("Valor Vendido", format_currency(dados['Vendido']), cor_neutra)
with k2: criar_card_destaque("Valor Faturado", format_currency(dados['Faturado']), cor_neutra)
with k3: criar_card_destaque("Lucro Real", format_currency(lucro_liquido), cor_dinamica)
with k4: criar_card_destaque("Margem Real", format_percent(margem_real_pct), cor_dinamica)

st.write("")
st.divider()

# ---------------------------------------------------------
# SEÇÃO 1: EFICIÊNCIA OPERACIONAL
# ---------------------------------------------------------
st.subheader("Eficiência Operacional")

with st.container(border=True):
    col_gauges, col_spacer, col_diag = st.columns([5, 0.2, 3], vertical_alignment="center")
    
    with col_gauges:
        fig_gauge = go.Figure()

        # Gauge 1: Físico (Sempre Verde ou a cor do Status)
        fig_gauge.add_trace(go.Indicator(
            mode = "gauge+number", value = dados['Conclusao_%'],
            title = {'text': "Avanço Físico", 'font': {'size': 14, 'color': '#8b949e'}},
            domain = {'x': [0, 0.45], 'y': [0, 1]},
            number = {'suffix': "%", 'font': {'color': 'white'}},
            gauge = {
                'axis': {'range': [0, 100], 'tickcolor': "#161b22"},
                'bar': {'color': cor_status}, # Usa a cor do status da obra
                'bgcolor': "#0d1117", 'borderwidth': 1, 'bordercolor': "#30363d"
            }
        ))

        # Gauge 2: Horas (Consumo)
        hh_orc = dados['HH_Orc_Qtd']
        hh_real = dados['HH_Real_Qtd']
        perc_hh = (hh_real / hh_orc * 100) if hh_orc > 0 else 0
        cor_hh = "#da3633" if perc_hh > (dados['Conclusao_%'] + 10) else "#3fb950"

        fig_gauge.add_trace(go.Indicator(
            mode = "gauge+number", value = perc_hh,
            title = {'text': "Consumo Horas", 'font': {'size': 14, 'color': '#8b949e'}},
            domain = {'x': [0.55, 1], 'y': [0, 1]},
            number = {'suffix': "%", 'valueformat': ".1f", 'font': {'color': 'white'}},
            gauge = {
                'axis': {'range': [0, max(100, perc_hh)], 'tickcolor': "#161b22"},
                'bar': {'color': cor_hh},
                'bgcolor': "#0d1117", 'borderwidth': 1, 'bordercolor': "#30363d",
                'threshold': {'line': {'color': "white", 'width': 3}, 'thickness': 0.75, 'value': dados['Conclusao_%']}
            }
        ))
        
        fig_gauge.update_layout(
            height=200, margin=dict(t=30, b=10, l=30, r=30), 
            paper_bgcolor='rgba(0,0,0,0)', font={'family': "Source Sans Pro"}
        )
        st.plotly_chart(fig_gauge, use_container_width=True, config={'displayModeBar': False})

    with col_diag:
        saldo_hh = hh_orc - hh_real
        
        if perc_hh > (dados['Conclusao_%'] + 10):
            border_c = "#da3633" 
            titulo = "Baixa Eficiência"
            texto = "Gasto de horas acima do avanço físico."
        elif perc_hh < dados['Conclusao_%']:
            border_c = "#3fb950"
            titulo = "Alta Eficiência"
            texto = "Obra avançada com economia de horas."
        else:
            border_c = "#1f6feb"
            titulo = "Equilibrado"
            texto = "Ritmo alinhado ao planejado."

        st.markdown(f"""
        <div style="background-color: #161b22; border-left: 3px solid {border_c}; padding: 15px; border-radius: 4px;">
            <strong style="color: {border_c}; font-size: 1rem;">{titulo}</strong><br>
            <span style="color: #8b949e; font-size: 0.85rem;">{texto}</span><br><br>
            <span style="color: white; font-weight:bold;">Saldo: {int(saldo_hh)}h</span>
        </div>
        """, unsafe_allow_html=True)

st.write("")
st.divider()

# ---------------------------------------------------------
# SEÇÃO 2: DETALHAMENTO FINANCEIRO
# ---------------------------------------------------------
st.subheader("Detalhamento de Custos")

# Gráfico de Barras Horizontal (Simplificado e Limpo)
def plot_bar_h(label, orcado, real):
    fig = go.Figure()
    
    # Barra Cinza (Fundo/Orçado)
    fig.add_trace(go.Bar(
        y=[label], x=[orcado], name='Orçado', orientation='h',
        marker_color='#21262d',
        text=[format_currency(orcado)], textposition='auto',
        hoverinfo='none'
    ))
    
    # Barra Colorida (Frente/Real)
    cor_bar = "#da3633" if real > orcado else "#1f6feb"
    fig.add_trace(go.Bar(
        y=[label], x=[real], name='Realizado', orientation='h',
        marker_color=cor_bar,
        text=[format_currency(real)], textposition='auto',
        hoverinfo='none'
    ))

    fig.update_layout(
        barmode='overlay',
        height=80,
        margin=dict(l=0, r=0, t=10, b=10),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False, showticklabels=False, fixedrange=True),
        yaxis=dict(showticklabels=True, color='white', fixedrange=True, tickfont=dict(size=14, family="Source Sans Pro")),
        showlegend=False,
        font={'family': "Source Sans Pro"}
    )
    return fig

c1, c2 = st.columns(2)

with c1:
    st.plotly_chart(plot_bar_h("Materiais", dados['Mat_Orc'], dados['Mat_Real']), use_container_width=True, config={'displayModeBar': False})
    st.plotly_chart(plot_bar_h("Despesas", dados['Desp_Orc'], dados['Desp_Real']), use_container_width=True, config={'displayModeBar': False})

with c2:
    st.plotly_chart(plot_bar_h("Mão de Obra", dados['HH_Orc_Vlr'], dados['HH_Real_Vlr']), use_container_width=True, config={'displayModeBar': False})
    
    # Lucro Waterfall Mini
    fig_w = go.Figure(go.Waterfall(
        orientation = "h", measure = ["relative", "total"],
        y = ["Custo", "Lucro"], x = [custo_total, lucro_liquido],
        connector = {"line":{"color":"#30363d"}},
        decreasing = {"marker":{"color":"#da3633"}},
        increasing = {"marker":{"color":"#3fb950"}},
        totals = {"marker":{"color":"#3fb950"}},
        text = [format_currency(custo_total), format_currency(lucro_liquido)],
        textposition = "auto"
    ))
    fig_w.update_layout(
        title="Resultado Final",
        height=180, margin=dict(l=0, r=0, t=30, b=0),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False, showticklabels=False),
        yaxis=dict(color='white'),
        font={'family': "Source Sans Pro", 'color': 'white'}
    )
    st.plotly_chart(fig_w, use_container_width=True, config={'displayModeBar': False})
