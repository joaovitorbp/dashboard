import streamlit as st
import streamlit_authenticator as stauth
import yaml

# ---------------------------------------------------------
# 1. CONFIGURAÇÃO VISUAL E CSS (AGORA COM SIDEBAR FIXO)
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

    /* --- CORREÇÃO DA SIDEBAR (BOTÃO NO RODAPÉ) --- */
    
    /* 1. Transforma a Sidebar em um container Flexível */
    section[data-testid="stSidebar"] > div {
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between; /* Empurra o conteúdo para as extremidades */
    }
    
    /* 2. Estiliza a área onde fica o botão de sair (User Content) */
    [data-testid="stSidebarUserContent"] {
        padding-bottom: 20px; /* Espaço na base */
        border-top: 1px solid #30363d; /* A LINHA SEPARADORA ÚNICA */
        padding-top: 20px; /* Espaço entre a linha e o botão */
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
    
    # === ÁREA LOGADA ===
    
    # 1. Definimos as páginas (Isso vai para o TOPO da sidebar automaticamente)
    pg = st.navigation([
        st.Page("dashboard_visao_geral.py", title="Visão Geral", icon="🏢"),
        st.Page("dashboard_detalhado.py", title="Detalhamento de Obra", icon="📝"),
        st.Page("configuracoes.py", title="Configurações", icon="⚙️"),
    ])

    # 2. Sidebar (Isso vai para o FUNDO da sidebar graças ao CSS)
    with st.sidebar:
        # Repare que NÃO tem st.divider() aqui, o CSS faz a borda
        authenticator.logout('Desconectar', 'sidebar') 
    
    # 3. Executa a página
    pg.run()

elif st.session_state.get("authentication_status") is False:
    st.error('Usuário ou senha incorretos.')

elif st.session_state.get("authentication_status") is None:
    pass
