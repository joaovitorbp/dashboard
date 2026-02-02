import streamlit as st
import streamlit_authenticator as stauth
import yaml

# ---------------------------------------------------------
# 1. CONFIGURAÇÃO VISUAL E CSS (AJUSTE DE ALTURA)
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

    /* --- CORREÇÃO DA SIDEBAR (SEM ROLAGEM) --- */
    
    /* 1. Define o container principal da sidebar para não vazar */
    section[data-testid="stSidebar"] > div {
        height: 100vh;
        overflow: hidden; /* Remove barra de rolagem forçada */
    }
    
    /* 2. Área de Conteúdo (Onde ficam os nossos widgets) */
    /* O PULO DO GATO: Calculamos a altura para ser (Tela - Tamanho do Menu) */
    /* 170px é uma estimativa segura para os 3 links de navegação + logo */
    [data-testid="stSidebarUserContent"] {
        display: flex;
        flex-direction: column;
        height: calc(100vh - 170px); 
    }
    
    /* 3. Empurra o rodapé para o final do espaço disponível */
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
# 4. LÓGICA DO LAYOUT
# ---------------------------------------------------------

if st.session_state.get("authentication_status"):
    
    # 1. Menu de Navegação (Ocupa o topo fixo)
    pg = st.navigation([
        st.Page("dashboard_visao_geral.py", title="Visão Geral", icon="🏢"),
        st.Page("dashboard_detalhado.py", title="Detalhamento de Obra", icon="📝"),
        st.Page("configuracoes.py", title="Configurações", icon="⚙️"),
    ])

    # 2. Inicia o "User Content" (Área flexível abaixo do menu)
    
    # Separador Superior
    with st.sidebar:
        st.divider()

    # Widget de Seleção (Logo abaixo do separador)
    pg.run()

    # Rodapé (Empurrado para baixo pelo CSS)
    with st.sidebar:
        with st.container():
            st.divider()
            authenticator.logout('Desconectar', 'sidebar') 
    
elif st.session_state.get("authentication_status") is False:
    st.error('Usuário ou senha incorretos.')

elif st.session_state.get("authentication_status") is None:
    st.markdown('<style>header {visibility: hidden;}</style>', unsafe_allow_html=True)
    pass
