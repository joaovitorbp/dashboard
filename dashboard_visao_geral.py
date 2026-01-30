import streamlit as st
import pandas as pd

# =========================================================
# CSS — ESTILO DO CARD + BOTÃO ESCALADO
# =========================================================
st.markdown("""
<style>
/* Fundo geral */
.stApp {
    background-color: #0e1117;
}

/* Card */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 8px;
}

/* Cabeçalho do card */
.tile-header {
    padding: 14px 14px 6px 14px;
    font-size: 0.9rem;
    font-weight: 600;
    color: #f0f6fc;
}

/* Conteúdo */
.tile-body {
    padding: 0px 14px 8px 14px;
    font-size: 0.75rem;
    color: #c9d1d9;
}

/* ---------- BOTÃO (ESCALA REAL 80%) ---------- */
.btn-scale {
    display: flex;
    justify-content: flex-end;
    padding: 6px 10px 10px 10px;

    transform: scale(0.8);              /* 🔥 escala TOTAL */
    transform-origin: right center;     /* ancora à direita */
}

/* Estilo do botão */
.btn-scale button {
    background-color: transparent !important;
    color: #58a6ff !important;
    border: 1px solid transparent !important;
    padding: 4px 10px !important;
    font-size: 0.75rem !important;
}

/* Hover */
.btn-scale button:hover {
    background-color: #1f242c !important;
    border-color: #30363d !important;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# DADOS DE EXEMPLO
# =========================================================
df = pd.DataFrame({
    "Projeto": ["Obra A", "Obra B", "Obra C"],
    "Margem": ["18%", "22%", "15%"],
    "HH": ["72%", "64%", "81%"]
})

# =========================================================
# INTERFACE
# =========================================================
st.title("📊 Dashboard de Projetos")

cols = st.columns(3)

for i, row in df.iterrows():
    with cols[i % 3]:
        with st.container(border=True):

            # ---------- CONTEÚDO DO CARD ----------
            st.markdown(
                f"<div class='tile-header'>{row['Projeto']}</div>",
                unsafe_allow_html=True
            )

            st.markdown(
                f"""
                <div class='tile-body'>
                    📈 Margem: {row['Margem']}<br>
                    ⏱ HH Consumido: {row['HH']}
                </div>
                """,
                unsafe_allow_html=True
            )

            # ---------- BOTÃO (ISOLADO E ESCALADO) ----------
            st.markdown("<div class='btn-scale'>", unsafe_allow_html=True)
            if st.button("Abrir ↗", key=f"btn_{row['Projeto']}"):
                st.session_state["projeto_foco"] = row["Projeto"]
                st.write("Abrindo:", row["Projeto"])
            st.markdown("</div>", unsafe_allow_html=True)
