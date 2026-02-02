import streamlit as st
import streamlit_authenticator as stauth
import yaml

# ---------------------------------------------------------
# 1. CONFIGURAÇÃO VISUAL
# ---------------------------------------------------------
st.set_page_config(page_title="Portal TE Engenharia", layout="wide", page_icon="🏗️")

st.markdown("""
<style>
    /* Fundo geral */
    .stApp {background-color: #0e1117;}
    
    /* --- 1. BOTÃO DE LOGIN (AZUL E GRANDE) --- */
    /* Este estilo só se aplica ao botão DENTRO do cartão de login */
    [data-testid="stForm"] .stButton button {
        background-color: #58a6ff !important;
        color: white !important;
        border: none !important;
        font-weight: bold !important;
        width: 100%; /* Login fica largura total */
        margin-top: 10px;
        transition: all 0.2s ease;
    }
    [data-testid="stForm"] .stButton button:hover {
        background-color: #79c0ff !important;
    }

    /* --- 2. BOTÃO DA SIDEBAR (RESET TOTAL PARA PADRÃO) --- */
    /* Forçamos o botão da barra lateral a ser pequeno e discreto */
    section[data-testid="stSidebar"] .stButton button {
        background-color: transparent !important;
        border: 1px solid #4a4a4a !important;
        color: #fafafa !important;
        width: auto !important; /* <--- ISSO IMPEDE QUE ELE MUDE DE TAMANHO SOZINHO */
        padding-left: 15px !important;
        padding-right: 15px !important;
    }
    
    /* Efeito ao passar o mouse no botão da sidebar */
    section[data-testid="stSidebar"] .stButton button:hover {
        border-color: #ff4b4b !important; /* Um vermelho sutil para indicar saída */
        color: #ff4b4b !important;
        background-color: rgba(255, 75, 75, 0.1) !important;
    }

    /* --- 3. CARD DE LOGIN --- */
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

    /* Inputs do Login */
    .stTextInput input {
        background-color: #0d1117 !important;
        border: 1px solid #30363d !important;
        color: white !important;
    }
    
    /* Mensagens de erro */
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

authenticator.login(location='main')

# ---------------------------------------------------------
# 4. LÓGICA DO SISTEMA
# ---------------------------------------------------------

if st.session_state.get("authentication_status"):
    
    # === USUÁRIO LOGADO ===
    
    pg = st.navigation([
        st.Page("dashboard_visao_geral.py", title="Visão Geral", icon="🏢"),
        st.Page("dashboard_detalhado.py", title="Detalhamento de Obra", icon="📝"),
        st.Page("configuracoes.py", title="Configurações", icon="⚙️"),
    ])
    
    pg.run()

    with st.sidebar:
        st.divider()
        authenticator.logout('Desconectar', 'sidebar') 

elif st.session_state.get("authentication_status") is False:
    st.error('Usuário ou senha incorretos.')

elif st.session_state.get("authentication_status") is None:
    st.markdown('<style>header {visibility: hidden;}</style>', unsafe_allow_html=True)
    pass
