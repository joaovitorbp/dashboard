import streamlit as st

# ---------------------------------------------------------
# CONFIGURAÇÃO INICIAL
# ---------------------------------------------------------
st.set_page_config(page_title="Portal TE Engenharia", layout="wide", page_icon="🏗️")

# Estilos CSS globais (Opcional)
st.markdown("""
<style>
    .stApp {background-color: #0e1117;}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# NAVEGAÇÃO
# ---------------------------------------------------------
# Definição das Páginas
pg = st.navigation([
    st.Page("dashboard_visao_geral.py", title="Visão Geral", icon="🏢"),
    st.Page("dashboard_detalhado.py", title="Detalhamento de Obra", icon="📝"),
    st.Page("configuracoes.py", title="Configurações", icon="⚙️"),
])

# Executa a navegação
pg.run()
