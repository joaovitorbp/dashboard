import streamlit as st
import streamlit_authenticator as stauth

st.title("Gerador de Senha Definitivo")

# --- DIGITE SUA SENHA AQUI EMBAIXO ---
minha_senha = "admin" 
# -------------------------------------

try:
    # Tenta gerar usando a versão mais nova da biblioteca
    hashed_passwords = stauth.Hasher([minha_senha]).generate()
    if isinstance(hashed_passwords, list):
        hash_final = hashed_passwords[0]
    else:
        hash_final = hashed_passwords
except Exception as e:
    st.error(f"Erro ao gerar: {e}")
    hash_final = "Erro"

st.write(f"Senha escolhida: **{minha_senha}**")
st.write("Copie o código abaixo EXATAMENTE como está (sem aspas extras):")
st.code(hash_final, language='text')
