import streamlit as st
import streamlit_authenticator as stauth
import yaml

# ---------------------------------------------------------
# 1. CONFIGURAÇÃO VISUAL E CSS
# ---------------------------------------------------------
st.set_page_config(page_title="Portal TE Engenharia", layout="wide", page_icon="🏗️")

st.markdown("""
<style>
    /* Fundo geral */
    .stApp {background-color: #0e1117;}
    
    /* Remove cabeçalho padrão */
    header {visibility: hidden;}
    
    /* --- CARD DE LOGIN --- */
    [data-testid="stForm"] {
        background-color: #161b22;
        padding: 2rem;
        border-radius: 12px;
        border: 1px solid #30363d;
        box-shadow: 0 10px 25px rgba(0,0,0,0.5);
        max-width: 350px !important;
        margin: 0 auto !important;
        position: relative;
        top: 50px; 
    }

    /* --- INPUTS --- */
    .stTextInput input {
        background-color: #0d1117 !important;
        border: 1px solid #30363d !important;
        color: white !important;
    }
    
    /* --- BOTÃO DE ENTRAR (LOGIN) --- */
    div[data-testid="stForm"] .stButton button {
        background-color: #58a6ff !important;
        color: white !important;
        border: none !important;
        font-weight: bold !important;
        width: 100%;
        margin-top: 10px;
        transition: all 0.2s ease;
    }
    div[data-testid="stForm"] .stButton button:hover {
        background-color: #79c0ff !important;
        box-shadow: 0 4px 10px rgba(88, 166, 255, 0.3);
    }
    
    /* Centraliza mensagens de erro */
    .stAlert {
        max-width: 350px;
        margin: 0 auto;
        position: relative;
        top: 60px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. PREPARAÇÃO DOS DADOS
# ---------------------------------------------------------
secrets = st.secrets

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

# ---------------------------------------------------------
# 4. LÓGICA DE EXIBIÇÃO
# ---------------------------------------------------------

authenticator.login(location='main')

if st.session_state.get("authentication_status"):
    
    # === ÁREA LOGADA (SIDEBAR AJUSTADA) ===
    with st.sidebar:
        # TRUQUE DO ESPAÇAMENTO:
        # Adicionamos uma caixa vazia alta para empurrar o botão para baixo.
        # Ajuste o 'height' (ex: 60vh, 70vh) dependendo da quantidade de itens no menu.
        st.markdown('<div style="height: 65vh;"></div>', unsafe_allow_html=True)
        
        # Botão Renomeado para "Desconectar"
        authenticator.logout('Desconectar', 'sidebar')
    
    # Navegação
    pg = st.navigation([
        st.Page("dashboard_visao_geral.py", title="Visão Geral", icon="🏢"),
        st.Page("dashboard_detalhado.py", title="Detalhamento de Obra", icon="📝"),
        st.Page("configuracoes.py", title="Configurações", icon="⚙️"),
    ])
    pg.run()

elif st.session_state.get("authentication_status") is False:
    st.error('Usuário ou senha incorretos.')

elif st.session_state.get("authentication_status") is None:
    pass
