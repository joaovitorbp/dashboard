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
    /* Fundo e Espaçamento */
    .stApp {background-color: #0e1117;}
    .block-container {padding-top: 1rem !important; padding-bottom: 2rem !important;}
    h1 {padding-top: 0rem !important; margin-top: -1rem !important;}
    
    /* --- ABAS (VISUAL CLEAN) --- */
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
    
    /* Box de Destaque */
    .highlight-box {
        background-color: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 15px; text-align: center;
    }
    .highlight-val { font-size: 1.5rem; font-weight: 800; color: white; }
    .highlight-lbl { color: #8b949e; font-size: 0.8rem; text-transform: uppercase; }

    /* Box de Destaque ADM */
    .adm-box {
        background-color: #161b22; border: 1px solid #d29922; border-radius: 8px; padding: 20px; text-align: center;
    }
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

df_raw['Cliente_Local'] = df_raw.apply(
    lambda row: f"{row['Cliente']} ({row['Cidade']})" if pd.notna(row['Cidade']) and str(row['Cidade']).strip() != "" else row['Cliente'], 
    axis=1
)

if 'Tipo' not in df_raw.columns:
    df_raw['Tipo'] = "Não Classificado"
else:
    df_raw['Tipo'] = df_raw['Tipo'].replace("", "Não Classificado")

# ---------------------------------------------------------
# 4. FILTROS E SEPARAÇÃO
# ---------------------------------------------------------

IDS_ADM = [5009.2025, 5010.2025, 5011.2025]
df_adm = df_raw[df_raw['Projeto'].isin(IDS_ADM)].copy()
df_obras = df_raw[~df_raw['Projeto'].isin(IDS_ADM)].copy()
df_finalizadas = df_obras[df_obras['Status'].isin(['Finalizado', 'Apresentado'])].copy()

# ---------------------------------------------------------
# 5. INTERFACE
# ---------------------------------------------------------
st.title("Análises Estratégicas")

tab1, tab2, tab3 = st.tabs(["Cliente", "Segmentos", "Custos Internos"])

# =========================================================
# ABA 1: CLIENTE
# =========================================================
with tab1:
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
            <div class="highlight-box" style="border-top: 4px solid #3fb950">
                <div class="highlight-lbl">Total Finalizado</div>
                <div class="highlight-val">R$ {total_vendido:,.2f}</div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            cor_m = "#3fb950" if margem_global >= META_MARGEM else "#da3633"
            st.markdown(f"""
            <div class="highlight-box" style="border-top: 4px solid {cor_m}">
                <div class="highlight-lbl">Margem</div>
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

        # RANKING POR PLANTA
        st.subheader("Ranking por Planta") 
        
        df_agrupado = df_finalizadas.groupby('Cliente_Local').agg({'Vendido': 'sum', 'Lucro': 'sum'}).reset_index()
        df_agrupado['Margem_%'] = (df_agrupado['Lucro'] / df_agrupado['Vendido'] * 100).fillna(0)
        df_agrupado = df_agrupado.sort_values(by='Vendido', ascending=True)

        fig_detalhe = px.bar(
            df_agrupado, y='Cliente_Local', x='Vendido', text_auto='.2s', orientation='h',
            color='Margem_%', color_continuous_scale=['#da3633', '#e3b341', '#3fb950'],
            labels={'Vendido': 'Valor Vendido (R$)', 'Cliente_Local': '', 'Margem_%': 'Margem %'}
        )
        fig_detalhe.update_layout(
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='white'),
            xaxis=dict(showgrid=True, gridcolor='#30363d'), height=500, margin=dict(t=0, l=0, r=0, b=0)
        )
        st.plotly_chart(fig_detalhe, use_container_width=True)

        st.write("")
        st.write("")

        col_cli, col_geo = st.columns(2)

        with col_cli:
            st.subheader("Ranking por Cliente")
            df_cli_only = df_finalizadas.groupby('Cliente').agg({'Vendido': 'sum', 'Lucro': 'sum'}).reset_index()
            df_cli_only['Margem_%'] = (df_cli_only['Lucro'] / df_cli_only['Vendido'] * 100).fillna(0)
            df_cli_only = df_cli_only.sort_values(by='Vendido', ascending=True)

            fig_cli = px.bar(
                df_cli_only, y='Cliente', x='Vendido', text_auto='.2s', orientation='h',
                color='Margem_%', color_continuous_scale=['#da3633', '#e3b341', '#3fb950'],
                labels={'Vendido': 'Valor Vendido (R$)', 'Cliente': ''}
            )
            fig_cli.update_layout(
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='white'),
                xaxis=dict(showgrid=True, gridcolor='#30363d'), height=350, margin=dict(l=0, r=0, t=10, b=0)
            )
            fig_cli.update_traces(marker_line_width=0)
            st.plotly_chart(fig_cli, use_container_width=True)

        with col_geo:
            st.subheader("Ranking por Cidade")
            df_geo = df_finalizadas.groupby('Cidade').agg({'Vendido': 'sum', 'Lucro': 'sum'}).reset_index()
            df_geo['Margem_%'] = (df_geo['Lucro'] / df_geo['Vendido'] * 100).fillna(0)
            df_geo = df_geo.sort_values(by='Vendido', ascending=True)

            fig_geo = px.bar(
                df_geo, y='Cidade', x='Vendido', text_auto='.2s', orientation='h',
                color='Margem_%', color_continuous_scale=['#da3633', '#e3b341', '#3fb950'],
                labels={'Vendido': 'Valor Vendido (R$)', 'Cidade': ''}
            )
            fig_geo.update_layout(
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='white'),
                xaxis=dict(showgrid=True, gridcolor='#30363d'), height=350, margin=dict(l=0, r=0, t=10, b=0)
            )
            fig_geo.update_traces(marker_line_width=0)
            st.plotly_chart(fig_geo, use_container_width=True)

# =========================================================
# ABA 2: SEGMENTOS
# =========================================================
with tab2:
    st.write("")
    
    tem_tipo = True
    if df_finalizadas['Tipo'].iloc[0] == "Não Classificado" and len(df_finalizadas['Tipo'].unique()) == 1:
        st.info("💡 Preencha a coluna 'Tipo' na planilha para ativar esta análise.")
        tem_tipo = False
    
    if tem_tipo:
        df_tipo = df_finalizadas.groupby('Tipo').agg({
            'Vendido': 'sum', 'Lucro': 'sum', 'Projeto': 'count'
        }).reset_index()
        df_tipo['Margem_Media'] = (df_tipo['Lucro'] / df_tipo['Vendido'] * 100).fillna(0)
        
        c1, c2 = st.columns(2)
        
        with c1:
            st.subheader("Participação na Receita")
            # TREEMAP
            fig_tree = px.treemap(
                df_tipo, path=['Tipo'], values='Vendido',
                color='Margem_Media', color_continuous_scale=['#da3633', '#e3b341', '#3fb950'],
            )
            fig_tree.update_layout(
                margin=dict(t=10, l=10, r=10, b=10),
                coloraxis_showscale=False
            )
            fig_tree.update_traces(
                textinfo="label+value+percent root",
                textfont=dict(color='white', size=14)
            )
            st.plotly_chart(fig_tree, use_container_width=True)
            
        with c2:
            st.subheader("Matriz Rentabilidade x Receita")
            # SCATTER PLOT
            fig_scat = px.scatter(
                df_tipo, x='Vendido', y='Margem_Media', size='Vendido', color='Tipo',
                text='Tipo', hover_name='Tipo',
                labels={'Vendido': 'Volume Vendido (R$)', 'Margem_Media': 'Rentabilidade (%)'}
            )
            fig_scat.add_hline(y=META_MARGEM, line_dash="dash", line_color="#8b949e", annotation_text=f"Meta")
            
            fig_scat.update_traces(textposition='top center', marker=dict(line=dict(width=1, color='White')))
            fig_scat.update_layout(
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'), 
                xaxis=dict(showgrid=True, gridcolor='#30363d'), 
                yaxis=dict(showgrid=True, gridcolor='#30363d'),
                showlegend=False
            )
            st.plotly_chart(fig_scat, use_container_width=True)

# =========================================================
# ABA 3: CUSTOS INTERNOS
# =========================================================
with tab3:
    st.write("")
    
    if df_adm.empty:
        st.warning("⚠️ Nenhum projeto 5009, 5010 ou 5011 encontrado.")
    else:
        # --- CÁLCULOS ---
        # 1. Total de Gastos (SEM IMPOSTOS)
        df_adm['Total_Sem_Imp'] = df_adm['Mat_Real'] + df_adm['Desp_Real'] + df_adm['HH_Real_Vlr']
        custo_adm_total = df_adm['Total_Sem_Imp'].sum()
        
        # 2. Verba Disponível
        faturamento_global = df_obras['Vendido'].sum()
        verba_permitida = faturamento_global * (META_ADM / 100.0)
        
        # 3. Impacto %
        impacto_percentual = (custo_adm_total / faturamento_global * 100) if faturamento_global > 0 else 0

        # --- KPI CARDS (ORIGINAIS) ---
        c_kpi1, c_kpi2 = st.columns(2)
        
        with c_kpi1:
            st.markdown(f"""
            <div class="adm-box">
                <div style="color: #d29922; font-size: 0.9rem; text-transform: uppercase; font-weight: bold;">Custo Administrativo</div>
                <div style="font-size: 2rem; font-weight: 800; color: white;">R$ {custo_adm_total:,.2f}</div>
            </div>
            """, unsafe_allow_html=True)
            
        with c_kpi2:
            cor_impacto = "#da3633" if impacto_percentual > META_ADM else "#3fb950"
            st.markdown(f"""
            <div class="adm-box" style="border-color: {cor_impacto}">
                <div style="color: {cor_impacto}; font-size: 0.9rem; text-transform: uppercase; font-weight: bold;">Overhead (Impacto)</div>
                <div style="font-size: 2rem; font-weight: 800; color: white;">{impacto_percentual:.1f}%</div>
                <div style="font-size: 0.7rem; color: #8b949e">Meta Max: {META_ADM:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)

        st.divider()

        # --- GRÁFICO 1: BARRA DE CONSUMO ÚNICA COM % INTERNA ---
        st.subheader("Consumo do Orçamento")
        
        # Prepara dados agrupados por ID para a barra
        df_gastos_id = df_adm.groupby('Projeto').agg({'Total_Sem_Imp': 'sum', 'Descricao': 'first'}).reset_index()
        
        # Calcula a porcentagem de cada ID em relação ao GASTO TOTAL (para mostrar dentro da barra)
        df_gastos_id['Pct_Do_Total'] = (df_gastos_id['Total_Sem_Imp'] / custo_adm_total * 100).fillna(0)
        
        # Formata o texto que vai dentro da barra: "R$ 10k (30%)"
        df_gastos_id['Rotulo'] = df_gastos_id.apply(
            lambda x: f"<b>R$ {x['Total_Sem_Imp']/1000:.0f}k</b><br>({x['Pct_Do_Total']:.0f}%)", axis=1
        )
        
        fig_progress = go.Figure()
        
        cores = ['#58a6ff', '#a371f7', '#d29922'] # Azul, Roxo, Laranja
        for i, row in df_gastos_id.iterrows():
            cor = cores[i % len(cores)]
            
            fig_progress.add_trace(go.Bar(
                y=['Consumo'], 
                x=[row['Total_Sem_Imp']], 
                name=f"{row['Projeto']} - {row['Descricao'][:15]}", 
                orientation='h',
                marker=dict(color=cor),
                text=[row['Rotulo']], # O texto formatado
                textposition='auto',  # Tenta colocar dentro, se não der, põe fora
                insidetextfont=dict(color='white', size=14, family="Arial Black"), # Fonte forte dentro
                outsidetextfont=dict(color='white'),
                hovertemplate=f"<b>{row['Descricao']}</b><br>Gasto: R$ %{{x:,.2f}}<br>Representa %{{text}}<extra></extra>"
            ))
            
        fig_progress.update_layout(
            barmode='stack',
            height=220, # Altura boa para ver os números
            margin=dict(l=0, r=0, t=30, b=10),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(
                showgrid=True, gridcolor='#30363d',
                showticklabels=True, tickfont=dict(color='#8b949e'),
                tickprefix="R$ ",
                # O eixo vai até onde for maior: A meta ou o gasto real (se estourou)
                range=[0, max(verba_permitida, custo_adm_total) * 1.15]
            ),
            yaxis=dict(showticklabels=False, title=None),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        # Linha da Meta
        fig_progress.add_vline(
            x=verba_permitida, 
            line_width=3, 
            line_dash="dash", 
            line_color="#da3633", 
            annotation_text=f"Limite Permitido (5%): R$ {verba_permitida:,.0f}", 
            annotation_position="top right",
            annotation_font=dict(color="#da3633", size=12, weight="bold")
        )
        
        st.plotly_chart(fig_progress, use_container_width=True)
        
        # Mensagem de status
        saldo = verba_permitida - custo_adm_total
        if saldo >= 0:
            st.success(f"✅ **Dentro do Orçamento:** Você ainda pode gastar **R$ {saldo:,.2f}** antes de atingir o limite de 5%.")
        else:
            st.error(f"🚨 **Orçamento Estourado:** Você excedeu o limite em **R$ {abs(saldo):,.2f}**.")
