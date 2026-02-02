import streamlit as st
import streamlit_authenticator as stauth
import yaml

# ---------------------------------------------------------
# 1. CONFIGURAÇÃO VISUAL E CSS (FLEXBOX PURO)
# ---------------------------------------------------------
st.set_page_config(page_title="Portal TE Engenharia", layout="wide", page_icon="🏗️")

st.markdown("""
<style>
    /* Fundo geral */
    .stApp {background-color: #0e1117;}
    
    /* Remove padding excessivo do topo */
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
    
    .stTextInput input {background-color: #0d1117 !important; border: 1px solid #30363d !important; color: white !important;}
    
    div[data-testid="stForm"] .stButton button {
        background-color: #58a6ff !important; color: white !important; border: none !important;
        width: 100%; margin-top: 10px; font-weight: bold !important;
    }
    div[data-testid="stForm"] .stButton button:hover {background-color: #79c0ff !important;}
    
    .stAlert {max-width: 350px; margin: 0 auto; position: relative; top: 60px;}

    /* --- SIDEBAR LAYOUT (A MÁGICA ACONTECE AQUI) --- */
    
    /* 1. Define a Sidebar inteira como uma coluna Flexível que ocupa 100% da tela */
    section[data-testid="stSidebar"] > div {
        height: 100vh;
        display: flex;
        flex-direction: column;
        overflow: hidden; /* Evita barra de rolagem dupla */
    }
    
    /* 2. O Menu de Navegação (stSidebarNav) já fica no topo naturalmente */
    
    /* 3. A Área de Conteúdo do Usuário (onde nós escrevemos) vai preencher TODO o resto */
    [data-testid="stSidebarUserContent"] {
        flex-grow: 1;          /* Ocupa todo o espaço disponível abaixo do menu */
        display: flex;         /* Transforma em container flexível também */
        flex-direction: column;
        overflow-y: auto;      /* Permite rolagem só se o conteúdo for muito grande */
        max-height: 100%;
    }
    
    /* 4. O ÚLTIMO elemento dentro do UserContent será empurrado para o fundo */
    [data-testid="stSidebarUserContent"] > div:last-child {
        margin-top: auto;      /* Empurra para o chão */
        padding-bottom: 20px;
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
# 4. LÓGICA DE ORGANIZAÇÃO
# ---------------------------------------------------------

if st.session_state.get("authentication_status"):
    
    # 1. Menu de Navegação (Fica no Topo automaticamente)
    pg = st.navigation([
        st.Page("dashboard_visao_geral.py", title="Visão Geral", icon="🏢"),
        st.Page("dashboard_detalhado.py", title="Detalhamento de Obra", icon="📝"),
        st.Page("configuracoes.py", title="Configurações", icon="⚙️"),
    ])

    # 2. Início do Conteúdo da Sidebar (Logo abaixo do menu)
    with st.sidebar:
        st.divider() # <--- LINHA SUPERIOR (Entre menu e selectbox)

    # 3. Execução da Página (Aqui entra o Selectbox se a página tiver um)
    # Ele será renderizado logo após o divider acima
    pg.run()

    # 4. Rodapé (Fica no Fundo automaticamente pelo CSS)
    with st.sidebar:
        # Agrupamos Linha + Botão em um container
        # O CSS 'last-child' pega este container e joga para o final da tela
        with st.container():
            st.divider() # <--- LINHA INFERIOR
            authenticator.logout('Desconectar', 'sidebar') 
    
elif st.session_state.get("authentication_status") is False:
    st.error('Usuário ou senha incorretos.')

elif st.session_state.get("authentication_status") is None:
    st.markdown('<style>header {visibility: hidden;}</style>', unsafe_allow_html=True)
    pass
