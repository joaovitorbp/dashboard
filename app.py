import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ---------------------------------------------------------
# 1. CONFIGURAÇÃO E ESTILO
# ---------------------------------------------------------
st.set_page_config(layout="wide", page_title="Painel de Obras 360", page_icon="🏗️")

# CSS para limpar a interface e dar destaque aos cards
st.markdown("""
<style>
    /* Remove padding excessivo do topo */
    .block-container {padding-top: 2rem; padding-bottom: 2rem;}
    
    /* Estilo para titulos de seção */
    h3 {color: #444; font-weight: 600;}
    
    /* Ajuste de métricas */
    [data-testid="stMetricValue"] {font-size: 1.6rem !important; color: #333;}
    [data-testid="stMetricLabel"] {font-size: 0.9rem !important; color: #666;}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. CARREGAMENTO DE DADOS
# ---------------------------------------------------------
@st.cache_data
def load_data():
    return pd.read_excel("dados_obras_v3.xlsx")

try:
    df_raw = load_data()
except FileNotFoundError:
    st.error("⚠️ Arquivo 'dados_obras_v3.xlsx' não encontrado.")
    st.stop()

# ---------------------------------------------------------
# 3. SIDEBAR
# ---------------------------------------------------------
st.sidebar.title("Navegação")
projetos = df_raw['Projeto'].unique()
projeto_sel = st.sidebar.selectbox("Selecione a Obra:", projetos)

# Filtrar dados
dados = df_raw[df_raw['Projeto'] == projeto_sel].iloc[0]

# ---------------------------------------------------------
# 4. CÁLCULOS (BACKEND)
# ---------------------------------------------------------
custo_total = dados['Mat_Real'] + dados['Desp_Real'] + dados['HH_Real_Vlr'] + dados['Impostos']
lucro_liquido = dados['Vendido'] - custo_total
margem_real_pct = (lucro_liquido / dados['Vendido']) * 100 if dados['Vendido'] > 0 else 0

# ---------------------------------------------------------
# 5. HEADER DO PROJETO
# ---------------------------------------------------------
col_a, col_b = st.columns([3, 1])
with col_a:
    st.title(f"{dados['Projeto']}")
    st.markdown(f"**Cliente:** {dados['Cliente']} | **Local:** {dados['Cidade']}")

with col_b:
    st.write("") # Espaço para alinhar
    status_map = {"Finalizado": "green", "Em andamento": "blue", "Não iniciado": "gray", "Apresentado": "orange"}
    cor_st = status_map.get(dados['Status'], "gray")
    st.markdown(f"### :{cor_st}[{dados['Status']}]")

st.divider()

# ---------------------------------------------------------
# 6. LINHA 1: CARDS FINANCEIROS (VISUAL LIMPO)
# ---------------------------------------------------------
c1, c2, c3, c4 = st.columns(4)

with c1:
    with st.container(border=True):
        st.metric("💰 Valor Vendido", f"R$ {dados['Vendido']:,.2f}")

with c2:
    with st.container(border=True):
        st.metric("📝 Total Faturado", f"R$ {dados['Faturado']:,.2f}")

with c3:
    with st.container(border=True):
        st.metric("📉 Custos Totais", f"R$ {custo_total:,.2f}", help="Soma de Materiais, Despesas, MO e Impostos")

with c4:
    with st.container(border=True):
        delta = margem_real_pct - 25
        st.metric("📈 Margem Líquida", f"{margem_real_pct:.1f}%", delta=f"{delta:.1f}% (Meta 25%)")

st.write("") # Espaçamento

# ---------------------------------------------------------
# 7. LINHA 2: GRÁFICO CASCATA (COM BOTÃO R$/%)
# ---------------------------------------------------------
col_water, col_hh_kpi = st.columns([2, 1])

with col_water:
    st.subheader("Fluxo de Resultado")
    
    # Toggle para mudar visualização
    modo_visualizacao = st.radio("Visualizar em:", ["Valores (R$)", "Porcentagem (%)"], horizontal=True, label_visibility="collapsed")
    
    # Preparar dados do gráfico
    labels = ["Vendido", "Impostos", "Materiais", "Despesas", "Mão de Obra", "Lucro"]
    
    if modo_visualizacao == "Valores (R$)":
        values = [dados['Vendido'], -dados['Impostos'], -dados['Mat_Real'], -dados['Desp_Real'], -dados['HH_Real_Vlr'], lucro_liquido]
        text_vals = [f"R$ {v/1000:.1f}k" for v in values] # Formato 100k
        y_title = "Valor (R$)"
    else:
        # Calcular % em relação ao Vendido
        base = dados['Vendido'] if dados['Vendido'] > 0 else 1
        values = [100, -(dados['Impostos']/base)*100, -(dados['Mat_Real']/base)*100, -(dados['Desp_Real']/base)*100, -(dados['HH_Real_Vlr']/base)*100, (lucro_liquido/base)*100]
        text_vals = [f"{v:.1f}%" for v in values]
        y_title = "Porcentagem (%)"

    fig_water = go.Figure(go.Waterfall(
        name = "Financeiro", orientation = "v",
        measure = ["relative", "relative", "relative", "relative", "relative", "total"],
        x = labels,
        y = values,
        text = text_vals,
        textposition = "outside",
        connector = {"line":{"color":"#cbd5e1"}},
        decreasing = {"marker":{"color":"#ef4444"}}, # Vermelho
        increasing = {"marker":{"color":"#10b981"}}, # Verde
        totals = {"marker":{"color":"#3b82f6"}}       # Azul
    ))
    fig_water.update_layout(height=400, margin=dict(t=30, b=0, l=0, r=0), yaxis_title=y_title)
    st.plotly_chart(fig_water, use_container_width=True)

# ---------------------------------------------------------
# 8. LINHA LATERAL: EFICIÊNCIA HH (Resumo)
# ---------------------------------------------------------
with col_hh_kpi:
    st.subheader("Eficiência HH")
    with st.container(border=True):
        # Dados HH
        hh_total = dados['HH_Orc_Qtd']
        hh_gasto = dados['HH_Real_Qtd']
        perc_hh = (hh_gasto / hh_total * 100) if hh_total > 0 else 0
        fisico = dados['Conclusao_%']
        
        # 1. Comparação Visual Rápida
        st.write("Físico (Obra)")
        st.progress(fisico/100)
        
        st.write("Horas (Consumido)")
        bar_color = "red" if perc_hh > (fisico + 10) else "green" # Lógica visual não nativa, mas o texto ajuda
        st.progress(min(perc_hh/100, 1.0))
        
        # Texto de Diagnóstico
        if perc_hh > (fisico + 10):
            st.error(f"🚨 **Crítico:** Consumo de horas ({perc_hh:.0f}%) está correndo mais que a obra ({fisico}%).")
        elif perc_hh < fisico:
            st.success(f"✅ **Excelente:** Obra avançada ({fisico}%) com economia de horas ({perc_hh:.0f}%).")
        else:
            st.info(f"⚖️ **Equilibrado:** Ritmo dentro do esperado.")
            
        st.divider()
        st.metric("Saldo de Horas", f"{int(hh_total - hh_gasto)} h", help="Horas restantes no orçamento")

st.divider()

# ---------------------------------------------------------
# 9. LINHA 3: DETALHAMENTO COMPARATIVO (ORÇADO x REAL)
# ---------------------------------------------------------
st.subheader("Detalhamento de Custos (Orçado vs Real)")

c_mat, c_desp, c_hh_vlr = st.columns(3)

def plot_horizontal_bar(titulo, orcado, real):
    # Lógica de cor: Vermelho se Real > Orçado
    color = '#ef4444' if real > orcado else '#3b82f6'
    
    fig = go.Figure()
    # Barra Orçado (Fundo Cinza)
    fig.add_trace(go.Bar(
        y=[''], x=[orcado], name='Orçado',
        orientation='h', marker_color='#e2e8f0',
        text=[f"Meta: {orcado/1000:.1f}k"], textposition='auto'
    ))
    # Barra Real (Frente Colorida)
    fig.add_trace(go.Bar(
        y=[''], x=[real], name='Realizado',
        orientation='h', marker_color=color,
        text=[f"Real: {real/1000:.1f}k"], textposition='auto'
    ))
    
    fig.update_layout(
        title=titulo,
        barmode='group', # Barras lado a lado para facilitar comparação
        height=200,
        margin=dict(l=0, r=0, t=30, b=0),
        xaxis=dict(showgrid=False, showticklabels=False), # Limpa eixo X
        yaxis=dict(showgrid=False),
        showlegend=False
    )
    return fig

with c_mat:
    with st.container(border=True):
        st.plotly_chart(plot_horizontal_bar("Materiais", dados['Mat_Orc'], dados['Mat_Real']), use_container_width=True)

with c_desp:
    with st.container(border=True):
        st.plotly_chart(plot_horizontal_bar("Despesas", dados['Desp_Orc'], dados['Desp_Real']), use_container_width=True)

with c_hh_vlr:
    with st.container(border=True):
        st.plotly_chart(plot_horizontal_bar("Mão de Obra (Valor R$)", dados['HH_Orc_Vlr'], dados['HH_Real_Vlr']), use_container_width=True)
