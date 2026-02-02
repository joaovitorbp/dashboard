import streamlit as st
import streamlit_authenticator as stauth

# --- CÓDIGO TEMPORÁRIO PARA GERAR HASH ---
senha_real = "coloque_sua_senha_aqui"  # <--- DIGITE SUA SENHA AQUI

hashed_passwords = stauth.Hasher([senha_real]).generate()
st.write("Sua senha criptografada é:")
st.code(hashed_passwords[0], language='text')
