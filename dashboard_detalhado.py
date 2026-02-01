import streamlit as st
import pandas as pd
import json
import os

# ---------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA
# ---------------------------------------------------------
st.set_page_config(page_title="Configurações", layout="wide")

st.markdown("""
<style>
    .stApp {background-color: #0e1117;}
    .block-container {padding-top: 3rem; padding-bottom: 3rem;}
    
    /* Estilização dos Botões para Azul (Melhor Contraste) */
    div.stButton > button {
        background-color: #1f6feb; 
        color: white; 
        border: 1px solid #1f6feb;
        font-weight: 600;
    }
    div.stButton > button:hover {
        background-color: #58a6ff;
        border-color: #58a6ff;
        color: white;
    }
    div.stButton > button:active {
        background-color: #1f6feb;
        color: white;
    }

    h3 {color: #58a6ff !important; font-size: 1.2rem;}
    p {color: #8b949e;}
</style>
""", unsafe_allow_html=True)

st.title("⚙️ Configurações do Sistema")
# Subtítulo removido conforme solicitado

# ARQUIVOS DE CONFIGURAÇÃO
CONFIG_FILE = "config.json"
DATA_FILE = "dados_obras_v5.xlsx"

# Função para carregar configurações
def load_config():
    default_data = {"meta_vendas": 5000000.0, "meta_margem": 25.0, "meta_custo_adm": 5.0}
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w") as f:
            json.dump(default_data, f)
        return default_data
    
    with open(CONFIG_FILE, "r") as f:
        data = json.load(f)
        if "meta_custo_adm" not in data: data["meta_custo_adm"] = 5.0
        return data

# Função para salvar configurações
def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f)

# Carrega valores atuais
config_atual = load_config()

# ---------------------------------------------------------
# 1. PARÂMETROS DE GESTÃO (METAS)
# ---------------------------------------------------------
# Substituído HTML manual por Container Nativo para evitar bugs visuais
with st.container(border=True):
    st.subheader("Parâmetros de Metas")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        nova_meta_vendas = st.number_input(
            "Meta Anual de Vendas (R$)",
            min_value=0.0,
            value=float(config_atual["meta_vendas"]),
            step=100000.0,
            format="%.2f"
        )
        
    with col2:
        nova_meta_margem = st.number_input(
            "Meta de Margem Bruta (%)",
            min_value=0.0,
            max_value=100.0,
            value=float(config_atual["meta_margem"]),
            step=0.5,
            format="%.1f"
        )

    with col3:
        nova_meta_adm = st.number_input(
            "Custo Adm. Esperado (%)",
            min_value=0.0,
            max_value=50.0,
            value=float(config_atual["meta_custo_adm"]),
            step=0.5,
            format="%.1f"
        )
    
    # Texto explicativo removido conforme solicitado
    st.write("") 

    if st.button("Salvar Novos Parâmetros"):
        novos_dados = {
            "meta_vendas": nova_meta_vendas,
            "meta_margem": nova_meta_margem,
            "meta_custo_adm": nova_meta_adm
        }
        save_config(novos_dados)
        st.success("✅ Parâmetros atualizados! Os indicadores foram recalculados.")

# ---------------------------------------------------------
# 2. ATUALIZAÇÃO DE DADOS (UPLOAD)
# ---------------------------------------------------------
with st.container(border=True):
    st.subheader("Base de dados")
    
    st.info(f"Arquivo em uso: **{DATA_FILE}**")
    
    uploaded_file = st.file_uploader("Arraste o arquivo atualizado aqui (.xlsx)", type=["xlsx"])

    if uploaded_file is not None:
        st.write("")
        if st.button("Confirmar Substituição da Base"):
            # Salva o arquivo no disco
            with open(DATA_FILE, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Limpa o cache para forçar recarregamento nas outras páginas
            st.cache_data.clear()
            st.success("✅ Base de dados atualizada e cache limpo!")

# ---------------------------------------------------------
# 3. VISUALIZAÇÃO DE CHECK (OPCIONAL)
# ---------------------------------------------------------
if os.path.exists(DATA_FILE):
    st.write("")
    with st.expander("Verificar dados carregados atualmente"):
        df_check = pd.read_excel(DATA_FILE)
        st.dataframe(df_check.head(10), use_container_width=True)
