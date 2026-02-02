import streamlit as st
import streamlit_authenticator as stauth

# ---------------------------------------------------------
# CONFIGURAÇÃO INICIAL
# ---------------------------------------------------------
st.set_page_config(page_title="Portal TE Engenharia", layout="wide", page_icon="🏗️")

st.markdown("""
<style>
    .stApp {background-color: #0e1117;}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# SISTEMA DE LOGIN (VIA SECRETS)
# ---------------------------------------------------------
# Lê as configurações que você salvou no site do Streamlit
config = st.secrets

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

# Cria a tela de login (Username será 'admin')
authenticator.login()

# ---------------------------------------------------------
# LÓGICA DE ACESSO
# ---------------------------------------------------------
if st.session_state["authentication_status"]:
    
    # === SE O LOGIN DER CERTO, MOSTRA O SISTEMA ===
    with st.sidebar:
        # Mostra o botão de Sair
        authenticator.logout('Sair', 'sidebar')
        st.divider()
    
    # Define as páginas do sistema
    pg = st.navigation([
        st.Page("dashboard_visao_geral.py", title="Visão Geral", icon="🏢"),
        st.Page("dashboard_detalhado.py", title="Detalhamento de Obra", icon="📝"),
        st.Page("configuracoes.py", title="Configurações", icon="⚙️"),
    ])
    
    # Roda o site
    pg.run()

elif st.session_state["authentication_status"] is False:
    # === SENHA ERRADA ===
    st.error('Usuário ou senha incorretos')

elif st.session_state["authentication_status"] is None:
    # === AGUARDANDO LOGIN ===
    st.warning('Por favor, faça login para acessar o sistema.')
