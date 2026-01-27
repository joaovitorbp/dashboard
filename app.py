import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ---------------------------------------------------------
# 1. CONFIGURAÇÃO E ESTILO (CSS DARK MODE REFINADO)
# ---------------------------------------------------------
st.set_page_config(layout="wide", page_title="Gestão de Obras", page_icon="🏗️")

st.markdown("""
<style>
    /* Fundo da aplicação */
    .stApp {
        background-color: #0e1117;
    }
    
    /* Espaçamento do container principal */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }
    
    /* Estilo dos Cards (KPIs) - Dark Mode "Glass" */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #1c1f26; 
        border: 1px solid #2d333b;
        border-radius: 8px;
        padding: 1rem;
    }
    
    /* Títulos e Textos */
    h1, h2, h3 {
        color: #f0f6fc !important;
        font-family: 'Inter', sans-serif;
    }
    p, label {
        color: #8b949e !important;
    }
    
    /* Métricas Grandes */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
        color: #ffffff !important;
        font-weight: 600;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.9rem !important;
        color: #8b949e !important;
    }
    
    /* Ajuste do Radio Button (Toggle) */
    div[role="radiogroup"] {
        display: flex;
        justify-content: center;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. CARREGAMENTO DE DADOS
# ---------------------------------------------------------
@st.cache_data
def load_data():
    return pd.read_excel("dados_obras_v5.xlsx")

try:
    df_raw = load_data()
except FileNotFoundError:
    st.error("⚠️ Arquivo 'dados_obras_v5.xlsx' não encontrado. Rode o script gerar_dados.py primeiro!")
    st.stop()

# ---------------------------------------------------------
# 3. SIDEBAR (SELETOR DE PROJETO COM DESCRIÇÃO)
# ---------------------------------------------------------
st.sidebar.title("Navegação")

# Criação do Label: "2024.0824 - Descrição..."
df_raw['Label_Menu'] = df_raw['Descricao'] + " (" + df_raw['Projeto'].astype(str) + ")"
mapa_projetos = dict(zip(df_raw['Label_Menu'], df_raw['Projeto']))

selecao = st.sidebar.selectbox("Selecione a Obra:", df_raw['Label_Menu'])
id_projeto = mapa_projetos[selecao]

# Filtrar dados
dados = df_raw[df_raw['Projeto'] == id_projeto].iloc[0]

# ---------------------------------------------------------
# 4. CÁLCULOS
# ---------------------------------------------------------
custo_total = dados['Mat_Real'] + dados['Desp_Real'] + dados['HH_Real_Vlr'] + dados['Impostos']
lucro_liquido = dados['Vendido'] - custo_total
margem_real_pct = (lucro_liquido / dados['Vendido']) * 100 if dados['Vendido'] > 0 else 0

# ---------------------------------------------------------
# 5. HEADER
# ---------------------------------------------------------
c_head, c_status = st.columns([3, 1])

with c_head:
    st.title(f"{dados['Descricao']}")
    st.markdown(f"**Projeto:** {dados['Projeto']} | **Cliente:** {dados['Cliente']} | **Local:** {dados['Cidade']}")

with c_status:
    st.write("")
    # Status com cor chamativa mas elegante
    cor_map = {"Finalizado": "#238636", "Em andamento": "#1f6feb", "Não iniciado": "#8b949e"}
    cor_bg = cor_map.get(dados['Status'], "#30363d")
    
    st.markdown(f"""
        <div style="background-color: {cor_bg}; padding: 10px; border-radius: 5px; text-align: center;">
            <strong style="color: white; font-size: 1.1rem;">{dados['Status'].upper()}</strong>
        </div>
    """, unsafe_allow_html=True)

st.write("")

# ---------------------------------------------------------
# 6. KPI CARDS (LIMPOS E PROPORCIONAIS)
# ---------------------------------------------------------
k1, k2, k3, k4 = st.columns(4)

with k1:
    with st.container(border=True):
        st.metric("💰 Contrato (Vendido)", f"R$ {dados['Vendido']/1000:,.0f}k")

with k2:
    with st.container(border=True):
        st.metric("📝 Faturado", f"R$ {dados['Faturado']/1000:,.0f}k")

with k3:
    with st.container(border=True):
        cor_lucro = "normal" if lucro_liquido >= 0 else "inverse"
        st.metric("💵 Lucro Real (R$)", f"R$ {lucro_liquido/1000:,.0f}k", delta_color=cor_lucro)

with k4:
    with st.container(border=True):
        # Removemos o texto longo do delta para não deformar o card
        st.metric("📈 Margem Real", f"{margem_real_pct:.1f}%", help="Meta esperada: 25.0%")

st.write("")

# ---------------------------------------------------------
# 7. SEÇÃO 1: EFICIÊNCIA OPERACIONAL (INVERTIDO E REDESENHADO)
# ---------------------------------------------------------
st.subheader("⚙️ Eficiência Operacional")

with st.container(border=True):
    col_gauges, col_info = st.columns([2, 1])
    
    with col_gauges:
        # Gráfico de Velocímetro Duplo (Gauge)
        fig_gauge = go.Figure()

        # Gauge 1: Físico
        fig_gauge.add_trace(go.Indicator(
            mode = "gauge+number",
            value = dados['Conclusao_%'],
            title = {'text': "Avanço Físico"},
            domain = {'x': [0, 0.45], 'y': [0, 1]},
            gauge = {
                'axis': {'range': [0, 100], 'tickcolor': "white"},
                'bar': {'color': "#238636"}, # Verde GitHub
                'bgcolor': "#161b22",
                'borderwidth': 2,
                'bordercolor': "#30363d"
            }
        ))

        # Gauge 2: Horas (HH)
        hh_orc = dados['HH_Orc_Qtd']
        hh_real = dados['HH_Real_Qtd']
        perc_hh = (hh_real / hh_orc * 100) if hh_orc > 0 else 0
        cor_hh = "#da3633" if perc_hh > (dados['Conclusao_%'] + 10) else "#1f6feb" # Vermelho ou Azul

        fig_gauge.add_trace(go.Indicator(
            mode = "gauge+number",
            value = perc_hh,
            title = {'text': "Consumo de Horas"},
            domain = {'x': [0.55, 1], 'y': [0, 1]},
            gauge = {
                'axis': {'range': [0, max(100, perc_hh)], 'tickcolor': "white"},
                'bar': {'color': cor_hh},
                'bgcolor': "#161b22",
                'borderwidth': 2,
                'bordercolor': "#30363d",
                'threshold': {
                    'line': {'color': "white", 'width': 4},
                    'thickness': 0.75,
                    'value': dados['Conclusao_%'] # Marca onde deveria estar
                }
            }
        ))
        
        fig_gauge.update_layout(height=250, margin=dict(t=30, b=10, l=10, r=10), paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"})
        st.plotly_chart(fig_gauge, use_container_width=True)

    with col_info:
        st.write("")
        st.markdown("### Diagnóstico")
        
        saldo_hh = hh_orc - hh_real
        if perc_hh > (dados['Conclusao_%'] + 10):
            st.error(f"🚨 **CRÍTICO:** Consumo de horas ({perc_hh:.0f}%) superou o avanço físico ({dados['Conclusao_%']}%) em mais de 10%.")
            st.markdown(f"**Estouro:** {int(hh_real - hh_orc)} horas acima do previsto.")
        elif perc_hh < dados['Conclusao_%']:
            st.success(f"✅ **EFICIENTE:** Obra avançada com economia de Mão de Obra.")
            st.markdown(f"**Saldo:** Ainda restam {int(saldo_hh)} horas.")
        else:
            st.info(f"⚖️ **EQUILIBRADO:** Ritmo de trabalho alinhado ao cronograma.")
            st.markdown(f"**Saldo:** Restam {int(saldo_hh)} horas.")

st.write("")

# ---------------------------------------------------------
# 8. SEÇÃO 2: COMPOSIÇÃO DE RESULTADO (CASCATA)
# ---------------------------------------------------------
st.subheader("📊 Composição do Lucro")

with st.container(border=True):
    # Toggle centralizado e acima
    col_ctrl, _ = st.columns([2, 5])
    with col_ctrl:
        modo_vis = st.radio("Visualização:", ["Percentual (%)", "Valores (R$)"], horizontal=True, label_visibility="collapsed")
    
    # Preparar Dados
    labels = ["Vendido", "Impostos", "Materiais", "Despesas", "Mão de Obra", "Lucro"]
    
    if modo_vis == "Valores (R$)":
        vals = [dados['Vendido'], -dados['Impostos'], -dados['Mat_Real'], -dados['Desp_Real'], -dados['HH_Real_Vlr'], lucro_liquido]
        text_vals = [f"R$ {v/1000:.1f}k" for v in vals]
        hover_templ = "R$ %{y:,.2f}"
    else:
        base = dados['Vendido'] if dados['Vendido'] > 0 else 1
        vals = [100, -(dados['Impostos']/base)*100, -(dados['Mat_Real']/base)*100, -(dados['Desp_Real']/base)*100, -(dados['HH_Real_Vlr']/base)*100, (lucro_liquido/base)*100]
        text_vals = [f"{v:.1f}%" for v in vals]
        hover_templ = "%{y:.1f}%"

    fig_water = go.Figure(go.Waterfall(
        orientation = "v",
        measure = ["relative", "relative", "relative", "relative", "relative", "total"],
        x = labels, y = vals,
        text = text_vals, textposition = "outside",
        connector = {"line":{"color":"#484f58"}},
        decreasing = {"marker":{"color":"#da3633"}}, # Vermelho opaco
        increasing = {"marker":{"color":"#238636"}}, # Verde GitHub
        totals = {"marker":{"color":"#1f6feb"}}       # Azul GitHub
    ))
    
    fig_water.update_layout(
        height=350, 
        margin=dict(t=20, b=0, l=0, r=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        yaxis=dict(showgrid=True, gridcolor='#30363d', zeroline=False),
        xaxis=dict(tickfont=dict(color='white')),
        font=dict(color='white')
    )
    st.plotly_chart(fig_water, use_container_width=True)

st.write("")

# ---------------------------------------------------------
# 9. SEÇÃO 3: DETALHAMENTO COMPARATIVO (CLEAN DESIGN)
# ---------------------------------------------------------
st.subheader("📉 Detalhamento de Custos")

c_mat, c_desp, c_mo = st.columns(3)

def plot_clean_bar(titulo, orcado, real):
    pct = (real / orcado * 100) if orcado > 0 else 0
    # Lógica de cor minimalista: Azul (Ok) ou Vermelho (Estouro)
    cor_bar = "#da3633" if real > orcado else "#1f6feb"
    
    fig = go.Figure()
    
    # Barra de Fundo (Budget) - Cinza Escuro para Dark Mode
    fig.add_trace(go.Bar(
        y=[''], x=[orcado], orientation='h', 
        marker_color='#30363d', # Cinza escuro
        name='Orçado', hovertemplate='Orçado: R$ %{x:,.2f}'
    ))
    
    # Barra de Frente (Real) - Colorida
    fig.add_trace(go.Bar(
        y=[''], x=[real], orientation='h', 
        marker_color=cor_bar,
        name='Realizado', hovertemplate='Real: R$ %{x:,.2f}'
    ))

    fig.update_layout(
        title=dict(text=f"{titulo}<br><span style='font-size:12px; color:#8b949e'>Gasto: {pct:.0f}% do Orçado</span>", x=0),
        barmode='overlay', 
        height=150,
        margin=dict(l=0, r=0, t=50, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False, showticklabels=False),
        yaxis=dict(showgrid=False, showticklabels=False),
        showlegend=False,
        font=dict(color='white')
    )
    return fig

with c_mat:
    with st.container(border=True):
        st.plotly_chart(plot_clean_bar("Materiais", dados['Mat_Orc'], dados['Mat_Real']), use_container_width=True)

with c_desp:
    with st.container(border=True):
        st.plotly_chart(plot_clean_bar("Despesas", dados['Desp_Orc'], dados['Desp_Real']), use_container_width=True)

with c_mo:
    with st.container(border=True):
        st.plotly_chart(plot_clean_bar("Mão de Obra (R$)", dados['HH_Orc_Vlr'], dados['HH_Real_Vlr']), use_container_width=True)
