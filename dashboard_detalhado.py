# ---------------------------------------------------------
# SIDEBAR NAVEGAÇÃO INTERNA
# ---------------------------------------------------------
st.sidebar.markdown("### Seleção de Obra")
lista_projetos = sorted(df_raw['Projeto'].unique())

# Lógica Inteligente: Verifica se veio da Home com um projeto selecionado
index_padrao = 0
if "projeto_foco" in st.session_state:
    try:
        # Tenta achar o índice do projeto que foi clicado lá na Home
        index_padrao = lista_projetos.index(st.session_state["projeto_foco"])
    except ValueError:
        index_padrao = 0

# Cria o selectbox já com o valor pré-selecionado
id_projeto = st.sidebar.selectbox("Projeto:", lista_projetos, index=index_padrao)

# Filtra os dados
dados = df_raw[df_raw['Projeto'] == id_projeto].iloc[0]
