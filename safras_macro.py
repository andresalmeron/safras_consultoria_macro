import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Configuração da Página
st.set_page_config(page_title="Visão Macro: Evolução das Safras", layout="wide")

st.title("📈 Visão Macro: Evolução Histórica das Safras")
st.markdown("""
Este painel consolida as tendências históricas.
**Dica:** Passe o mouse sobre as barras para ver os valores exatos.
""")

# --- Função de Formatação Brasileira ---
def format_br(valor, tipo):
    if pd.isna(valor):
        return "-"
    if tipo == 'dinheiro':
        texto = f"R$ {valor:,.2f}"
        return texto.replace(',', 'X').replace('.', ',').replace('X', '.')
    elif tipo == 'inteiro':
        texto = f"{valor:,.0f}"
        return texto.replace(',', 'X').replace('.', ',').replace('X', '.')
    elif tipo == 'porcentagem':
        texto = f"{valor:.1%}"
        return texto.replace('.', ',')
    return str(valor)

# --- Upload ---
st.sidebar.header("📂 Carregar Dados")
file_sem_mf = st.sidebar.file_uploader("Upload: Planilha Sem MF", type=["xlsx", "csv"])
file_mf = st.sidebar.file_uploader("Upload: Planilha Com MF", type=["xlsx", "csv"])

@st.cache_data
def load_data(file):
    try:
        if file.name.endswith('.csv'):
            return pd.read_csv(file)
        else:
            return pd.read_excel(file)
    except Exception as e:
        st.error(f"Erro ao ler o arquivo {file.name}: {e}")
        return None

# --- Função de Plotagem Limpa (Hover Only) ---
def plot_comparison(df_sem, df_mf, metric_col, title, format_type, color_sem='#4c72b0', color_mf='#55a868'):
    
    fig = go.Figure()

    # Prepara o template do Hover (Tooltip)
    if format_type == 'dinheiro':
        hover_template = '%{y:,.2f}' # Formato base do D3, ajustamos visualmente no eixo se precisar
    elif format_type == 'porcentagem':
        hover_template = '%{y:.1%}'
    else:
        hover_template = '%{y}'

    # Série Sem MF
    fig.add_trace(go.Bar(
        x=df_sem['Turma'],
        y=df_sem[metric_col],
        name='Sem MF',
        marker_color=color_sem,
        hovertemplate=f"Turma %{{x}}<br>Sem MF: <b>{hover_template}</b><extra></extra>"
    ))

    # Série Com MF
    fig.add_trace(go.Bar(
        x=df_mf['Turma'],
        y=df_mf[metric_col],
        name='Com MF',
        marker_color=color_mf,
        hovertemplate=f"Turma %{{x}}<br>Com MF: <b>{hover_template}</b><extra></extra>"
    ))

    fig.update_layout(
        title=title,
        xaxis_title="Turma (Safra)",
        yaxis_title=metric_col,
        barmode='group',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=400,
        margin=dict(l=20, r=20, t=60, b=20),
        hovermode="x unified" # Mostra ambos os valores ao passar o mouse em uma turma
    )
    
    fig.update_xaxes(type='category')
    
    # Formatação do Eixo Y para ficar bonito
    if format_type == 'porcentagem':
        fig.update_yaxes(tickformat=".0%")
    
    return fig

if file_sem_mf and file_mf:
    df_sem_mf = load_data(file_sem_mf)
    df_mf = load_data(file_mf)

    if df_sem_mf is not None and df_mf is not None:
        
        # --- SELETOR DE FAIXA (RANGE SLIDER) ---
        # Pega todas as turmas disponíveis em ambos os arquivos
        all_turmas = sorted(list(set(df_sem_mf['Turma'].unique()) | set(df_mf['Turma'].unique())))
        min_turma, max_turma = min(all_turmas), max(all_turmas)

        st.sidebar.markdown("---")
        st.sidebar.subheader("📅 Filtro de Período")
        
        # Slider duplo para selecionar inicio e fim
        start_turma, end_turma = st.sidebar.slider(
            "Selecione o intervalo de Turmas:",
            min_value=min_turma,
            max_value=max_turma,
            value=(min_turma, max_turma) # Default: Todas
        )
        
        # Filtragem dos Dataframes
        df_s_filtered = df_sem_mf[(df_sem_mf['Turma'] >= start_turma) & (df_sem_mf['Turma'] <= end_turma)]
        df_m_filtered = df_mf[(df_mf['Turma'] >= start_turma) & (df_mf['Turma'] <= end_turma)]

        # --- GRÁFICO 1: Volume de Ingressantes ---
        st.subheader("1. Volume: Total de Ingressantes")
        fig1 = plot_comparison(
            df_s_filtered, df_m_filtered, 
            'Entradas Totais', 
            'Total de Entradas', 
            'inteiro'
        )
        st.plotly_chart(fig1, use_container_width=True)
        st.markdown("---")

        # --- GRÁFICO 2: Volume de Ativos ---
        st.subheader("2. Volume: Total de Ativos(as)")
        fig2 = plot_comparison(
            df_s_filtered, df_m_filtered, 
            'Ativos(as)', 
            'Total de Consultores Ativos', 
            'inteiro'
        )
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown("---")

        # --- GRÁFICO 3: Sobrevivência (NOVO) ---
        st.subheader("3. Retenção: Sobrevivência (%)")
        fig3 = plot_comparison(
            df_s_filtered, df_m_filtered, 
            'Sobrevivência (%)', 
            'Taxa de Sobrevivência por Safra', 
            'porcentagem'
        )
        st.plotly_chart(fig3, use_container_width=True)
        st.markdown("---")

        # --- GRÁFICO 4: Performance Média (AuC) ---
        st.subheader("4. Performance: AuC Médio (Exc. Desligados)")
        fig4 = plot_comparison(
            df_s_filtered, df_m_filtered, 
            'AuC Médio (Exc. desl.)', 
            'AuC Médio por Safra (R$)', 
            'dinheiro'
        )
        st.plotly_chart(fig4, use_container_width=True)
        st.markdown("---")

        # --- GRÁFICO 5: Performance Mediana (AuC) ---
        st.subheader("5. Performance: AuC Mediano (Exc. Desligados)")
        fig5 = plot_comparison(
            df_s_filtered, df_m_filtered, 
            'AuC Mediano (Exc. desl.)', 
            'AuC Mediano por Safra (R$)', 
            'dinheiro'
        )
        st.plotly_chart(fig5, use_container_width=True)

else:
    st.info("👈 Faça o upload das planilhas para gerar a visão consolidada.")
