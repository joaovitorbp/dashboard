import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import gspread
import os

# ---------------------------------------------------------
# 1. CONFIGURAÇÃO VISUAL (PADRÃO DO PROJETO)
# ---------------------------------------------------------
st.markdown("""
<style>
    /* Fundo e Espaçamento */
    .stApp {background-color: #0e1117;}
    .block-container {padding-top: 1rem !important; padding-bottom: 2rem !important;}
    h1 {padding-top: 0rem !important; margin-top: -1rem !important;}
    
    /* Abas customizadas */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px; white-space: pre-wrap; background-color: #161b22; border-radius: 5px; color: #fff; border: 1px solid #30363d;
    }
    .stTabs [aria-selected="true"] {
        background-color: #58a6ff !important; color: white !important; border-color: #58a6ff;
    }
    
    /* Box de Destaque */
    .highlight-box {
        background-color: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 15px; text-align: center;
    }
    .highlight-val { font-size: 1.5rem; font-weight: 800; color: white; }
    .highlight-lbl { color: #8b949e; font-size: 0.8rem; text-transform: uppercase; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. DADOS (CONECTADO AO GOOGLE SHEETS)
# ---------------------------------------------------------
@st.cache_data(ttl=60)
def load_data():
    try:
        gc = gspread.service_account_from_dict(st.secrets["gcp_service_account"])
        sh = gc.open("dados_dashboard_obras") 
        worksheet = sh.sheet1
        dados = worksheet.get_all_records()
        df = pd.DataFrame(dados)
        return df
    except Exception as e:
        return None

df_raw = load_data()

if df_raw is None:
    st.error("⚠️ Erro ao conectar com o Google Sheets.")
    st.stop()

# --- LIMPEZA DE DADOS ---
def clean_google_number(x):
    if isinstance(x, (int, float)): return float(x)
    if x is None: return 0.0
    s = str(x).strip()
    if s == "": return 0.0
    try:
        s = s.replace('R$', '').replace('%', '').replace(' ', '')
        s = s.replace('.', '').replace(',', '.')
        return float(s)
    except: return 0.0

cols_numericas = ['Vendido', 'Mat_Real', 'Desp_Real', 'HH_Real_Vlr', 'Impostos']
for col in cols_numericas:
    if col in df_raw.columns:
        df_raw[col] = df_raw[col].apply(clean_google_number)
    else:
        df_raw[col] = 0.0

# Cálculos Base
df_raw['Custo_Total'] = df_raw['Mat_Real'] + df_raw['Desp_Real'] + df_raw['HH_Real_Vlr'] + df_raw['Impostos']
df_raw['Lucro'] = df_raw['Vendido'] - df_raw['Custo_Total']

# Criação da Chave Única: Cliente + Local
# Ex: "Empresa X (São Paulo)"
df_raw['Cliente_Local'] = df_raw.apply(
    lambda row: f"{row['Cliente']} ({row['Cidade']})" if pd.notna(row['Cidade']) and str(row['Cidade']).strip() != "" else row['Cliente'], 
    axis=1
)

# ---------------------------------------------------------
# 3. FILTROS ESTRATÉGICOS (REGRA DE NEGÓCIO)
# ---------------------------------------------------------

# 1. Remover IDs Administrativos da análise de obras
IDS_ADM = [5009.2025, 5010.2025, 5011.2025]
df_obras = df_raw[~df_raw['Projeto'].isin(IDS_ADM)].copy()

# 2. FILTRO CRÍTICO: Apenas Obras Concluídas
# Motivo: Obras em andamento distorcem a margem pois o custo ainda não aconteceu totalmente.
df_finalizadas = df_obras[df_obras['Status'].isin(['Finalizado', 'Apresentado'])].copy()

# ---------------------------------------------------------
# 4. INTERFACE
# ---------------------------------------------------------
st.title("Análise Macro de Clientes")

if df_finalizadas.empty:
    st.warning("⚠️ Nenhuma obra com status 'Finalizado' ou 'Apresentado' encontrada. Finalize obras para ver as análises.")
    st.stop()

# --- KPI GERAL DA CARTEIRA FINALIZADA ---
total_vendido = df_finalizadas['Vendido'].sum()
total_lucro = df_finalizadas['Lucro'].sum()
margem_global = (total_lucro / total_vendido * 100) if total_vendido > 0 else 0

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f"""
    <div class="highlight-box" style="border-top: 4px solid #58a6ff">
        <div class="highlight-lbl">Total Finalizado</div>
        <div class="highlight-val">R$ {total_vendido:,.2f}</div>
    </div>
    """, unsafe_allow_html=True)
with c2:
    cor_m = "#3fb950" if margem_global > 25 else "#da3633"
    st.markdown(f"""
    <div class="highlight-box" style="border-top: 4px solid {cor_m}">
        <div class="highlight-lbl">Margem Real Média</div>
        <div class="highlight-val" style="color:{cor_m}">{margem_global:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)
with c3:
    st.markdown(f"""
    <div class="highlight-box" style="border-top: 4px solid #8b949e">
        <div class="highlight-lbl">Obras Entregues</div>
        <div class="highlight-val">{len(df_finalizadas)}</div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ---------------------------------------------------------
# ANÁLISE DETALHADA POR CLIENTE + LOCAL
# ---------------------------------------------------------
st.subheader("Performance por Cliente e Local")
st.caption("Considerando apenas obras entregues (Status: Finalizado ou Apresentado)")

# Agrupamento Inteligente
df_agrupado = df_finalizadas.groupby('Cliente_Local').agg({
    'Vendido': 'sum',
    'Lucro': 'sum',
    'Projeto': 'count'
}).reset_index()

# Cálculo da Margem Ponderada
df_agrupado['Margem_%'] = (df_agrupado['Lucro'] / df_agrupado['Vendido'] * 100).fillna(0)
df_agrupado = df_agrupado.sort_values(by='Vendido', ascending=True)

col_chart, col_table = st.columns([2, 1])

with col_chart:
    st.markdown("##### 📊 Rentabilidade x Volume")
    
    # Gráfico de Barras Horizontal
    fig = px.bar(
        df_agrupado, 
        y='Cliente_Local', 
        x='Vendido',
        text_auto='.2s',
        orientation='h',
        color='Margem_%',
        # Escala de cor semafórica: Vermelho (Ruim) -> Amarelo -> Verde (Bom)
        color_continuous_scale=['#da3633', '#e3b341', '#3fb950'],
        labels={'Vendido': 'Faturamento Realizado (R$)', 'Cliente_Local': 'Cliente', 'Margem_%': 'Margem Real %'}
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', 
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        xaxis=dict(showgrid=True, gridcolor='#30363d'),
        height=500,
        margin=dict(l=0, r=0, t=30, b=0)
    )
    # Personaliza o tooltip para mostrar qtd de obras
    fig.update_traces(hovertemplate='<b>%{y}</b><br>Faturamento: R$ %{x:,.2f}<br>Margem: %{marker.color:.1f}%<extra></extra>')
    
    st.plotly_chart(fig, use_container_width=True)
    st.info("💡 **Dica:** A barra mostra o volume financeiro. A **cor** mostra se o cliente deu lucro (Verde) ou apertou a margem (Vermelho).")

with col_table:
    st.markdown("##### 🏆 Ranking (Pareto)")
    
    # Prepara tabela para exibição (Top Clientes)
    df_pareto = df_agrupado.sort_values(by='Vendido', ascending=False).copy()
    
    st.dataframe(
        df_pareto[['Cliente_Local', 'Vendido', 'Margem_%']],
        column_config={
            "Cliente_Local": st.column_config.TextColumn("Cliente (Local)"),
            "Vendido": st.column_config.ProgressColumn(
                "Total Faturado", 
                format="R$ %.2f", 
                min_value=0, 
                max_value=float(df_pareto['Vendido'].max())
            ),
            "Margem_%": st.column_config.NumberColumn(
                "Margem %", 
                format="%.1f%%"
            )
        },
        hide_index=True,
        use_container_width=True,
        height=500
    )
