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
# 2. PREPARAÇÃO DOS DADOS
# ---------------------------------------------------------
secrets = st.secrets

# Montamos o dicionário manualmente para compatibilidade
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
try:
    authenticator = stauth.Authenticate(
        config_dict['credentials'],
        config_dict['cookie']['name'],
        config_dict['cookie']['key'],
        config_dict['cookie']['expiry_days'],
        config_dict['preauthorized']
    )
except TypeError:
    authenticator = stauth.Authenticate(
        config_dict['credentials'],
        config_dict['cookie']['name'],
        config_dict['cookie']['key'],
        config_dict['cookie']['expiry_days']
    )

authenticator.login()

# ---------------------------------------------------------
# 4. NAVEGAÇÃO
# ---------------------------------------------------------
if st.session_state.get("authentication_status"):
    
    # === LOGADO ===
    with st.sidebar:
        # Mostra o nome real configurado no Secrets (ex: "Diretoria TE")
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
    # AVISO REMOVIDO AQUI
    st.error('Usuário ou senha incorretos.')

elif st.session_state.get("authentication_status") is None:
    st.warning('Por favor, faça login para continuar.')
