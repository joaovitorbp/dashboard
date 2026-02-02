import streamlit as st
import pandas as pd
import json
import os
import shutil

# ---------------------------------------------------------
# NOTA: REMOVEMOS O st.set_page_config E O CSS DAQUI.
# ---------------------------------------------------------

st.markdown("""
<style>
    /* Fundo geral */
    .stApp {background-color: #0e1117;}
    
    /* --- ALINHAMENTO NO TOPO (PADRONIZADO) --- */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
    }
    h1 {
        padding-top: 0rem !important;
        margin-top: -1rem !important;
    }
    
    /* --- Estilização dos Botões (Azul Vibrante) --- */
    div.stButton > button {
        background-color: #58a6ff;
        color: #ffffff; 
        border: none;
        font-weight: 700;
        padding: 0.5rem 1rem;
        transition: all 0.2s ease-in-out;
    }
    div.stButton > button:hover {
        background-color: #79c0ff;
        color: #ffffff;
        box-shadow: 0 4px 8px rgba(88, 166, 255, 0.3);
    }
    div.stButton > button:active {
        background-color: #58a6ff;
        transform: translateY(2px);
    }

    /* --- Tipografia --- */
    h3 {color: #ffffff !important; font-size: 1.3rem; font-weight: 600;}
    p, .stMarkdown, .stNumberInput label {color: #e6edf3 !important;}
    
</style>
""", unsafe_allow_html=True)

st.title("⚙️ Configurações do Sistema")

# ARQUIVOS
CONFIG_FILE = "config.json"
DATA_FILE = "dados_obras_v5.xlsx"
BACKUP_FILE = "dados_obras_v5.bak"

# ---------------------------------------------------------
# SISTEMA DE BACKUP AUTOMÁTICO
# ---------------------------------------------------------
if os.path.exists(DATA_FILE) and not os.path.exists(BACKUP_FILE):
    shutil.copy(DATA_FILE, BACKUP_FILE)

# ---------------------------------------------------------
# FUNÇÕES
# ---------------------------------------------------------
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

def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f)

config_atual = load_config()

# ---------------------------------------------------------
# 1. PARÂMETROS DE GESTÃO
# ---------------------------------------------------------
with st.container(border=True):
    st.subheader("Parâmetros de Metas")
    st.write("") 
    
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
    
    st.write("")
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
# 2. ATUALIZAÇÃO DE DADOS
# ---------------------------------------------------------
with st.container(border=True):
    st.subheader("Base de dados")
    st.write("")
    
    st.markdown(f"Arquivo interno do sistema: **{DATA_FILE}**")
    st.write("")
    
    uploaded_file = st.file_uploader("Arraste o arquivo atualizado aqui (.xlsx)", type=["xlsx"])

    if uploaded_file is not None:
        st.write("")
        if st.button("Confirmar Substituição da Base"):
            # Backup antes de substituir
            if os.path.exists(DATA_FILE) and not os.path.exists(BACKUP_FILE):
                shutil.copy(DATA_FILE, BACKUP_FILE)
            
            with open(DATA_FILE, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            st.cache_data.clear()
            st.success("✅ Base de dados atualizada temporariamente!")
            st.rerun()

# ---------------------------------------------------------
# 3. RESTAURAÇÃO (PADRONIZADO)
# ---------------------------------------------------------
if os.path.exists(BACKUP_FILE):
    st.write("")
    with st.container(border=True):
        st.subheader("Modo de Restauração")
        st.write("")
        st.markdown("Caso tenha enviado um arquivo errado, clique abaixo para voltar ao arquivo original do sistema.")
        st.write("")
        
        if st.button("Restaurar Arquivo Original"):
            try:
                shutil.copy(BACKUP_FILE, DATA_FILE)
                st.cache_data.clear()
                st.success("✅ Base original restaurada com sucesso!")
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao restaurar: {e}")

# ---------------------------------------------------------
# 4. VISUALIZAÇÃO DE CHECK
# ---------------------------------------------------------
if os.path.exists(DATA_FILE):
    st.write("")
    with st.expander("Verificar dados carregados atualmente"):
        try:
            df_check = pd.read_excel(DATA_FILE)
            st.dataframe(df_check, use_container_width=True)
        except Exception as e:
            st.error("O arquivo atual parece estar corrompido ou inválido.")
