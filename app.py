import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ---------------------------------------------------------
# 1. CONFIGURAÇÃO
# ---------------------------------------------------------
st.set_page_config(layout="wide", page_title="Painel de Obras 360", page_icon="🏗️")

# CSS para ajuste visual
st.markdown("""
<style>
    .block-container {padding-top: 1.5rem; padding-bottom: 1rem;}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. CARREGAMENTO DE DADOS
# ---------------------------------------------------------
@st.cache_data
def load_data():
    # O arquivo deve estar na mesma pasta do GitHub que este script
    return pd.read_excel("dados_obras_v3.xlsx")

try:
    df_raw = load_data()
except FileNotFoundError:
    st.error("⚠️ O arquivo 'dados_obras_v3.xlsx' não foi encontrado. Certifique-se de que você fez o upload dele para o GitHub na mesma pasta do app.py.")
    st.stop()
except Exception as e:
    st.error(f"Erro ao ler o arquivo: {e}")
    st.stop()

# ---------------------------------------------------------
# 3. SIDEBAR
# ---------------------------------------------------------
st.sidebar.title("Gestão de Obras")
projetos = df_raw['Projeto'].unique()
projeto_sel = st.sidebar.selectbox("📂 Selecione o Projeto:", projetos)

# Filtrar dados
dados = df_raw[df_raw['Projeto'] == projeto_sel].iloc[0]

# ---------------------------------------------------------
# 4. CÁLCULOS
# ---------------------------------------------------------
custo_total = dados['Mat_Real'] + dados['Desp_Real'] + dados['HH_Real_Vlr'] + dados['Impostos']
lucro_liquido = dados['Vendido'] - custo_total
margem_real_pct = (lucro_liquido / dados['Vendido']) * 100 if dados['Vendido'] > 0 else 0

# ---------------------------------------------------------
# 5. DASHBOARD
# ---------------------------------------------------------
# Cabeçalho
col_tit, col_status = st.columns([3, 1])
with col_tit:
    st.title(f"{dados['Projeto']} | {dados['Cliente']}")
    st.caption(f"📍 {dados['Cidade']} | Contrato: R$ {dados['Vendido']:,.2f}")

with col_status:
    cores = {"Finalizado": "green", "Em andamento": "blue", "Não iniciado": "gray"}
    cor = cores.get(dados['Status'], "gray")
    st.markdown(f"### :{cor}[{dados['Status']}]")

st.divider()

# KPIs Macro
k1, k2, k3, k4 = st.columns(4)
k1.metric("💰 Valor Vendido", f"R$ {dados['Vendido']:,.2f}")
k2.metric("📝 Faturado", f"R$ {dados['Faturado']:,.2f}")
k3.metric("📉 Custo Total", f"R$ {custo_total:,.2f}")
k4.metric("📈 Margem Real", f"{margem_real_pct:.1f}%", delta=f"{margem_real_pct-25:.1f}% (Meta)", delta_color="normal")

# Eficiência e Gráficos
st.divider()
st.subheader("⚙️ Eficiência Operacional")

c_fis, c_hh, c_msg = st.columns([2,2,2])

with c_fis:
    st.write("**Conclusão Física**")
    st.progress(dados['Conclusao_%']/100)
    st.caption(f"{dados['Conclusao_%']}% Concluído")

with c_hh:
    perc_hh = (dados['HH_Real_Qtd'] / dados['HH_Orc_Qtd'] * 100) if dados['HH_Orc_Qtd'] > 0 else 0
    st.write(f"**Consumo Horas** ({int(dados['HH_Real_Qtd'])}/{int(dados['HH_Orc_Qtd'])})")
    st.progress(min(perc_hh/100, 1.0))
    st.caption(f"{perc_hh:.1f}% Consumido")

with c_msg:
    st.write("")
    if perc_hh > (dados['Conclusao_%'] + 15):
        st.error("⚠️ Consumo de horas muito acima do físico!")
    elif perc_hh > dados['Conclusao_%']:
        st.warning("⚠️ Consumo de horas levemente acima.")
    else:
        st.success("✅ Eficiência Operacional OK.")

st.divider()

# Gráfico Cascata
st.subheader("📊 Composição do Resultado")
fig = go.Figure(go.Waterfall(
    name = "Financeiro", orientation = "v",
    measure = ["relative", "relative", "relative", "relative", "relative", "total"],
    x = ["Vendido", "Impostos", "Materiais", "Despesas", "M.O. (R$)", "Lucro"],
    y = [dados['Vendido'], -dados['Impostos'], -dados['Mat_Real'], -dados['Desp_Real'], -dados['HH_Real_Vlr'], lucro_liquido],
    connector = {"line":{"color":"rgb(63, 63, 63)"}},
    decreasing = {"marker":{"color":"#ef4444"}},
    increasing = {"marker":{"color":"#10b981"}},
    totals = {"marker":{"color":"#3b82f6"}}
))
st.plotly_chart(fig, use_container_width=True)
