import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ---------------------------------------------------------
# 1. CONFIGURAÇÃO E ESTILO
# ---------------------------------------------------------
st.set_page_config(layout="wide", page_title="Painel de Obras 360", page_icon="🏗️")

st.markdown("""
<style>
    .block-container {padding-top: 2rem; padding-bottom: 3rem;}
    h3 {color: #1f2937; font-weight: 700;}
    [data-testid="stMetricValue"] {font-size: 1.8rem !important; color: #111827;}
    [data-testid="stMetricLabel"] {font-size: 1rem !important; color: #6b7280;}
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

dados = df_raw[df_raw['Projeto'] == projeto_sel].iloc[0]

# ---------------------------------------------------------
# 4. CÁLCULOS
# ---------------------------------------------------------
custo_total = dados['Mat_Real'] + dados['Desp_Real'] + dados['HH_Real_Vlr'] + dados['Impostos']
lucro_liquido = dados['Vendido'] - custo_total
margem_real_pct = (lucro_liquido / dados['Vendido']) * 100 if dados['Vendido'] > 0 else 0

# ---------------------------------------------------------
# 5. HEADER
# ---------------------------------------------------------
col_a, col_b = st.columns([3, 1])
with col_a:
    st.title(f"{dados['Projeto']}")
    st.markdown(f"**Cliente:** {dados['Cliente']} | **Local:** {dados['Cidade']}")

with col_b:
    st.write("")
    status_map = {"Finalizado": "green", "Em andamento": "blue", "Não iniciado": "gray", "Apresentado": "orange"}
    cor_st = status_map.get(dados['Status'], "gray")
    st.markdown(f"### :{cor_st}[{dados['Status']}]")

st.divider()

# ---------------------------------------------------------
# 6. KPI CARDS (LUCRO LÍQUIDO ATUALIZADO)
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
        # Mudança solicitada: Lucro Líquido no lugar de Custos
        cor_lucro = "normal" if lucro_liquido >= 0 else "inverse"
        st.metric("💵 Lucro Líquido (R$)", f"R$ {lucro_liquido:,.2f}", delta_color=cor_lucro)

with c4:
    with st.container(border=True):
        delta = margem_real_pct - 25
        st.metric("📈 Margem Líquida (%)", f"{margem_real_pct:.1f}%", delta=f"{delta:.1f}% (Meta 25%)")

st.divider()

# ---------------------------------------------------------
# 7. SEÇÃO: COMPOSIÇÃO DE RESULTADO (CASCATA) - FULL WIDTH
# ---------------------------------------------------------
st.subheader("📊 Composição do Resultado")

with st.container(border=True):
    col_tgl, col_chart = st.columns([1, 6])
    
    with col_tgl:
        st.write("")
        st.write("")
        modo_vis = st.radio("Visualizar:", ["Valores (R$)", "Percentual (%)"], label_visibility="collapsed")
    
    with col_chart:
        labels = ["Vendido", "Impostos", "Materiais", "Despesas", "Mão de Obra", "Lucro Líquido"]
        
        if modo_vis == "Valores (R$)":
            vals = [dados['Vendido'], -dados['Impostos'], -dados['Mat_Real'], -dados['Desp_Real'], -dados['HH_Real_Vlr'], lucro_liquido]
            text_vals = [f"R$ {v/1000:.1f}k" for v in vals]
            y_ax = "Valor (R$)"
        else:
            base = dados['Vendido'] if dados['Vendido'] > 0 else 1
            vals = [100, -(dados['Impostos']/base)*100, -(dados['Mat_Real']/base)*100, -(dados['Desp_Real']/base)*100, -(dados['HH_Real_Vlr']/base)*100, (lucro_liquido/base)*100]
            text_vals = [f"{v:.1f}%" for v in vals]
            y_ax = "Percentual (%)"

        fig_water = go.Figure(go.Waterfall(
            orientation = "v",
            measure = ["relative", "relative", "relative", "relative", "relative", "total"],
            x = labels, y = vals, text = text_vals, textposition = "outside",
            connector = {"line":{"color":"#cbd5e1"}},
            decreasing = {"marker":{"color":"#ef4444"}},
            increasing = {"marker":{"color":"#10b981"}},
            totals = {"marker":{"color":"#3b82f6"}}
        ))
        fig_water.update_layout(height=350, margin=dict(t=10, b=0, l=0, r=0), yaxis_title=y_ax)
        st.plotly_chart(fig_water, use_container_width=True)

st.write("") # Espaço

# ---------------------------------------------------------
# 8. SEÇÃO: EFICIÊNCIA OPERACIONAL - FULL WIDTH
# ---------------------------------------------------------
st.subheader("⚙️ Eficiência Operacional (Físico vs Horas)")

with st.container(border=True):
    c_fis, c_hh = st.columns(2)
    
    # Progresso Físico
    with c_fis:
        fisico = dados['Conclusao_%']
        st.write(f"**🏗️ Avanço Físico:** {fisico}%")
        st.progress(fisico/100)
        st.caption("Baseado no cronograma físico medido.")

    # Progresso Horas
    with c_hh:
        hh_orc = dados['HH_Orc_Qtd']
        hh_real = dados['HH_Real_Qtd']
        perc_hh = (hh_real / hh_orc * 100) if hh_orc > 0 else 0
        
        # Cor dinâmica da barra
        if perc_hh > (fisico + 10):
            cor_hh = ":red"
            msg = "⚠️ Consumo alto de horas!"
        elif perc_hh < fisico:
            cor_hh = ":green"
            msg = "✅ Economia de horas."
        else:
            cor_hh = ":blue"
            msg = "⚖️ Dentro do esperado."

        st.write(f"**⏱️ Banco de Horas:** {perc_hh:.1f}% Consumido {cor_hh}[({int(hh_real)}/{int(hh_orc)}h)]")
        st.progress(min(perc_hh/100, 1.0))
        st.caption(msg)

st.write("")

# ---------------------------------------------------------
# 9. SEÇÃO: COMPARATIVOS FINANCEIROS (BULLET CHART MELHORADO)
# ---------------------------------------------------------
st.subheader("📉 Detalhamento de Custos (Orçado vs Realizado)")

c_mat, c_desp, c_mo = st.columns(3)

def plot_bullet(titulo, orcado, real, cor_real="#3b82f6"):
    # Calcula % para exibir no título
    pct = (real / orcado * 100) if orcado > 0 else 0
    cor_final = "#ef4444" if real > orcado else cor_real
    
    fig = go.Figure()

    # Barra de Fundo (Orçado) - Cinza claro, larga
    fig.add_trace(go.Bar(
        y=[''], x=[orcado], name='Orçado',
        orientation='h', marker_color='#e5e7eb',
        width=0.5, # Barra mais grossa
        hoverinfo='x+name'
    ))

    # Barra de Frente (Real) - Colorida, mais fina (efeito bullet)
    fig.add_trace(go.Bar(
        y=[''], x=[real], name='Realizado',
        orientation='h', marker_color=cor_final,
        width=0.25, # Barra mais fina
        hoverinfo='x+name'
    ))

    fig.update_layout(
        title=f"<b>{titulo}</b> <span style='font-size: 14px; color: #666;'>({pct:.0f}%)</span>",
        barmode='overlay', # Sobrepor as barras
        height=180,
        margin=dict(l=10, r=10, t=40, b=10),
        xaxis=dict(showgrid=False, showticklabels=True),
        yaxis=dict(showgrid=False, showticklabels=False),
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig

with c_mat:
    with st.container(border=True):
        st.plotly_chart(plot_bullet("Materiais", dados['Mat_Orc'], dados['Mat_Real'], "#3b82f6"), use_container_width=True)
        st.caption(f"Orçado: R$ {dados['Mat_Orc']/1000:.1f}k | Real: R$ {dados['Mat_Real']/1000:.1f}k")

with c_desp:
    with st.container(border=True):
        st.plotly_chart(plot_bullet("Despesas", dados['Desp_Orc'], dados['Desp_Real'], "#f59e0b"), use_container_width=True)
        st.caption(f"Orçado: R$ {dados['Desp_Orc']/1000:.1f}k | Real: R$ {dados['Desp_Real']/1000:.1f}k")

with c_mo:
    with st.container(border=True):
        st.plotly_chart(plot_bullet("Mão de Obra (R$)", dados['HH_Orc_Vlr'], dados['HH_Real_Vlr'], "#10b981"), use_container_width=True)
        st.caption(f"Orçado: R$ {dados['HH_Orc_Vlr']/1000:.1f}k | Real: R$ {dados['HH_Real_Vlr']/1000:.1f}k")
