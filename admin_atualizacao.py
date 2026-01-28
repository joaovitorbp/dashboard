import streamlit as st
from github import Github
import pandas as pd
import io

# Configuração da Página
st.markdown("# 📤 Atualização de Dados")
st.markdown("---")
st.info("ℹ️ Utilize esta página para subir a planilha atualizada. O sistema irá substituir o arquivo no banco de dados e reiniciar automaticamente.")

# Autenticação (Pega os dados do Cofre do Streamlit)
try:
    GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
    REPO_NAME = st.secrets["REPO_NAME"]
    FILE_PATH = st.secrets["FILE_PATH"]
except:
    st.error("❌ Erro de Configuração: As chaves (Secrets) não foram encontradas no Streamlit Cloud.")
    st.stop()

# Botão de Upload
uploaded_file = st.file_uploader("Selecione o arquivo Excel (.xlsx)", type=["xlsx"])

if uploaded_file is not None:
    # Mostra uma prévia para conferência
    try:
        df_preview = pd.read_excel(uploaded_file)
        st.success("✅ Arquivo lido com sucesso!")
        st.write(f"**Linhas encontradas:** {len(df_preview)}")
        
        with st.expander("👀 Ver prévia dos dados"):
            st.dataframe(df_preview.head())
        
        st.divider()
        
        # Botão para Confirmar a Gravação no GitHub
        col_btn, col_info = st.columns([1, 2])
        
        with col_btn:
            btn_confirmar = st.button("🚀 Confirmar e Atualizar", type="primary")
            
        if btn_confirmar:
            status_box = st.status("Iniciando processo de atualização...", expanded=True)
            
            try:
                # 1. Conecta no GitHub
                status_box.write("🔌 Conectando ao GitHub...")
                g = Github(GITHUB_TOKEN)
                repo = g.get_repo(REPO_NAME)
                
                # 2. Pega o arquivo antigo (para obter o 'sha')
                status_box.write("📂 Localizando arquivo antigo...")
                contents = repo.get_contents(FILE_PATH)
                
                # 3. Lê os bytes do arquivo novo
                novos_bytes = uploaded_file.getvalue()
                
                # 4. Atualiza o arquivo no repositório
                status_box.write("💾 Enviando novos dados...")
                repo.update_file(
                    path=contents.path,
                    message="Atualização via Dashboard Streamlit",
                    content=novos_bytes,
                    sha=contents.sha
                )
                
                status_box.update(label="✅ Atualização Concluída!", state="complete", expanded=False)
                
                st.balloons()
                st.success("O arquivo foi atualizado com sucesso no repositório!")
                st.warning("🔄 O sistema está reiniciando para carregar os novos dados. Aguarde alguns segundos...")
                
            except Exception as e:
                status_box.update(label="❌ Erro na atualização", state="error")
                st.error(f"Detalhe do erro: {e}")
                    
    except Exception as e:
        st.error(f"Erro ao ler o arquivo Excel: {e}")
