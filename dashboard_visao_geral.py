import streamlit as st
import pandas as pd
import textwrap

# ---------------------------------------------------------
# 1. CONFIGURAÇÃO VISUAL (CSS - TILES MODERNOS)
# ---------------------------------------------------------
st.markdown("""
<style>
    .stApp {background-color: #0e1117;}
    .block-container {padding-top: 2rem;}

    /* --- CONTAINER DO CARD --- */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 0px !important;
        transition: transform 0.2s;
    }
    [data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color: #58a6ff;
        transform: translateY(-2px);
    }

    /* --- HEADER --- */
    .tile-header {
        padding: 15px 15px 10px 15px;
    }
    .tile-title {
        color: white;
        font-family: "Source Sans Pro", sans-serif;
        font-weight: 700;
        font-size: 1rem;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        margin-bottom: 2px;
    }
    .tile-sub {
        color: #8b949e;
        font-size: 0.75rem;
        font-family: "Source Sans Pro", sans-serif;
    }

    /* --- DATA STRIP --- */
    .data-strip {
        background-color: #0d1117;
        border-top: 1px solid #21262d;
        border-bottom: 1px solid #21262d;
        padding: 10px 15px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .data-col {
        display: flex;
        flex-direction: column;
        align-items: center;
        width: 25%;
    }
    .data-col:not(:last-child) {
        border-right: 1px solid #30363d;
    }
    .data-lbl {
        font-size: 0.6rem;
        color: #8b949e;
        text-transform: uppercase;
        margin-bottom: 2px;
    }
    .data-val {
        font-size: 0.85rem;
        font-weight: 700;
        color: #e6edf3;
        font-family: "Source Sans Pro", sans-serif;
    }

    /* --- FOOTER --- */
    .tile-footer {
        padding: 10px 15px;
    }
    .progress-track {
        background-color: #21262d;
        height: 4px;
        border-radius: 2px;
        width: 100%;
        margin-bottom: 10px;
        overflow: hidden;
    }
    .progress-fill { height: 100%; border-radius: 2px; }

    .footer-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        height: 20px;
    }

    .badge-status {
        font-size: 0.65rem;
        font-weight: 700;
        text-transform: uppercase;
        padding: 2px 8px;
        border-radius: 4px;
        letter-spacing: 0.5px;
        line-height: 1.2;
    }

    .footer-pct {
        font-size: 0.8rem;
        font-weight: 700;
        font-family: "Source Sans Pro", sans-serif;
        line-height: 1;
        display: flex;
        align-items: center;
    }

    /* --- BOTÃO (REDUZIDO) --- */
    div[data-testid="stVerticalBlockBorderWrapper"] button {
        background-color: transparent;
        color: #58a6ff;
        border: 1px solid transparent;
        border-radius: 4px;

        font-size: 0.65rem;   /* ↓ menor */
        padding: 2px 6px;     /* ↓ menor */
        height: auto;
        min-height: 0px;
        line-height: 1.1;
        margin: 0;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] button:hover {
        background-color: #1f242c;
        border-color: #30363d;
        text-decoration: none;
    }

    div[data-testid="column"] { padding: 0 8px; }

    /* KPIs Globais */
    .big-kpi {
        background-color: #161b22;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #30363d;
        text-align: center;
    }
    .big-kpi-val {
        font-size: 1.8rem;
        font-weight: bold;
        color: white;
        font-family: "Source Sans Pro", sans-serif;
    }
    .big-kpi-lbl {
        font-size: 0.9rem;
        color: #8b949e;
        font-family: "Source Sans Pro", sans-serif;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. DADOS
# ---------------------------------------------------------
@st.cache_data
def load_data():
    return pd.read_excel("dados_obras_v5.xlsx")

try:
    df = load_data()
except FileNotFoundError:
    st.error("⚠️ Base de dados 'dados_obras_v5.xlsx' não encontrada.")
    st.stop()

# ---------------------------------------------------------
# 3. CÁLCULOS
# ---------------------------------------------------------
META_MARGEM = 20.0

def calcular_dados_extras(row):
    custo = row['Mat_Real'] + row['Desp_Real'] + row['HH_Real_Vlr'] + row['Impostos']
    lucro = row['Vendido'] - custo
    margem = (lucro / row['Vendido'] * 100) if row['Vendido'] > 0 else 0
    hh_perc = (row['HH_Real_Qtd'] / row['HH_Orc_Qtd'] * 100) if row['HH_Orc_Qtd'] > 0 else 0
    fisico = row['Conclusao_%']
    critico = margem < META_MARGEM or hh_perc > (fisico + 10)
    return pd.Series([margem, critico])

df[['Margem_%', 'E_Critico']] = df.apply(calcular_dados_extras, axis=1)

# ---------------------------------------------------------
# 4. INTERFACE
# ---------------------------------------------------------
st.title("🏢 Painel de Controle")

k1, k2, k3, k4 = st.columns(4)
k1.markdown(f"<div class='big-kpi'><div class='big-kpi-lbl'>Total Carteira</div><div class='big-kpi-val'>R$ {df['Vendido'].sum()/1e6:.1f}M</div></div>", unsafe_allow_html=True)
k2.markdown(f"<div class='big-kpi'><div class='big-kpi-lbl'>Faturamento</div><div class='big-kpi-val'>R$ {df['Faturado'].sum()/1e6:.1f}M</div></div>", unsafe_allow_html=True)
k3.markdown(f"<div class='big-kpi'><div class='big-kpi-lbl'>Obras Ativas</div><div class='big-kpi-val'>{len(df[df['Status']=='Em andamento'])}</div></div>", unsafe_allow_html=True)
k4.markdown(f"<div class='big-kpi'><div class='big-kpi-lbl'>Margem Média</div><div class='big-kpi-val'>{df['Margem_%'].mean():.1f}%</div></div>", unsafe_allow_html=True)

st.divider()

status_options = ["Todas", "Não iniciado", "Em andamento", "Apresentado", "Finalizado", "🚨 Críticas"]
filtro_status = st.radio("Visualização:", status_options, horizontal=True)

df_show = df.copy()

if filtro_status == "Não iniciado":
    df_show = df_show[df_show['Status'].str.strip().str.lower() == 'não iniciado']
elif filtro_status == "Em andamento":
    df_show = df_show[df_show['Status'] == 'Em andamento']
elif filtro_status == "Apresentado":
    df_show = df_show[df_show['Status'] == 'Apresentado']
elif filtro_status == "Finalizado":
    df_show = df_show[df_show['Status'] == 'Finalizado']
elif filtro_status == "🚨 Críticas":
    df_show = df_show[df_show['E_Critico']]

st.write(f"**{len(df_show)}** projetos encontrados")
st.write("")

# ---------------------------------------------------------
# 5. GRID DE CARDS
# ---------------------------------------------------------
cols = st.columns(3)

for index, row in df_show.iterrows():
    with cols[index % 3]:

        pct = int(row['Conclusao_%'])
        status_raw = str(row['Status']).strip()

        pct_horas = (row['HH_Real_Qtd'] / row['HH_Orc_Qtd'] * 100) if row['HH_Orc_Qtd'] > 0 else 0
        pct_mat = (row['Mat_Real'] / row['Mat_Orc'] * 100) if row['Mat_Orc'] > 0 else 0

        if status_raw == "Finalizado":
            cor_tema = "#238636"
            bg_badge = "rgba(35, 134, 54, 0.2)"
            color_badge = "#3fb950"
        elif status_raw == "Apresentado":
            cor_tema = "#1f6feb"
            bg_badge = "rgba(31, 111, 235, 0.2)"
            color_badge = "#58a6ff"
        elif status_raw == "Em andamento":
            cor_tema = "#d29922"
            bg_badge = "rgba(210, 153, 34, 0.2)"
            color_badge = "#e3b341"
        else:
            cor_tema = "#da3633"
            bg_badge = "rgba(218, 54, 51, 0.2)"
            color_badge = "#f85149"

        cor_margem = "#da3633" if row['Margem_%'] < META_MARGEM else "#3fb950"
        cor_horas = "#da3633" if pct_horas > 100 else "#e6edf3"
        cor_mat = "#da3633" if pct_mat > 100 else "#e6edf3"

        with st.container(border=True):

            st.markdown(f"""
            <div class="tile-header" style="border-left: 3px solid {cor_tema}">
                <div class="tile-title" title="{row['Projeto']} - {row['Descricao']}">{row['Projeto']} - {row['Descricao']}</div>
                <div class="tile-sub">{row['Cliente']} | {row['Cidade']}</div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div class="data-strip">
                <div class="data-col"><span class="data-lbl">Valor</span><span class="data-val">{row['Vendido']/1000:,.0f}k</span></div>
                <div class="data-col"><span class="data-lbl">Margem</span><span class="data-val" style="color:{cor_margem}">{row['Margem_%']:.0f}%</span></div>
                <div class="data-col"><span class="data-lbl">Horas</span><span class="data-val" style="color:{cor_horas}">{pct_horas:.0f}%</span></div>
                <div class="data-col"><span class="data-lbl">Mat</span><span class="data-val" style="color:{cor_mat}">{pct_mat:.0f}%</span></div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div class="tile-footer">
                <div class="progress-track">
                    <div class="progress-fill" style="width:{pct}%; background-color:{cor_tema};"></div>
                </div>
                <div class="footer-row">
                    <span class="badge-status" style="background-color:{bg_badge}; color:{color_badge}">{status_raw}</span>
                    <span class="footer-pct" style="color:{color_badge}">{pct}%</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            col_spacer, col_btn = st.columns([2, 1])
            with col_btn:
                if st.button("Abrir ↗", key=f"btn_{row['Projeto']}"):
                    st.session_state["projeto_foco"] = row['Projeto']
                    st.switch_page("dashboard_detalhado.py")
