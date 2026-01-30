import streamlit as st
import pandas as pd

# ---------------------------------------------------------
# 1. CSS
# ---------------------------------------------------------
st.markdown("""
<style>
    .stApp {background-color: #0e1117;}
    .block-container {padding-top: 2rem;}

    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 0px !important;
    }

    .tile-header {
        padding: 15px;
        color: white;
        font-weight: 700;
    }

    /* ---------- BOTÃO ---------- */
    .btn-scale {
        display: flex;
        justify-content: flex-end;
        padding: 8px 12px 12px 12px;
        transform: scale(0.8);
        transform-origin: right center;
    }

    .btn-scale button {
        background-color: transparent;
        border: 1px solid transparent;
        color: #58a6ff;
    }

    .btn-scale button:hover {
        background-color: #1f242c;
        border-color: #30363d;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. DADOS
# ---------------------------------------------------------
df = pd.DataFrame({
    "Projeto": ["Obra A", "Obra B", "Obra C"]
})

# ---------------------------------------------------------
# 3. INTERFACE
# ---------------------------------------------------------
st.title("🏢 Painel de Controle")

cols = st.columns(3)

for i, row in df.iterrows():
    with cols[i % 3]:
        with st.container(border=True):

            # CONTEÚDO DO CARD (inalterado)
            st.markdown(f"""
            <div class="tile-header">
                {row['Projeto']}
            </div>
            """, unsafe_allow_html=True)

            st.markdown("📊 Margem: 18%  |  ⏱ HH: 72%")

            # BOTÃO (isolado e escalado)
            st.markdown("<div class='btn-scale'>", unsafe_allow_html=True)
            if st.button("Abrir ↗", key=f"btn_{row['Projeto']}"):
                st.write("Abrindo", row['Projeto'])
            st.markdown("</div>", unsafe_allow_html=True)
