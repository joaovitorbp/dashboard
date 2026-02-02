import streamlit as st
import streamlit_authenticator as stauth
import yaml

# ---------------------------------------------------------
# 1. CONFIGURAÇÃO VISUAL E CSS (DEFINITIVO)
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

    /* --- SIDEBAR FLEXÍVEL (LAYOUT TOPO/FUNDO) --- */
    
    /* 1. Faz a área de conteúdo do usuário ocupar a altura total */
    section[data-testid="stSidebar"] > div {
        height: 100vh;
    }
    
    /* 2. Configura o container interno como Flex Column */
    [data-testid="stSidebarUserContent"] {
        display: flex;
        flex-direction: column;
        height: 100%;
    }
    
    /* 3. O PULO DO GATO: */
    /* Seleciona o ÚLTIMO container dentro da sidebar (nosso rodapé) */
    /* e aplica margem automática no topo, empurrando-o para o final */
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
# 4. LÓGICA DE ORGANIZAÇÃO (AQUI ESTÁ O LAYOUT)
# ---------------------------------------------------------

if st.session_state.get("authentication_status"):
    
    # === PARTE 1: MENU NAVEGAÇÃO (AUTOMÁTICO NO TOPO) ===
    pg = st.navigation([
        st.Page("dashboard_visao_geral.py", title="Visão Geral", icon="🏢"),
        st.Page("dashboard_detalhado.py", title="Detalhamento de Obra", icon="📝"),
        st.Page("configuracoes.py", title="Configurações", icon="⚙️"),
    ])

    # === PARTE 2: SEPARADOR SUPERIOR ===
    # Colocamos isso ANTES de rodar a página, para ficar acima do Selectbox
    with st.sidebar:
        st.divider() # <--- O SEPARADOR DE CIMA

    # === PARTE 3: CONTEÚDO DA PÁGINA (SELETOR DE PROJETO) ===
    # Ao rodar a página, se ela tiver um sidebar.selectbox, 
    # ele aparecerá logo abaixo do divider que criamos acima.
    pg.run()

    # === PARTE 4: RODAPÉ (PRESO NO FUNDO) ===
    with st.sidebar:
        # IMPORTANTE: Usamos st.container para agrupar Linha + Botão
        # O CSS 'last-child' vai pegar esse container inteiro e jogar pro chão
        with st.container():
            st.divider() # <--- O SEPARADOR DE BAIXO
            authenticator.logout('Desconectar', 'sidebar') 
    
elif st.session_state.get("authentication_status") is False:
    st.error('Usuário ou senha incorretos.')

elif st.session_state.get("authentication_status") is None:
    st.markdown('<style>header {visibility: hidden;}</style>', unsafe_allow_html=True)
    pass
