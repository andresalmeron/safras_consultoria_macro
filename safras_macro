import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Configuração da Página
st.set_page_config(page_title="Visão Macro: Evolução das Safras", layout="wide")

st.title("📈 Visão Macro: Evolução Histórica das Safras (Geeko Mode 🦎)")
st.markdown("""
Este painel consolida os dados de **todas as turmas** disponíveis nas planilhas, permitindo identificar tendências de volume e performance entre os grupos **Com MF** e **Sem MF**.
""")

# --- Função de Formatação Brasileira (Reutilizada) ---
def format_br(valor, tipo):
    if pd.isna(valor):
        return "-"
    if tipo == 'dinheiro':
        texto = f"R$ {valor:,.2f}"
        return texto.replace(',', 'X').replace('.', ',').replace('X', '.')
    elif tipo == 'inteiro':
        texto = f"{valor:,.0f}"
        return texto.replace(',', 'X').replace('.', ',').replace('X', '.')
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

# --- Função de Plotagem Genérica ---
def plot_comparison(df_sem, df_mf, metric_col, title, format_type, color_sem='#4c72b0', color_mf='#55a868'):
    """
    Gera um gráfico de barras agrupadas comparando toda a série histórica.
    """
    # Garantir que as turmas estão ordenadas
    df_sem = df_sem.sort_values('Turma')
    df_mf = df_mf.sort_values('Turma')

    fig = go.Figure()

    # Série Sem MF
    fig.add_trace(go.Bar(
        x=df_sem['Turma'],
        y=df_sem[metric_col],
        name='Sem MF',
        marker_color=color_sem,
        text=[format_br(v, format_type) for v in df_sem[metric_col]],
        textposition='auto'
    ))

    # Série Com MF
    fig.add_trace(go.Bar(
        x=df_mf['Turma'],
        y=df_mf[metric_col],
        name='Com MF',
        marker_color=color_mf,
        text=[format_br(v, format_type) for v in df_mf[metric_col]],
        textposition='auto'
    ))

    fig.update_layout(
        title=title,
        xaxis_title="Turma (Safra)",
        yaxis_title=metric_col,
        barmode='group',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        height=450,
        margin=dict(l=20, r=20, t=60, b=20)
    )
    
    # Garantir que o eixo X mostre todas as turmas como categorias (não números contínuos)
    fig.update_xaxes(type='category')
    
    return fig

if file_sem_mf and file_mf:
    df_sem_mf = load_data(file_sem_mf)
    df_mf = load_data(file_mf)

    if df_sem_mf is not None and df_mf is not None:
        
        # Filtros de Visualização (Opcional, mas útil se houver muitas turmas)
        all_turmas = sorted(list(set(df_sem_mf['Turma'].unique()) | set(df_mf['Turma'].unique())))
        
        st.sidebar.markdown("---")
        turmas_selected = st.sidebar.multiselect(
            "Filtrar Turmas Específicas (Opcional)", 
            all_turmas, 
            default=all_turmas
        )
        
        if turmas_selected:
            # Filtrar Dataframes
            df_s_filtered = df_sem_mf[df_sem_mf['Turma'].isin(turmas_selected)]
            df_m_filtered = df_mf[df_mf['Turma'].isin(turmas_selected)]

            # --- GRÁFICO 1: Volume de Ingressantes ---
            st.subheader("1. Volume: Total de Ingressantes")
            fig1 = plot_comparison(
                df_s_filtered, df_m_filtered, 
                'Entradas Totais', 
                'Total de Entradas por Safra', 
                'inteiro'
            )
            st.plotly_chart(fig1, use_container_width=True)
            st.markdown("---")

            # --- GRÁFICO 2: Volume de Ativos ---
            st.subheader("2. Volume: Total de Ativos(as)")
            fig2 = plot_comparison(
                df_s_filtered, df_m_filtered, 
                'Ativos(as)', 
                'Total de Consultores Ativos por Safra', 
                'inteiro'
            )
            st.plotly_chart(fig2, use_container_width=True)
            st.markdown("---")

            # --- GRÁFICO 3: Performance Média (AuC) ---
            st.subheader("3. Performance: AuC Médio (Exc. Desligados)")
            # Nota: Usando Exc. Desl. como padrão de performance real
            fig3 = plot_comparison(
                df_s_filtered, df_m_filtered, 
                'AuC Médio (Exc. desl.)', 
                'AuC Médio por Safra (R$)', 
                'dinheiro'
            )
            st.plotly_chart(fig3, use_container_width=True)
            st.markdown("---")

            # --- GRÁFICO 4: Performance Mediana (AuC) ---
            st.subheader("4. Performance: AuC Mediano (Exc. Desligados)")
            fig4 = plot_comparison(
                df_s_filtered, df_m_filtered, 
                'AuC Mediano (Exc. desl.)', 
                'AuC Mediano por Safra (R$)', 
                'dinheiro'
            )
            st.plotly_chart(fig4, use_container_width=True)

        else:
            st.warning("Selecione pelo menos uma turma no filtro lateral.")
            
else:
    st.info("👈 Faça o upload das planilhas para gerar a visão consolidada.")
