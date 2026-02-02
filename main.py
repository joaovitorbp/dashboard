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
    
    /* --- REMOVE ESPAÇO DO TOPO DA SIDEBAR --- */
    section[data-testid="stSidebar"] .block-container {
        padding-top: 2rem !important;
        padding-bottom: 0rem !important;
    }

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
    
    /* --- BOTÃO DE ENTRAR --- */
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

    /* --- CORREÇÃO DA SIDEBAR (O PULO DO GATO) --- */
    
    /* 1. Define a Sidebar como uma coluna Flexível */
    section[data-testid="stSidebar"] > div {
        height: 100%;
        display: flex;
        flex-direction: column;
    }
    
    /* 2. Área de Conteúdo do Usuário (Onde ficam Selectbox e Botão) */
    [data-testid="stSidebarUserContent"] {
        display: flex;
        flex-direction: column;
        flex-grow: 1; /* Ocupa todo o espaço vertical disponível */
        /* Removemos o margin-top: auto daqui, pois ele empurrava tudo */
    }
    
    /* 3. Apenas o ÚLTIMO container (nosso rodapé) vai para o fundo */
    [data-testid="stSidebarUserContent"] > div:last-child {
        margin-top: auto;
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
# 4. LÓGICA DO SISTEMA (ORDEM CORRIGIDA)
# ---------------------------------------------------------

if st.session_state.get("authentication_status"):
    
    # === 1. DEFINIÇÃO DAS PÁGINAS ===
    pg = st.navigation([
        st.Page("dashboard_visao_geral.py", title="Visão Geral", icon="🏢"),
        st.Page("dashboard_detalhado.py", title="Detalhamento de Obra", icon="📝"),
        st.Page("configuracoes.py", title="Configurações", icon="⚙️"),
    ])

    # === 2. EXECUTAR A PÁGINA (ISSO CRIA O SELETOR DE OBRAS) ===
    # Executamos o pg.run() ANTES do rodapé. 
    # Assim, o seletor entra na sidebar primeiro (no topo).
    pg.run()

    # === 3. CRIAR O RODAPÉ (ISSO VAI PARA O FUNDO) ===
    with st.sidebar:
        # Usamos um container para agrupar a linha e o botão
        # O CSS 'last-child' vai pegar esse container e jogar pro fundo
        with st.container():
            st.divider()
            authenticator.logout('Desconectar', 'sidebar') 
    
elif st.session_state.get("authentication_status") is False:
    st.error('Usuário ou senha incorretos.')

elif st.session_state.get("authentication_status") is None:
    st.markdown('<style>header {visibility: hidden;}</style>', unsafe_allow_html=True)
    pass
