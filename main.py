st.markdown("""
<style>
    /* 1. CORREÇÃO GLOBAL DE SCROLL (Evita o pulo da tela) */
    .stApp {
        background-color: #0e1117;
        overflow-y: scroll; 
    }
    
    /* 2. TRAVAMENTO TOTAL DO BOTÃO DA SIDEBAR */
    section[data-testid="stSidebar"] .stButton {
        width: 100% !important; /* Trava o container do botão */
    }
    
    section[data-testid="stSidebar"] .stButton button {
        background-color: transparent !important;
        border: 1px solid #4a4a4a !important;
        color: #fafafa !important;
        
        /* AQUI ESTÁ O SEGREDO DO TRAVAMENTO: */
        width: 100% !important;
        min-width: 100% !important;
        max-width: 100% !important;
        box-sizing: border-box !important; /* Garante que a borda não aumente o tamanho */
        display: block !important;
        margin: 0px !important;
    }
    
    section[data-testid="stSidebar"] .stButton button:hover {
        border-color: #ff4b4b !important;
        color: #ff4b4b !important;
        background-color: rgba(255, 75, 75, 0.1) !important;
    }

    /* 3. BOTÃO DE LOGIN (AZUL) */
    [data-testid="stForm"] .stButton button {
        background-color: #58a6ff !important;
        color: white !important;
        border: none !important;
        font-weight: bold !important;
        width: 100%;
        margin-top: 10px;
    }
    [data-testid="stForm"] .stButton button:hover {
        background-color: #79c0ff !important;
    }

    /* 4. CARD DE LOGIN */
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
    .stTextInput input {
        background-color: #0d1117 !important;
        border: 1px solid #30363d !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)
