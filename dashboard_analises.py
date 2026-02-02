import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import gspread
import os

# ---------------------------------------------------------
# 1. CONFIGURAÇÃO VISUAL
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
    
    /* Box de Destaque (KPIs) */
    .highlight-box {
        background-color: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 15px; text-align: center;
    }
    .highlight-val { font-size: 1.5rem; font-weight: 800; color: white; }
    .highlight-lbl { color: #8b949e; font-size: 0.8rem; text-transform: uppercase; }

    /* Box de Destaque para ADM */
    .adm-box {
        background-color: #161b22; border: 1px solid #d29922; border-radius: 8px; padding: 20px; text-align: center;
    }
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
df_raw['Cliente_Local'] = df_raw.apply(
    lambda row: f"{row['Cliente']} ({row['Cidade']})" if pd.notna(row['Cidade']) and str(row['Cidade']).strip() != "" else row['Cliente'], 
    axis=1
)

if 'Tipo' not in df_raw.columns:
    df_raw['Tipo'] = "Não Classificado"
else:
    df_raw['Tipo'] = df_raw['Tipo'].replace("", "Não Classificado")

# ---------------------------------------------------------
# 3. FILTROS E SEPARAÇÃO
# ---------------------------------------------------------

# IDs Administrativos
IDS_ADM = [5009.2025, 5010.2025, 5011.2025]

# DataFrame ADM (Apenas 5009, 5010, 5011)
df_adm = df_raw[df_raw['Projeto'].isin(IDS_ADM)].copy()

# DataFrame OBRAS (Tudo exceto ADM)
df_obras = df_raw[~df_raw['Projeto'].isin(IDS_ADM)].copy()

# FILTRO CRÍTICO: Apenas Obras Concluídas para análise de cliente/tipo
df_finalizadas = df_obras[df_obras['Status'].isin(['Finalizado', 'Apresentado'])].copy()

# ---------------------------------------------------------
# 4. INTERFACE
# ---------------------------------------------------------
st.title("Análises Estratégicas")

# As 4 abas contendo todas as análises
tab1, tab2, tab3, tab4 = st.tabs(["👥 Clientes", "🏗️ Tipos de Obra", "📍 Geografia", "🏢 Custos Internos"])

# =========================================================
# ABA 1: CLIENTES (Atualizado: Sem tabela, Sem dica)
# =========================================================
with tab1:
    st.write("")
    
    if df_finalizadas.empty:
        st.warning("⚠️ Nenhuma obra finalizada encontrada.")
    else:
        # KPI GERAL
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

        # GRÁFICO (FULL WIDTH)
        st.subheader("Performance por Cliente e Local")
        
        df_agrupado = df_finalizadas.groupby('Cliente_Local').agg({
            'Vendido': 'sum', 'Lucro': 'sum', 'Projeto': 'count'
        }).reset_index()

        df_agrupado['Margem_%'] = (df_agrupado['Lucro'] / df_agrupado['Vendido'] * 100).fillna(0)
        df_agrupado = df_agrupado.sort_values(by='Vendido', ascending=True)

        fig = px.bar(
            df_agrupado, 
            y='Cliente_Local', x='Vendido',
            text_auto='.2s', orientation='h',
            color='Margem_%',
            color_continuous_scale=['#da3633', '#e3b341', '#3fb950'],
            labels={'Vendido': 'Faturamento Realizado (R$)', 'Cliente_Local': 'Cliente', 'Margem_%': 'Margem Real %'}
        )
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'), xaxis=dict(showgrid=True, gridcolor='#30363d'),
            height=600, # Aumentei um pouco a altura para ficar mais imponente
            margin=dict(l=0, r=0, t=30, b=0)
        )
        fig.update_traces(hovertemplate='<b>%{y}</b><br>Faturamento: R$ %{x:,.2f}<br>Margem: %{marker.color:.1f}%<extra></extra>')
        
        st.plotly_chart(fig, use_container_width=True)

# =========================================================
# ABA 2: TIPOS DE OBRA
# =========================================================
with tab2:
    st.write("")
    
    # Verifica se a coluna Tipo está preenchida
    tem_tipo = True
    if df_finalizadas['Tipo'].iloc[0] == "Não Classificado" and len(df_finalizadas['Tipo'].unique()) == 1:
        st.info("💡 Para ativar esta análise, preencha a coluna 'Tipo' na planilha.")
        tem_tipo = False
    
    if tem_tipo:
        df_tipo = df_finalizadas.groupby('Tipo').agg({
            'Vendido': 'sum', 'Lucro': 'sum', 'Projeto': 'count'
        }).reset_index()
        df_tipo['Margem_Media'] = (df_tipo['Lucro'] / df_tipo['Vendido'] * 100).fillna(0)
        
        c1, c2 = st.columns(2)
        
        with c1:
            st.markdown("##### Share de Faturamento")
            fig_pie = px.pie(
                df_tipo, values='Vendido', names='Tipo', hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig_pie.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='white'))
            st.plotly_chart(fig_pie, use_container_width=True)
            
        with c2:
            st.markdown("##### Matriz de Rentabilidade")
            fig_scat = px.scatter(
                df_tipo, x='Vendido', y='Margem_Media', size='Vendido', color='Tipo',
                text='Tipo', hover_name='Tipo',
                labels={'Vendido': 'Volume Financeiro', 'Margem_Media': 'Rentabilidade (%)'}
            )
            fig_scat.update_traces(textposition='top center')
            fig_scat.update_layout(
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'), xaxis=dict(showgrid=True, gridcolor='#30363d'), yaxis=dict(showgrid=True, gridcolor='#30363d')
            )
            st.plotly_chart(fig_scat, use_container_width=True)

# =========================================================
# ABA 3: GEOGRAFIA
# =========================================================
with tab3:
    st.write("")
    df_geo = df_finalizadas.groupby('Cidade').agg({'Vendido': 'sum', 'Lucro': 'sum'}).reset_index()
    df_geo['Margem_Media'] = (df_geo['Lucro'] / df_geo['Vendido'] * 100).fillna(0)
    df_geo = df_geo.sort_values(by='Vendido', ascending=False)
    
    st.markdown("##### Resultados por Cidade")
    fig_geo = px.bar(
        df_geo, x='Cidade', y='Vendido',
        color='Margem_Media', color_continuous_scale=['#da3633', '#e3b341', '#3fb950'],
        text_auto='.2s'
    )
    fig_geo.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'), yaxis=dict(showgrid=True, gridcolor='#30363d')
    )
    st.plotly_chart(fig_geo, use_container_width=True)

# =========================================================
# ABA 4: CUSTOS INTERNOS (ADM)
# =========================================================
with tab4:
    st.write("")
    
    if df_adm.empty:
        st.warning("⚠️ Nenhum projeto 5009, 5010 ou 5011 encontrado.")
    else:
        custo_adm_total = df_adm['Custo_Total'].sum()
        
        # Categorias
        mat = df_adm['Mat_Real'].sum()
        desp = df_adm['Desp_Real'].sum()
        hh = df_adm['HH_Real_Vlr'].sum()
        imp = df_adm['Impostos'].sum()
        
        # Impacto no Faturamento Global (Aqui usamos df_obras total, pois o ADM impacta tudo)
        faturamento_global = df_obras['Vendido'].sum() 
        impacto_percentual = (custo_adm_total / faturamento_global * 100) if faturamento_global > 0 else 0

        c_kpi1, c_kpi2 = st.columns(2)
        
        with c_kpi1:
            st.markdown(f"""
            <div class="adm-box">
                <div style="color: #d29922; font-size: 0.9rem; text-transform: uppercase; font-weight: bold;">Custo Administrativo Total</div>
                <div style="font-size: 2rem; font-weight: 800; color: white;">R$ {custo_adm_total:,.2f}</div>
                <div style="color: #8b949e; font-size: 0.8rem; margin-top: 5px;">Soma de 5009, 5010 e 5011</div>
            </div>
            """, unsafe_allow_html=True)
            
        with c_kpi2:
            cor_impacto = "#da3633" if impacto_percentual > 10 else "#3fb950"
            st.markdown(f"""
            <div class="adm-box" style="border-color: {cor_impacto}">
                <div style="color: {cor_impacto}; font-size: 0.9rem; text-transform: uppercase; font-weight: bold;">Impacto no Faturamento</div>
                <div style="font-size: 2rem; font-weight: 800; color: white;">{impacto_percentual:.1f}%</div>
                <div style="color: #8b949e; font-size: 0.8rem; margin-top: 5px;">Quanto o escritório consome das vendas</div>
            </div>
            """, unsafe_allow_html=True)

        st.divider()

        c_chart1, c_chart2 = st.columns(2)
        
        with c_chart1:
            st.markdown("##### Onde estamos gastando?")
            df_pie_adm = pd.DataFrame({
                'Categoria': ['Materiais/Insumos', 'Despesas Gerais', 'Mão de Obra (Salários)', 'Impostos'],
                'Valor': [mat, desp, hh, imp]
            })
            
            fig_adm_pie = px.pie(
                df_pie_adm, values='Valor', names='Categoria', hole=0.5,
                color_discrete_sequence=['#a371f7', '#d29922', '#58a6ff', '#8b949e']
            )
            fig_adm_pie.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='white'))
            st.plotly_chart(fig_adm_pie, use_container_width=True)

        with c_chart2:
            st.markdown("##### Detalhe por Centro de Custo")
            df_ids = df_adm.groupby('Projeto').agg({'Custo_Total': 'sum', 'Descricao': 'first'}).reset_index()
            df_ids['Projeto'] = df_ids['Projeto'].astype(str)
            
            fig_adm_bar = px.bar(
                df_ids, x='Projeto', y='Custo_Total', color='Projeto',
                text_auto='.2s', hover_data=['Descricao']
            )
            fig_adm_bar.update_layout(
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', 
                font=dict(color='white'), showlegend=False,
                xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='#30363d')
            )
            st.plotly_chart(fig_adm_bar, use_container_width=True)
