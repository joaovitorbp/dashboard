import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import gspread
import json
import os

# ---------------------------------------------------------
# 1. CONFIGURAÇÃO VISUAL
# ---------------------------------------------------------
st.markdown("""
<style>
    .stApp {background-color: #0e1117;}
    .block-container {padding-top: 1rem !important; padding-bottom: 2rem !important;}
    h1 {padding-top: 0rem !important; margin-top: -1rem !important;}
    
    .stTabs [data-baseweb="tab-list"] { 
        gap: 0px; 
        background-color: transparent;
        border-bottom: 1px solid #30363d; 
        padding-bottom: 0px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 45px; 
        background-color: transparent; 
        border: none;
        color: #8b949e; 
        border-radius: 0px;
        flex-grow: 0;
        padding-left: 20px;
        padding-right: 20px;
        font-weight: 600;
        margin-bottom: -1px;
    }
    .stTabs [aria-selected="true"] {
        background-color: transparent !important; 
        color: #58a6ff !important; 
        border-bottom: 2px solid #58a6ff;
    }
    .stTabs [data-baseweb="tab-highlight"] {
        background-color: transparent !important;
        height: 0px !important;
    }
    
    .highlight-box {
        background-color: #161b22; 
        border: 1px solid #30363d; 
        border-radius: 8px; 
        padding: 15px; 
        text-align: center;
        height: 100%;
        display: flex; flex-direction: column; justify-content: center;
    }
    .highlight-val { font-size: 1.5rem; font-weight: 800; color: white; }
    .highlight-lbl { color: #8b949e; font-size: 0.8rem; text-transform: uppercase; margin-bottom: 5px; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. CARREGAR CONFIGURAÇÕES
# ---------------------------------------------------------
def load_config():
    default_data = {"meta_vendas": 5000000.0, "meta_margem": 25.0, "meta_custo_adm": 5.0}
    if not os.path.exists("config.json"):
        return default_data
    with open("config.json", "r") as f:
        data = json.load(f)
        if "meta_margem" not in data: data["meta_margem"] = 25.0
        if "meta_custo_adm" not in data: data["meta_custo_adm"] = 5.0
        return data

config = load_config()
META_MARGEM = float(config["meta_margem"])
META_ADM = float(config["meta_custo_adm"])

# ---------------------------------------------------------
# 3. DADOS
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
    except:
        return None

df_raw = load_data()

if df_raw is None:
    st.error("⚠️ Erro ao conectar com o Google Sheets.")
    st.stop()

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

df_raw['Custo_Total'] = df_raw['Mat_Real'] + df_raw['Desp_Real'] + df_raw['HH_Real_Vlr'] + df_raw['Impostos']
df_raw['Lucro'] = df_raw['Vendido'] - df_raw['Custo_Total']
df_raw['Cliente_Local'] = df_raw.apply(lambda row: f"{row['Cliente']} ({row['Cidade']})" if pd.notna(row['Cidade']) and str(row['Cidade']).strip() != "" else row['Cliente'], axis=1)

if 'Tipo' not in df_raw.columns:
    df_raw['Tipo'] = "Não Classificado"
else:
    df_raw['Tipo'] = df_raw['Tipo'].replace("", "Não Classificado")

IDS_ADM = [5009.2025, 5010.2025, 5011.2025]
df_adm = df_raw[df_raw['Projeto'].isin(IDS_ADM)].copy()
df_obras = df_raw[~df_raw['Projeto'].isin(IDS_ADM)].copy()
df_finalizadas = df_obras[df_obras['Status'].isin(['Finalizado', 'Apresentado'])].copy()

# ---------------------------------------------------------
# 5. INTERFACE
# ---------------------------------------------------------
st.title("Análises Estratégicas")
tab1, tab2, tab3 = st.tabs(["Cliente", "Segmentos", "Custos Internos"])

with tab1:
    if df_finalizadas.empty:
        st.warning("⚠️ Nenhuma obra finalizada encontrada.")
    else:
        total_vendido = df_finalizadas['Vendido'].sum()
        total_lucro = df_finalizadas['Lucro'].sum()
        margem_global = (total_lucro / total_vendido * 100) if total_vendido > 0 else 0

        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f'<div class="highlight-box" style="border-top: 4px solid #3fb950"><div class="highlight-lbl">Total Finalizado</div><div class="highlight-val">R$ {total_vendido:,.2f}</div></div>', unsafe_allow_html=True)
        with c2:
            cor_m = "#3fb950" if margem_global >= META_MARGEM else "#da3633"
            st.markdown(f'<div class="highlight-box" style="border-top: 4px solid {cor_m}"><div class="highlight-lbl">Margem</div><div class="highlight-val" style="color:{cor_m}">{margem_global:.1f}%</div></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="highlight-box" style="border-top: 4px solid #8b949e"><div class="highlight-lbl">Obras Entregues</div><div class="highlight-val">{len(df_finalizadas)}</div></div>', unsafe_allow_html=True)

        st.divider()
        st.subheader("Ranking por Planta") 
        df_agrupado = df_finalizadas.groupby('Cliente_Local').agg({'Vendido': 'sum', 'Lucro': 'sum'}).reset_index()
        df_agrupado['Margem_%'] = (df_agrupado['Lucro'] / df_agrupado['Vendido'] * 100).fillna(0)
        df_agrupado = df_agrupado.sort_values(by='Vendido', ascending=True)

        # Gráfico mantido com paleta neutra profissional
        fig_detalhe = px.bar(df_agrupado, y='Cliente_Local', x='Vendido', text_auto='.2s', orientation='h', color='Margem_%', color_continuous_scale=['#1f2937', '#4b5563', '#60a5fa'], labels={'Vendido': 'Valor Vendido (R$)', 'Cliente_Local': '', 'Margem_%': 'Margem %'})
        fig_detalhe.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='white'), xaxis=dict(showgrid=True, gridcolor='#30363d'), height=500, margin=dict(t=0, l=0, r=0, b=0))
        st.plotly_chart(fig_detalhe, use_container_width=True, config={'displayModeBar': False})

with tab2:
    st.write("")
    if df_finalizadas['Tipo'].iloc[0] == "Não Classificado" and len(df_finalizadas['Tipo'].unique()) == 1:
        st.info("💡 Preencha a coluna 'Tipo' na planilha.")
    else:
        df_tipo = df_finalizadas.groupby('Tipo').agg({'Vendido': 'sum', 'Lucro': 'sum', 'Projeto': 'count'}).reset_index()
        df_tipo['Margem_Media'] = (df_tipo['Lucro'] / df_tipo['Vendido'] * 100).fillna(0)
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Participação na Receita")
            fig_tree = px.treemap(df_tipo, path=['Tipo'], values='Vendido', color='Margem_Media', color_continuous_scale=['#1f2937', '#60a5fa'])
            fig_tree.update_layout(margin=dict(t=10, l=10, r=10, b=10), coloraxis_showscale=False)
            fig_tree.update_traces(textinfo="label+value+percent root", textfont=dict(color='white', size=14))
            st.plotly_chart(fig_tree, use_container_width=True, config={'displayModeBar': False})
        with c2:
            st.subheader("Matriz Rentabilidade x Receita")
            fig_scat = px.scatter(df_tipo, x='Vendido', y='Margem_Media', size='Vendido', color='Vendido', color_continuous_scale=['#1f2937', '#60a5fa'], text='Tipo', hover_name='Tipo', labels={'Vendido': 'Volume Vendido (R$)', 'Margem_Media': 'Rentabilidade (%)'})
            fig_scat.add_hline(y=META_MARGEM, line_dash="dash", line_color="#8b949e")
            fig_scat.update_traces(textposition='top center', marker=dict(line=dict(width=1, color='White')))
            fig_scat.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='white'), xaxis=dict(showgrid=True, gridcolor='#30363d'), yaxis=dict(showgrid=True, gridcolor='#30363d'), showlegend=False, coloraxis_showscale=False)
            st.plotly_chart(fig_scat, use_container_width=True, config={'displayModeBar': False})

with tab3:
    st.write("")
    if df_adm.empty:
        st.warning("⚠️ Nenhum projeto 5009, 5010 ou 5011 encontrado.")
    else:
        df_adm['Total_Sem_Imp'] = df_adm['Mat_Real'] + df_adm['Desp_Real'] + df_adm['HH_Real_Vlr']
        custo_adm_total = df_adm['Total_Sem_Imp'].sum()
        faturamento_global = df_obras['Vendido'].sum()
        verba_permitida = faturamento_global * (META_ADM / 100.0)
        impacto_percentual = (custo_adm_total / faturamento_global * 100) if faturamento_global > 0 else 0
        saldo = verba_permitida - custo_adm_total

        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f'<div class="highlight-box" style="border-top: 4px solid #d29922"><div class="highlight-lbl">Custo Interno</div><div class="highlight-val">R$ {custo_adm_total:,.2f}</div></div>', unsafe_allow_html=True)
        with c2:
            # Card com cor semafórica para alertar sobre o Overhead
            cor_impacto = "#3fb950" if impacto_percentual <= META_ADM else "#da3633"
            st.markdown(f'<div class="highlight-box" style="border-top: 4px solid {cor_impacto}"><div class="highlight-lbl">Overhead</div><div class="highlight-val" style="color: {cor_impacto}">{impacto_percentual:.1f}%</div></div>', unsafe_allow_html=True)
        with c3:
            # Card com cor semafórica para indicar Saldo Positivo ou Negativo
            cor_saldo = "#3fb950" if saldo >= 0 else "#da3633"
            sinal = "+" if saldo >= 0 else "-"
            st.markdown(f'<div class="highlight-box" style="border-top: 4px solid {cor_saldo}"><div class="highlight-lbl">Saldo</div><div class="highlight-val" style="color: {cor_saldo}">{sinal} R$ {abs(saldo):,.2f}</div></div>', unsafe_allow_html=True)

        st.divider()

        def plotar_consumo(df_input, group_col):
            # Paleta Corporativa Neutra
            cores_cat = {'Pessoal': '#003366', 'Despesas': '#4b5563', 'Materiais': '#708090'}
            cores_seq = ['#003366', '#4b5563', '#708090']
            
            if group_col == 'Categoria':
                vals = {'Pessoal': df_adm['HH_Real_Vlr'].sum(), 'Despesas': df_adm['Desp_Real'].sum(), 'Materiais': df_adm['Mat_Real'].sum()}
                df_grouped = pd.DataFrame(list(vals.items()), columns=['Categoria', 'Valor'])
                df_grouped = df_grouped[df_grouped['Valor'] > 0]
                col_val, col_name = 'Valor', 'Categoria'
            else:
                df_grouped = df_adm.groupby('Projeto').agg({'Total_Sem_Imp': 'sum', 'Descricao': 'first'}).reset_index()
                col_val, col_name = 'Total_Sem_Imp', 'Projeto'
            
            df_grouped['Pct'] = (df_grouped[col_val] / df_grouped[col_val].sum() * 100).fillna(0)
            df_grouped['Rotulo'] = df_grouped.apply(lambda x: f"<b>{x[col_name]}</b><br>R$ {x[col_val]/1000:.0f}k<br>({x['Pct']:.1f}%)", axis=1)

            fig = go.Figure()
            for i, row in df_grouped.iterrows():
                cor = cores_cat.get(row[col_name], '#60a5fa') if group_col == 'Categoria' else cores_seq[i % 3]
                fig.add_trace(go.Bar(y=['Consumo'], x=[row[col_val]], name=str(row[col_name]), orientation='h', marker=dict(color=cor), text=[row['Rotulo']], textposition='auto', insidetextfont=dict(color='white', size=13)))

            fig.update_layout(barmode='stack', height=180, margin=dict(l=0, r=0, t=10, b=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(showgrid=True, gridcolor='#30363d', tickfont=dict(color='#8b949e'), tickprefix="R$ ", range=[0, max(verba_permitida, custo_adm_total) * 1.15]), yaxis=dict(showticklabels=False), showlegend=False)
            fig.add_vline(x=verba_permitida, line_width=2, line_dash="dot", line_color="white", annotation_text=f"Limite: R$ {verba_permitida:,.0f}", annotation_position="top right", annotation_font=dict(color="white"))
            return fig

        st.subheader("Por Centro de Custo")
        st.plotly_chart(plotar_consumo(df_adm, 'Projeto'), use_container_width=True, config={'displayModeBar': False})
        
        st.write("")
        st.subheader("Por Natureza do Gasto")
        st.plotly_chart(plotar_consumo(df_adm, 'Categoria'), use_container_width=True, config={'displayModeBar': False})
