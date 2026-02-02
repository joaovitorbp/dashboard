import streamlit as st
import streamlit_authenticator as stauth
import yaml

# ---------------------------------------------------------
# 1. CONFIGURAÇÃO VISUAL
# ---------------------------------------------------------
st.set_page_config(page_title="Portal TE Engenharia", layout="wide", page_icon="🏗️")

st.markdown("""
<style>
    .stApp {background-color: #0e1117;}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. PREPARAÇÃO DOS DADOS (EVITANDO ERROS DE VERSÃO)
# ---------------------------------------------------------
secrets = st.secrets

# Montamos o dicionário manualmente para evitar erro de "Proxy" do Streamlit
# e para garantir que a estrutura esteja correta para a biblioteca
config_dict = {
    "credentials": {
        "usernames": {
            username: dict(user_data) 
            for username, user_data in secrets['credentials']['usernames'].items()
        }
    },
    "cookie": dict(secrets['cookie']),
    "preauthorized": list(secrets['preauthorized']['emails'])
}

# ---------------------------------------------------------
# 3. AUTENTICAÇÃO
# ---------------------------------------------------------
# Tenta inicializar de forma compatível com múltiplas versões
try:
    authenticator = stauth.Authenticate(
        config_dict['credentials'],
        config_dict['cookie']['name'],
        config_dict['cookie']['key'],
        config_dict['cookie']['expiry_days'],
        config_dict['preauthorized']
    )
except TypeError:
    # Fallback para versões muito novas que mudaram a assinatura
    authenticator = stauth.Authenticate(
        config_dict['credentials'],
        config_dict['cookie']['name'],
        config_dict['cookie']['key'],
        config_dict['cookie']['expiry_days']
    )

authenticator.login()

# ---------------------------------------------------------
# 4. VERIFICAÇÃO E NAVEGAÇÃO
# ---------------------------------------------------------
if st.session_state.get("authentication_status"):
    
    # === LOGADO ===
    with st.sidebar:
        st.write(f"👋 Olá, *{st.session_state['name']}*")
        authenticator.logout('Sair', 'sidebar')
        st.divider()
    
    pg = st.navigation([
        st.Page("dashboard_visao_geral.py", title="Visão Geral", icon="🏢"),
        st.Page("dashboard_detalhado.py", title="Detalhamento de Obra", icon="📝"),
        st.Page("configuracoes.py", title="Configurações", icon="⚙️"),
    ])
    pg.run()

elif st.session_state.get("authentication_status") is False:
    st.error('Usuário ou senha incorretos. (Usuário é "admin")')

elif st.session_state.get("authentication_status") is None:
    st.warning('Faça login para continuar.')
