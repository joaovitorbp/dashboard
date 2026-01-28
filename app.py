import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ---------------------------------------------------------
# 1. CONFIGURAÇÃO E ESTILO (MANTENDO DARK MODE)
# ---------------------------------------------------------
st.set_page_config(layout="wide", page_title="Gestão de Obras", page_icon="🏗️")

st.markdown("""
<style>
    .stApp {background-color: #0e1117;}
    .block-container {padding-top: 2rem; padding-bottom: 3rem;}
    
    /* Cards KPI com borda sutil */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #1c1f26; 
        border: 1px solid #2d333b;
        border-radius: 8px;
        padding: 1rem;
    }
    
    /* Textos e Métricas */
    h1, h2, h3 {color: #f0f6fc !important;}
    p, label, span, div {color: #e6edf3 !important;}
    
    [data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
        color: #ffffff !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 1rem !important;
        color: #8b949e !important;
    }
    
    /* Remove barra de ferramentas do Plotly */
    .js-plotly-plot .plotly .modebar {display: none !important;}
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
    st.error("⚠️ Arquivo 'dados_obras_v5.xlsx' não encontrado.")
    st.stop()

# ---------------------------------------------------------
# 3. SIDEBAR (PONTO 1: BASEADO NO NÚMERO DO PROJETO)
# ---------------------------------------------------------
st.sidebar.title("Navegação")

# Lista ordenada apenas pelos números dos projetos
lista_projetos = sorted(df_raw['Projeto'].unique())
id_projeto = st.sidebar.selectbox("Selecione o Projeto:", lista_projetos)

# Filtrar dados
dados = df_raw[df_raw['Projeto'] == id_projeto].iloc[0]

# ---------------------------------------------------------
# 4. CÁLCULOS
# ---------------------------------------------------------
custo_total = dados['Mat_Real'] + dados['Desp_Real'] + dados['HH_Real_Vlr'] + dados['Impostos']
lucro_liquido = dados['Vendido'] - custo_total
margem_real_pct = (lucro_liquido / dados['Vendido']) * 100 if dados['Vendido'] > 0 else 0

META_MARGEM = 25.0

# ---------------------------------------------------------
# 5. HEADER (PONTO 2: NÚMERO - DESCRIÇÃO)
# ---------------------------------------------------------
c_head, c_status = st.columns([3, 1])

with c_head:
    st.title(f"{dados['Projeto']} - {dados['Descricao']}")
    st.markdown(f"**Cliente:** {dados['Cliente']} | **Local:** {dados['Cidade']}")

with c_status:
    st.write("")
    cor_map = {"Finalizado": "#238636", "Em andamento": "#1f6feb", "Não iniciado": "#8b949e"}
    cor_bg = cor_map.get(dados['Status'], "#30363d")
    
    st.markdown(f"""
        <div style="background-color: {cor_bg}; padding: 8px; border-radius: 6px; text-align: center;">
            <strong style="color: white; font-size: 1rem;">{dados['Status'].upper()}</strong>
        </div>
    """, unsafe_allow_html=True)

st.divider()

# ---------------------------------------------------------
# 6. KPI CARDS (PONTO 4: COR NA MARGEM E LUCRO)
# ---------------------------------------------------------
k1, k2, k3, k4 = st.columns(4)

with k1:
    with st.container(border=True):
        st.metric("💰 Contrato", f"R$ {dados['Vendido']:,.0f}")

with k2:
    with st.container(border=True):
        st.metric("📝 Faturado", f"R$ {dados['Faturado']:,.0f}")

# Lógica de Cor: Se Margem < 25%, delta é negativo (vermelho). Se >= 25%, delta é positivo (verde).
delta_val = margem_real_pct - META_MARGEM
cor_delta = "normal" # Normal faz: Positivo=Verde, Negativo=Vermelho

with k3:
    with st.container(border=True):
        # Usando o mesmo delta da margem para colorir o lucro
        st.metric("💵 Lucro Real", f"R$ {lucro_liquido:,.0f}", delta=f"{lucro_liquido:,.0f}", delta_color=cor_delta)

with k4:
    with st.container(border=True):
        st.metric("📈 Margem Real", f"{margem_real_pct:.1f}%", delta=f"{delta_val:.1f}% (Meta 25%)", delta_color=cor_delta)

st.write("")

# ---------------------------------------------------------
# 7. SEÇÃO 1: EFICIÊNCIA OPERACIONAL (PONTO 5: AJUSTE DIAGNÓSTICO)
# ---------------------------------------------------------
st.subheader("⚙️ Eficiência Operacional")

with st.container(border=True):
    # Adicionei col_spacer para afastar o texto dos gráficos
    col_gauges, col_spacer, col_diag = st.columns([5, 0.5, 3])
    
    with col_gauges:
        # Gráfico Gauge Lado a Lado
        fig_gauge = go.Figure()

        # Gauge 1: Físico
        fig_gauge.add_trace(go.Indicator(
            mode = "gauge+number", value = dados['Conclusao_%'],
            title = {'text': "Avanço Físico"},
            domain = {'x': [0, 0.45], 'y': [0, 1]},
            gauge = {
                'axis': {'range': [0, 100], 'tickcolor': "white"},
                'bar': {'color': "#238636"}, 
                'bgcolor': "#0d1117", 'borderwidth': 2, 'bordercolor': "#30363d"
            }
        ))

        # Gauge 2: Horas
        hh_orc = dados['HH_Orc_Qtd']
        hh_real = dados['HH_Real_Qtd']
        perc_hh = (hh_real / hh_orc * 100) if hh_orc > 0 else 0
        cor_hh = "#da3633" if perc_hh > (dados['Conclusao_%'] + 10) else "#1f6feb"

        fig_gauge.add_trace(go.Indicator(
            mode = "gauge+number", value = perc_hh,
            title = {'text': "Consumo Horas"},
            domain = {'x': [0.55, 1], 'y': [0, 1]},
            gauge = {
                'axis': {'range': [0, max(100, perc_hh)], 'tickcolor': "white"},
                'bar': {'color': cor_hh},
                'bgcolor': "#0d1117", 'borderwidth': 2, 'bordercolor': "#30363d",
                'threshold': {'line': {'color': "white", 'width': 4}, 'thickness': 0.75, 'value': dados['Conclusao_%']}
            }
        ))
        
        # PONTO 3: Gráficos fixos (sem modebar, sem zoom)
        fig_gauge.update_layout(
            height=220, 
            margin=dict(t=30, b=10, l=20, r=20), 
            paper_bgcolor='rgba(0,0,0,0)', 
            font={'color': "white"},
            xaxis={'fixedrange': True}, yaxis={'fixedrange': True}
        )
        st.plotly_chart(fig_gauge, use_container_width=True, config={'displayModeBar': False})

    # Diagnóstico (Alterado: sem fundo colorido forte, apenas texto formatado)
    with col_diag:
        st.write("")
        st.write("") # Espaçamento vertical
        st.markdown("##### 🩺 Diagnóstico")
        
        saldo_hh = hh_orc - hh_real
        if perc_hh > (dados['Conclusao_%'] + 10):
            st.markdown(f"🔴 **CRÍTICO:** Consumo de horas (**{perc_hh:.0f}%**) superou o físico.")
            st.markdown(f"Desvio: **{int(hh_real - hh_orc)}h** excedentes.")
        elif perc_hh < dados['Conclusao_%']:
            st.markdown(f"🟢 **EFICIENTE:** Obra avançada com economia.")
            st.markdown(f"Saldo atual: **{int(saldo_hh)}h** disponíveis.")
        else:
            st.markdown(f"🔵 **EQUILIBRADO:** Ritmo alinhado ao planejado.")
            st.markdown(f"Saldo: **{int(saldo_hh)}h**.")

st.write("")

# ---------------------------------------------------------
# 8. SEÇÃO 2: COMPOSIÇÃO DE RESULTADO (CASCATA)
# ---------------------------------------------------------
st.subheader("📊 Composição do Lucro")

with st.container(border=True):
    col_tgl, col_graph = st.columns([1, 6])
    with col_tgl:
        st.write("")
        # Toggle mantido conforme pedido anterior
        modo_vis = st.radio("Unidade:", ["Percentual (%)", "Valores (R$)"], label_visibility="collapsed")
    
    with col_graph:
        labels = ["Vendido", "Impostos", "Materiais", "Despesas", "Mão de Obra", "Lucro"]
        if modo_vis == "Valores (R$)":
            vals = [dados['Vendido'], -dados['Impostos'], -dados['Mat_Real'], -dados['Desp_Real'], -dados['HH_Real_Vlr'], lucro_liquido]
            text_vals = [f"R$ {v/1000:.1f}k" for v in vals]
        else:
            base = dados['Vendido'] if dados['Vendido'] > 0 else 1
            vals = [100, -(dados['Impostos']/base)*100, -(dados['Mat_Real']/base)*100, -(dados['Desp_Real']/base)*100, -(dados['HH_Real_Vlr']/base)*100, (lucro_liquido/base)*100]
            text_vals = [f"{v:.1f}%" for v in vals]

        fig_water = go.Figure(go.Waterfall(
            orientation = "v", measure = ["relative"]*5 + ["total"],
            x = labels, y = vals, text = text_vals, textposition = "outside",
            connector = {"line":{"color":"#484f58"}},
            decreasing = {"marker":{"color":"#da3633"}},
            increasing = {"marker":{"color":"#238636"}},
            totals = {"marker":{"color":"#1f6feb"}}
        ))
        
        # PONTO 3: Gráficos fixos
        fig_water.update_layout(
            height=300, margin=dict(t=20, b=0, l=0, r=0),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            yaxis=dict(showgrid=True, gridcolor='#30363d', zeroline=False, fixedrange=True),
            xaxis=dict(tickfont=dict(color='white'), fixedrange=True),
            font=dict(color='white')
        )
        st.plotly_chart(fig_water, use_container_width=True, config={'displayModeBar': False})

st.write("")

# ---------------------------------------------------------
# 9. SEÇÃO 3: DETALHAMENTO DE CUSTOS (PONTO 6: MAIS DETALHE)
# ---------------------------------------------------------
st.subheader("📉 Detalhamento de Custos (Orçado vs Realizado)")

# Função para criar gráfico detalhado por linha
def plot_detailed_row(titulo, orcado, real):
    pct = (real / orcado * 100) if orcado > 0 else 0
    # Vermelho se estourar orçamento, Azul se estiver dentro
    cor_real = "#da3633" if real > orcado else "#1f6feb" 
    
    fig = go.Figure()
    
    # Barra Orçado
    fig.add_trace(go.Bar(
        y=[titulo], x=[orcado], name='Orçado', orientation='h', 
        marker_color='#30363d', 
        text=[f"R$ {orcado:,.0f}"], textposition='auto'
    ))
    
    # Barra Realizado
    fig.add_trace(go.Bar(
        y=[titulo], x=[real], name='Realizado', orientation='h', 
        marker_color=cor_real,
        text=[f"R$ {real:,.0f}"], textposition='auto'
    ))

    # PONTO 3: Gráficos fixos
    fig.update_layout(
        title=dict(text=f"<b>{titulo}</b> <span style='color:#8b949e; font-size:14px'>- Consumo: {pct:.1f}% do Orçamento</span>", x=0),
        barmode='group', # Barras lado a lado (agrupadas) para ver melhor a diferença
        height=140, # Altura suficiente para ver as duas barras e números
        margin=dict(l=0, r=10, t=40, b=10),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=True, gridcolor='#262730', showticklabels=False, fixedrange=True),
        yaxis=dict(showticklabels=False, fixedrange=True),
        legend=dict(orientation="h", yanchor="bottom", y=1, xanchor="right", x=1, font=dict(color="white")),
        font=dict(color='white')
    )
    return fig

# Um gráfico por linha para máximo detalhe
with st.container(border=True):
    st.plotly_chart(plot_detailed_row("📦 Materiais", dados['Mat_Orc'], dados['Mat_Real']), use_container_width=True, config={'displayModeBar': False})

with st.container(border=True):
    st.plotly_chart(plot_detailed_row("🚗 Despesas", dados['Desp_Orc'], dados['Desp_Real']), use_container_width=True, config={'displayModeBar': False})

with st.container(border=True):
    st.plotly_chart(plot_detailed_row("👷 Mão de Obra (R$)", dados['HH_Orc_Vlr'], dados['HH_Real_Vlr']), use_container_width=True, config={'displayModeBar': False})
