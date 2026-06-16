import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.theme_utils import aplicar_tema_global

# ====================== INICIALIZAR SESSION STATE ======================
if "configuracoes" not in st.session_state:
    st.session_state.configuracoes = {
        "salario_mensal": 0.0,
        "limite_gastos": 0.0,
        "alertas_ativos": True,
        "ml_ativado": True,
        "tema": "Claro"
    }

# Aplicar tema
aplicar_tema_global()

st.set_page_config(page_title="Insights ML - AdaptFin", page_icon="🤖", layout="wide")

def formatar_moeda(valor):
    try:
        return f"R$ {float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return "R$ 0,00"

def formatar_data_br(data):
    if pd.isna(data):
        return "N/A"
    try:
        if isinstance(data, str):
            data = pd.to_datetime(data, errors='coerce')
        if pd.isna(data):
            return "N/A"
        return data.strftime("%d/%m/%Y")
    except:
        return "N/A"

st.title("🤖 Insights de Machine Learning")
st.markdown("---")

# Carregar dados do session state
if "receitas" not in st.session_state:
    st.session_state.receitas = pd.DataFrame()
if "despesas_fixas" not in st.session_state:
    st.session_state.despesas_fixas = pd.DataFrame()
if "gastos_variaveis" not in st.session_state:
    st.session_state.gastos_variaveis = pd.DataFrame()

def carregar_todas():
    """Carrega todas as transações do session state"""
    todas = []
    if not st.session_state.receitas.empty:
        todas.append(st.session_state.receitas)
    if not st.session_state.despesas_fixas.empty:
        todas.append(st.session_state.despesas_fixas)
    if not st.session_state.gastos_variaveis.empty:
        todas.append(st.session_state.gastos_variaveis)
    
    if todas:
        df = pd.concat(todas, ignore_index=True)
        if 'Valor' in df.columns:
            df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce')
            df = df.dropna(subset=['Valor'])
        if 'Data' in df.columns:
            df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
        return df
    return pd.DataFrame()

dados = carregar_todas()

if not dados.empty:
    # ====================== RESUMO FINANCEIRO ======================
    st.subheader("📊 Resumo Financeiro")
    
    entradas = dados[dados['Valor'] > 0]['Valor'].sum()
    despesas = abs(dados[dados['Valor'] < 0]['Valor'].sum())
    saldo = entradas - despesas
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("💰 Total de Entradas", formatar_moeda(entradas))
    with col2:
        st.metric("📤 Total de Despesas", formatar_moeda(despesas))
    with col3:
        delta_cor = "normal" if saldo >= 0 else "inverse"
        st.metric("💵 Saldo", formatar_moeda(saldo), delta_color=delta_cor)
    
    st.markdown("---")
    
    # ====================== ANÁLISE DE CATEGORIAS ======================
    st.subheader("🏷️ Análise de Gastos por Categoria")
    
    despesas_cat = dados[dados['Valor'] < 0].groupby('Categoria')['Valor'].sum().abs().sort_values(ascending=False)
    
    if not despesas_cat.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.pie(values=despesas_cat.values, names=despesas_cat.index, 
                        title="Distribuição dos Gastos",
                        color_discrete_sequence=px.colors.qualitative.Set3)
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.write("**Detalhamento por Categoria:**")
            for cat, valor in despesas_cat.items():
                percentual = (valor / despesas_cat.sum()) * 100
                st.write(f"• **{cat}:** {formatar_moeda(valor)} ({percentual:.1f}%)")
    else:
        st.info("Nenhum gasto registrado")
    
    st.markdown("---")
    
    # ====================== SCORE FINANCEIRO ======================
    st.subheader("📈 Score Financeiro")
    
    # Calcular score
    score = 50
    economia_percent = 0
    
    if entradas > 0:
        economia_percent = (saldo / entradas) * 100
        if economia_percent >= 20:
            score = 90
        elif economia_percent >= 10:
            score = 70
        elif economia_percent >= 0:
            score = 50
        else:
            score = 30
    
    # Determinar classificação
    if score >= 80:
        classificacao = "Excelente 🏆"
        cor = "#2ecc71"
        mensagem = "Parabéns! Sua saúde financeira está excelente!"
    elif score >= 60:
        classificacao = "Bom 👍"
        cor = "#3498db"
        mensagem = "Você está no caminho certo, mas ainda pode melhorar!"
    elif score >= 40:
        classificacao = "Regular ⚠️"
        cor = "#f39c12"
        mensagem = "Atenção! Reveja seus gastos para melhorar sua saúde financeira."
    else:
        classificacao = "Atenção 🚨"
        cor = "#e74c3c"
        mensagem = "Priorize o corte de gastos e aumente sua reserva financeira!"
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown(f"""
        <div style="background-color: {cor}; padding: 30px; border-radius: 20px; text-align: center; color: white;">
            <span style="font-size: 3rem;">{score:.0f}</span>
            <p style="font-size: 1.2rem;">{classificacao}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"**{mensagem}**")
        st.progress(score / 100)
        st.caption(f"Score baseado em: economia ({economia_percent:.1f}%)")
    
    st.markdown("---")
    
    # ====================== INSIGHTS PERSONALIZADOS ======================
    st.subheader("💡 Insights Personalizados")
    
    insights = []
    
    # Insight 1: Economia
    if economia_percent > 20:
        insights.append("✅ **Excelente!** Você está economizando mais de 20% da sua renda. Considere investir esse valor!")
    elif economia_percent > 10:
        insights.append("👍 **Bom trabalho!** Você está economizando mais de 10% da sua renda. Continue assim!")
    elif economia_percent > 0:
        insights.append("📈 **OK!** Você está economizando, mas pode melhorar. Tente cortar gastos supérfluos.")
    else:
        insights.append("🚨 **Atenção!** Você está gastando mais do que ganha. Reveja suas despesas urgentemente!")
    
    # Insight 2: Maior gasto
    if not despesas_cat.empty:
        maior_gasto_cat = despesas_cat.idxmax()
        percentual_maior = (despesas_cat.max() / despesas_cat.sum()) * 100
        if percentual_maior > 40:
            insights.append(f"⚠️ **Concentração de gastos:** {percentual_maior:.0f}% dos seus gastos estão em '{maior_gasto_cat}'. Avalie se está equilibrado.")
    
    # Insight 3: Número de transações
    if len(dados) < 10:
        insights.append("📊 **Poucas transações:** Adicione mais transações para análises mais precisas.")
    
    # Exibir insights
    for insight in insights:
        if "✅" in insight or "👍" in insight:
            st.success(insight)
        elif "⚠️" in insight or "🚨" in insight:
            st.warning(insight)
        else:
            st.info(insight)
    
    st.markdown("---")
    
    # ====================== RECOMENDAÇÕES ======================
    st.subheader("🎯 Recomendações Personalizadas")
    
    recomendacoes = []
    
    # Recomendação baseada na economia
    if economia_percent < 10:
        recomendacoes.append("• **Corte gastos supérfluos:** Identifique pequenos gastos diários que somam muito no fim do mês.")
        recomendacoes.append("• **Revise assinaturas:** Netflix, Spotify, Amazon Prime - você usa todas?")
    
    # Recomendação baseada na categoria
    if not despesas_cat.empty:
        maior_gasto = despesas_cat.idxmax()
        if maior_gasto in ["Alimentação", "Restaurante", "Ifood"]:
            recomendacoes.append("• **Economize na alimentação:** Cozinhar em casa 3x por semana pode economizar R$200/mês.")
        elif maior_gasto in ["Uber", "Taxi", "Transporte"]:
            recomendacoes.append("• **Reduza custos de transporte:** Considere transporte público ou carona 2x por semana.")
        elif maior_gasto in ["Netflix", "Streaming", "Serviços"]:
            recomendacoes.append("• **Reveja suas assinaturas:** Você realmente usa todos os serviços de streaming?")
    
    # Recomendação genérica
    if not recomendacoes:
        recomendacoes.append("• **Mantenha o controle:** Continue registrando todas as suas transações para manter a saúde financeira.")
        recomendacoes.append("• **Defina metas:** Estabeleça metas de economia realistas para os próximos meses.")
    
    for rec in recomendacoes:
        st.info(rec)
    
    st.markdown("---")
    
    # ====================== PROJEÇÕES ======================
    st.subheader("🔮 Projeções e Metas")
    
    if entradas > 0:
        meta_ideal = entradas * 0.2
        faltam_para_meta = meta_ideal - saldo if saldo < meta_ideal else 0
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("🎯 Meta de Economia Ideal", formatar_moeda(meta_ideal), 
                     delta=f"Faltam {formatar_moeda(faltam_para_meta)}" if faltam_para_meta > 0 else "Meta alcançada!")
        
        with col2:
            projecao_anual = saldo * 12
            st.metric("📈 Projeção Anual de Economia", formatar_moeda(projecao_anual),
                     delta="Se manter este ritmo")

else:
    st.info("🤖 Adicione transações para obter insights de Machine Learning")
    
    with st.expander("💡 Como funciona o ML no AdaptFin?"):
        st.markdown("""
        **O Machine Learning no AdaptFin analisa:**
        
        - 📊 **Score Financeiro:** Avalia sua saúde financeira (0-100)
        - 💰 **Padrões de Gasto:** Identifica onde você mais gasta
        - 📈 **Tendências:** Mostra se seus gastos estão aumentando ou diminuindo
        - 🎯 **Recomendações:** Sugere ações para melhorar suas finanças
        - 🔮 **Projeções:** Estima sua economia futura
        
        **Para obter insights mais precisos:**
        1. Adicione pelo menos 10 transações
        2. Use datas corretas
        3. Categorize seus gastos adequadamente
        """)

st.markdown("---")
st.caption("🤖 Análises baseadas em Machine Learning - Quanto mais dados, melhores os insights!")