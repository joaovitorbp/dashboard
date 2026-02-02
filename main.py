import streamlit as st
import bcrypt

# --- GERADOR DE HASH INFALÍVEL ---
st.title("Gerador de Senha")

# 1. Digite sua senha aqui dentro das aspas
minha_senha_real = "admin" 

# 2. O código abaixo cria a criptografia
senha_bytes = minha_senha_real.encode('utf-8')
salt = bcrypt.gensalt()
senha_hash = bcrypt.hashpw(senha_bytes, salt)

# 3. Mostra o resultado na tela
st.write("Copie o código abaixo para colocar no Secrets:")
st.code(senha_hash.decode('utf-8'), language='text')
