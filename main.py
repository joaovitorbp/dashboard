import streamlit as st
import streamlit_authenticator as stauth
import yaml

# ---------------------------------------------------------
# 1. CONFIGURAÇÃO VISUAL E CSS (O SEGREDO DO DESIGN)
# ---------------------------------------------------------
st.set_page_config(page_title="Portal TE Engenharia", layout="wide", page_icon="🏗️")

st.markdown("""
<style>
    /* Fundo geral */
    .stApp {background-color: #0e1117;}
    
    /* Remove a barra superior padrão do Streamlit na tela de login */
    header {visibility: hidden;}
    
    /* --- ESTILO DO CARD DE LOGIN --- */
    /* Isso afeta o container onde o formulário está */
    [data-testid="stForm"] {
        background-color: #161b22; /* Cinza um pouco mais claro que o fundo */
        padding: 2rem;
        border-radius: 15px;
        border: 1px solid #30363d;
        box-shadow: 0 10px 25px rgba(0,0,0,0.5); /* Sombra elegante */
    }

    /* --- ESTILO DOS INPUTS --- */
    /* Caixas de texto */
    .stTextInput input {
        background-color: #0d1117 !important;
        border: 1px solid #30363d !important;
        color: white !important;
    }
    
    /* --- ESTILO DO BOTÃO DE ENTRAR --- */
    /* Foca especificamente no botão do formulário */
    div[data-testid="stForm"] button {
        background-color: #58a6ff !important;
        color: white !important;
        border: none !important;
        font-weight: bold !important;
        width: 100%; /* Botão ocupando toda a largura */
        margin-top: 10px;
        transition: all 0.3s ease;
    }
    div[data-testid="stForm"] button:hover {
        background-color: #79c0ff !important;
        box-shadow: 0 4px 10px rgba(88, 166, 255, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. PREPARAÇÃO DOS DADOS
# ---------------------------------------------------------
secrets = st.secrets

# Monta dicionário de credenciais
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

# Inicializa Autenticador
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
# 3. LÓGICA DE EXIBIÇÃO (CENTRALIZADA)
# ---------------------------------------------------------

# Verificamos o status antes de desenhar a tela
# (Isso evita que o login pisque se já estiver logado)
authenticator.login(location='main') 

if st.session_state.get("authentication_status"):
    
    # === SE O LOGIN DER CERTO (ÁREA RESTRITA) ===
    
    # Sidebar só aparece aqui dentro
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
    # === TELA DE ERRO (CENTRALIZADA) ===
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.error('Usuário ou senha incorretos.')

elif st.session_state.get("authentication_status") is None:
    # === TELA DE LOGIN (LAYOUT PERSONALIZADO) ===
    
    # Criamos 3 colunas para empurrar o conteúdo para o meio
    # [1, 2, 1] significa: Espaço Vazio | Conteúdo (Dobro do tamanho) | Espaço Vazio
    # Se quiser mais estreito, use [3, 2, 3]
    
    # O authenticator.login() já foi chamado acima, mas ele renderiza o form automaticamente.
    # Para adicionar o LOGO acima dele, usamos um truque visual:
    # O Streamlit renderiza de cima para baixo. Como o login() é um widget,
    # ele tende a aparecer onde foi chamado.
    
    # Como o componente de login do Streamlit Authenticator é meio "teimoso" para posicionar,
    # vamos injetar um cabeçalho visual logo acima dele usando CSS Hack ou layout.
    
    # NOTA: O authenticator desenha o form sozinho. 
    # Para "enfeitar" a tela de login, adicionamos elementos VISUAIS antes.
    
    col_spacer_L, col_center, col_spacer_R = st.columns([1, 1.5, 1])
    
    with col_center:
        st.markdown("""
            <div style="text-align: center; margin-bottom: -60px; z-index: 999; position: relative; padding-top: 50px;">
                <h1 style="font-size: 3rem;">🏗️</h1>
                <h2 style="color: white; font-weight: 800; letter-spacing: -1px;">TE ENGENHARIA</h2>
                <p style="color: #8b949e; margin-bottom: 20px;">Sistema de Gestão de Obras</p>
            </div>
        """, unsafe_allow_html=True)
        
        # O widget de login aparecerá logo abaixo disso automaticamente
