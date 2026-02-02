import streamlit as st
import streamlit_authenticator as stauth
import yaml

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
# SISTEMA DE LOGIN (COM CORREÇÃO DE ERRO)
# ---------------------------------------------------------
# 1. Carregar os segredos
secrets = st.secrets

# 2. CONVERTER PARA DICIONÁRIO EDITÁVEL (O PULO DO GATO 🐈)
# Isso evita o erro "Secrets does not support item assignment"
credentials = dict(secrets['credentials'])
cookie = secrets['cookie']
preauthorized = secrets['preauthorized']

# 3. Inicializar o Autenticador
authenticator = stauth.Authenticate(
    credentials,
    cookie['name'],
    cookie['key'],
    cookie['expiry_days'],
    preauthorized
)

# 4. Criar o Widget de Login
# O parâmetro 'fields' é opcional dependendo da versão, 
# mas chamar login() sem argumentos geralmente funciona na maioria.
authenticator.login()

# ---------------------------------------------------------
# LÓGICA DE ACESSO
# ---------------------------------------------------------
if st.session_state["authentication_status"]:
    
    # === SE O LOGIN DER CERTO ===
    
    # Menu Lateral com Logout
    with st.sidebar:
        st.write(f"👋 Olá, *{st.session_state['name']}*")
        authenticator.logout('Sair', 'sidebar')
        st.divider()
    
    # Navegação do Sistema
    pg = st.navigation([
        st.Page("dashboard_visao_geral.py", title="Visão Geral", icon="🏢"),
        st.Page("dashboard_detalhado.py", title="Detalhamento de Obra", icon="📝"),
        st.Page("configuracoes.py", title="Configurações", icon="⚙️"),
    ])
    
    pg.run()

elif st.session_state["authentication_status"] is False:
    st.error('Usuário ou senha incorretos')

elif st.session_state["authentication_status"] is None:
    st.warning('Por favor, faça login para acessar o sistema.')
