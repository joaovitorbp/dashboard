import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ---------------------------------------------------------
# 1. CONFIGURAÇÃO E ESTILO
# ---------------------------------------------------------
st.set_page_config(layout="wide", page_title="Gestão de Obras", page_icon="🏗️")

st.markdown("""
<style>
    .stApp {background-color: #0e1117;}
    .block-container {padding-top: 2rem; padding-bottom: 3rem;}
    
    /* Remove barra de ferramentas do Plotly */
    .js-plotly-plot .plotly .modebar {display: none !important;}
    
    /* Estilo Cards KPI */
    .kpi-card {
        background-color: #1c1f26;
        border: 1px solid #2d333b;
        border-radius: 8px;
        padding: 15px;
        text-align: left;
    }
    .kpi-label {color: #8b949e; font-size: 0.9rem; margin-bottom: 5px;}
    .kpi-value {font-size: 1.8rem; font-weight: 600; color: #ffffff;}
    
    /* Títulos */
    h1, h2, h3 {color: #f0f6fc !important;}
    p, label, span, div {color: #e6edf3 !important;}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. FUNÇÕES ÚTEIS
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
# 3. SIDEBAR
# ---------------------------------------------------------
st.sidebar.title("Navegação")
lista_projetos = sorted(df_raw['Projeto'].unique())
id_projeto = st.sidebar.selectbox("Selecione o Projeto:", lista_projetos)
dados = df_raw[df_raw['Projeto'] == id_projeto].iloc[0]

# ---------------------------------------------------------
# 4. CÁLCULOS
# ---------------------------------------------------------
custo_total = dados['Mat_Real'] + dados['Desp_Real'] + dados['HH_Real_Vlr'] + dados['Impostos']
lucro_liquido = dados['Vendido'] - custo_total
margem_real_pct = (lucro_liquido / dados['Vendido']) * 100 if dados['Vendido'] > 0 else 0
META_MARGEM = 25.0

# ---------------------------------------------------------
# 5. HEADER
# ---------------------------------------------------------
c_head, c_status = st.columns([3, 1])
with c_head:
    st.title(f"{dados['Projeto']} - {dados['Descricao']}")
    st.markdown(f"**Cliente:** {dados['Cliente']} | **Local:** {dados['Cidade']}")

with c_status:
    st.write("")
    st.write("")
    cor_map = {"Finalizado": "#238636", "Em andamento": "#1f6feb", "Não iniciado": "#8b949e"}
    cor_bg = cor_map.get(dados['Status'], "#30363d")
    st.markdown(f"""<div style="background-color:{cor_bg};color:white;padding:6px 12px;border-radius:20px;text-align:center;font-weight:600;display:inline-block;float:right;">{dados['Status'].upper()}</div>""", unsafe_allow_html=True)

st.divider()

# ---------------------------------------------------------
# 6. KPI CARDS
# ---------------------------------------------------------
def criar_card(titulo, valor, cor_texto="#ffffff"):
    st.markdown(f"""<div class="kpi-card"><div class="kpi-label">{titulo}</div><div class="kpi-value" style="color:{cor_texto}">{valor}</div></div>""", unsafe_allow_html=True)

k1, k2, k3, k4 = st.columns(4)
with k1: criar_card("Valor Vendido", format_currency(dados['Vendido']))
with k2: criar_card("Valor Faturado", format_currency(dados['Faturado']))

cor_lucro = "#2ea043" if lucro_liquido >= 0 else "#da3633"
cor_margem = "#2ea043" if margem_real_pct >= META_MARGEM else "#da3633"

with k3: criar_card("Lucro", format_currency(lucro_liquido), cor_lucro)
with k4: criar_card("Margem de Lucro", format_percent(margem_real_pct), cor_margem)

st.write("")

# ---------------------------------------------------------
# 7. SEÇÃO 1: EFICIÊNCIA OPERACIONAL (ALINHAMENTO VERTICAL)
# ---------------------------------------------------------
st.subheader("⚙️ Eficiência Operacional")

with st.container(border=True):
    # AJUSTE: 'vertical_alignment="center"' centraliza o minicard no eixo Y
    col_gauges, col_spacer, col_diag = st.columns([5, 0.2, 3], vertical_alignment="center")
    
    with col_gauges:
        fig_gauge = go.Figure()

        # Gauge 1: Físico
        fig_gauge.add_trace(go.Indicator(
            mode = "gauge+number", value = dados['Conclusao_%'],
            title = {'text': "Avanço Físico", 'font': {'size': 14}},
            domain = {'x': [0, 0.45], 'y': [0, 1]},
            number = {'suffix': "%"},
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
            title = {'text': "Consumo Horas", 'font': {'size': 14}},
            domain = {'x': [0.55, 1], 'y': [0, 1]},
            number = {'suffix': "%", 'valueformat': ".1f"},
            gauge = {
                'axis': {'range': [0, max(100, perc_hh)], 'tickcolor': "white"},
                'bar': {'color': cor_hh},
                'bgcolor': "#0d1117", 'borderwidth': 2, 'bordercolor': "#30363d",
                'threshold': {'line': {'color': "white", 'width': 3}, 'thickness': 0.75, 'value': dados['Conclusao_%']}
            }
        ))
        
        fig_gauge.update_layout(
            height=220, margin=dict(t=40, b=20, l=30, r=30), 
            paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"},
            xaxis={'fixedrange': True}, yaxis={'fixedrange': True}
        )
        st.plotly_chart(fig_gauge, use_container_width=True, config={'displayModeBar': False})

    with col_diag:
        # AJUSTE: Removido o título antigo e mantido apenas o card limpo
        saldo_hh = hh_orc - hh_real
        
        if perc_hh > (dados['Conclusao_%'] + 10):
            border_c = "#da3633" # Vermelho
            titulo = "Consumo Crítico"
            texto = f"O consumo de horas ({perc_hh:.0f}%) ultrapassou o avanço físico em mais de 10%."
            saldo_txt = f"Excedente: {int(hh_real - hh_orc)}h"
        elif perc_hh < dados['Conclusao_%']:
            border_c = "#238636" # Verde
            titulo = "Eficiência Alta"
            texto = "A obra está avançada em relação ao consumo de horas planejado."
            saldo_txt = f"Saldo: {int(saldo_hh)}h"
        else:
            border_c = "#1f6feb" # Azul
            titulo = "Equilibrado"
            texto = "O ritmo de trabalho segue alinhado ao cronograma físico."
            saldo_txt = f"Saldo: {int(saldo_hh)}h"

        st.markdown(f"""
        <div style="background-color: #161b22; border-left: 4px solid {border_c}; padding: 15px; border-radius: 4px;">
            <strong style="color: {border_c}; font-size: 1.1rem;">{titulo}</strong><br>
            <span style="color: #8b949e; font-size: 0.9rem;">{texto}</span><br><br>
            <strong style="color: white;">{saldo_txt}</strong>
        </div>
        """, unsafe_allow_html=True)

st.write("")

# ---------------------------------------------------------
# 8. SEÇÃO 2: COMPOSIÇÃO DE RESULTADO
# ---------------------------------------------------------
st.subheader("📊 Composição do Lucro")

with st.container(border=True):
    modo_vis = st.radio("Unidade de Medida:", ["Percentual (%)", "Valores (R$)"], horizontal=True, label_visibility="collapsed")
    
    labels = ["Vendido", "Impostos", "Materiais", "Despesas", "Mão de Obra", "Lucro"]
    
    if modo_vis == "Valores (R$)":
        vals = [dados['Vendido'], -dados['Impostos'], -dados['Mat_Real'], -dados['Desp_Real'], -dados['HH_Real_Vlr'], lucro_liquido]
        text_vals = [format_currency(v).replace("R$ ", "") for v in vals]
    else:
        base = dados['Vendido'] if dados['Vendido'] > 0 else 1
        vals = [100, -(dados['Impostos']/base)*100, -(dados['Mat_Real']/base)*100, -(dados['Desp_Real']/base)*100, -(dados['HH_Real_Vlr']/base)*100, (lucro_liquido/base)*100]
        text_vals = [format_percent(v) for v in vals]

    fig_water = go.Figure(go.Waterfall(
        orientation = "v", measure = ["relative"]*5 + ["total"],
        x = labels, y = vals, text = text_vals, textposition = "outside",
        connector = {"line":{"color":"#484f58"}},
        decreasing = {"marker":{"color":"#da3633"}},
        increasing = {"marker":{"color":"#238636"}},
        totals = {"marker":{"color":"#1f6feb"}},
        cliponaxis = False
    ))
    
    fig_water.update_layout(
        height=320, margin=dict(t=50, b=10, l=10, r=10),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        yaxis=dict(showgrid=True, gridcolor='#30363d', zeroline=False, fixedrange=True),
        xaxis=dict(tickfont=dict(color='white'), fixedrange=True),
        font=dict(color='white')
    )
    st.plotly_chart(fig_water, use_container_width=True, config={'displayModeBar': False})

st.write("")

# ---------------------------------------------------------
# 9. SEÇÃO 3: DETALHAMENTO DE CUSTOS
# ---------------------------------------------------------
st.subheader("📉 Detalhamento de Custos")

def plot_row_fixed(titulo, orcado, real):
    pct = (real / orcado * 100) if orcado > 0 else 0
    cor_real = "#da3633" if real > orcado else "#1f6feb"
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=[titulo], x=[orcado], name='Orçado', orientation='h', 
        marker_color='#30363d', 
        text=[format_currency(orcado)], textposition='outside',
        cliponaxis=False
    ))
    
    fig.add_trace(go.Bar(
        y=[titulo], x=[real], name='Realizado', orientation='h', 
        marker_color=cor_real, 
        text=[format_currency(real)], textposition='outside',
        cliponaxis=False 
    ))

    max_val = max(orcado, real) * 1.35 
    
    fig.update_layout(
        title=dict(text=f"<b>{titulo}</b> <span style='color:#8b949e; font-size:14px'>- Consumo: {format_percent(pct)}</span>", x=0),
        barmode='group',
        height=140,
        margin=dict(l=0, r=20, t=30, b=10),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=True, gridcolor='#262730', showticklabels=False, range=[0, max_val], fixedrange=True),
        yaxis=dict(showticklabels=False, fixedrange=True),
        showlegend=False,
        font=dict(color='white')
    )
    return fig

with st.container(border=True):
    st.plotly_chart(plot_row_fixed("Materiais", dados['Mat_Orc'], dados['Mat_Real']), use_container_width=True, config={'displayModeBar': False})

with st.container(border=True):
    st.plotly_chart(plot_row_fixed("Despesas", dados['Desp_Orc'], dados['Desp_Real']), use_container_width=True, config={'displayModeBar': False})

with st.container(border=True):
    st.plotly_chart(plot_row_fixed("Mão de Obra (R$)", dados['HH_Orc_Vlr'], dados['HH_Real_Vlr']), use_container_width=True, config={'displayModeBar': False})
