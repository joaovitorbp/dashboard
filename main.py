import streamlit as st
import streamlit_authenticator as stauth

# --- CÓDIGO TEMPORÁRIO PARA GERAR HASH ---
try:
    # Tenta usar a versão mais nova da biblioteca
    hasher = stauth.Hasher(["Obras@2026"]) 
    hashed_passwords = hasher.generate()
except:
    # Fallback para versões antigas ou comportamento diferente
    import bcrypt
    senha = "coloque_sua_senha_aqui"
    hashed_passwords = [bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()]

st.title("Copie o código abaixo:")
st.code(hashed_passwords[0], language='text')
