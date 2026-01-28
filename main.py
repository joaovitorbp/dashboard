import streamlit as st

# Configuração da Página Principal
st.set_page_config(page_title="Portal TE Engenharia", layout="wide", page_icon="🏗️")

# Definição do Menu de Navegação
pg = st.navigation([
    st.Page("dashboard_visao_geral.py", title="Visão Geral", icon="🏢"),
    st.Page("dashboard_detalhado.py", title="Detalhamento de Obra", icon="📝"),
])

# Executa a navegação
pg.run()
