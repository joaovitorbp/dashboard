import streamlit as st
import bcrypt

st.title("Gerador de Senha 100% Funcional")

# --- SUA SENHA AQUI ---
senha_desejada = "obras@2026" 
# ----------------------

# Gera o hash manualmente usando bcrypt puro
try:
    senha_bytes = senha_desejada.encode('utf-8')
    salt = bcrypt.gensalt()
    senha_hash = bcrypt.hashpw(senha_bytes, salt).decode('utf-8')
    
    st.success("Senha gerada com sucesso!")
    st.write(f"Senha original: **{senha_desejada}**")
    st.write("Copie o código abaixo para o Secrets:")
    st.code(senha_hash, language='text')
except Exception as e:
    st.error(f"Erro: {e}")
