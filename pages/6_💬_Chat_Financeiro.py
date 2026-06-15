import streamlit as st
import pandas as pd
from datetime import datetime
import sys
import os
import re

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.shared import carregar_todas_transacoes
from src.llm_service import LLMService
from src.forecast_engine import ForecastEngine
from utils.theme_utils import aplicar_tema_global

# ====================== CONFIGURAÇÃO ======================
if "configuracoes" not in st.session_state:
    st.session_state.configuracoes = {
        "groq_api_key": "",
        "llm_provider": "groq"
    }

aplicar_tema_global()

st.set_page_config(page_title="Chat Financeiro - AdaptFin", page_icon="💬", layout="wide")

# ====================== CSS ESTILO ======================
st.markdown("""
<style>
    .stApp {
        background-color: #f7f7f8;
    }
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 5rem;
        max-width: 900px;
    }
    .chat-title {
        text-align: center;
        margin-bottom: 1rem;
    }
    .chat-title h1 {
        font-size: 2rem;
        font-weight: 600;
        background: linear-gradient(135deg, #4CAF50, #2196F3);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    .chat-title p {
        color: #666;
        font-size: 0.9rem;
    }
    .status-online {
        display: inline-block;
        width: 10px;
        height: 10px;
        background-color: #4CAF50;
        border-radius: 50%;
        margin-right: 6px;
        animation: pulse 1.5s infinite;
    }
    @keyframes pulse {
        0% { opacity: 0.5; transform: scale(0.8); }
        100% { opacity: 1; transform: scale(1.2); }
    }
    .suggestions-section {
        background: linear-gradient(135deg, #f8f9fa, #ffffff);
        border-radius: 16px;
        padding: 20px;
        margin-top: 20px;
        border: 1px solid #e9ecef;
    }
    .suggestions-title {
        text-align: center;
        margin-bottom: 15px;
        font-size: 0.9rem;
        color: #6c757d;
    }
    .stButton button {
        border-radius: 20px !important;
        transition: all 0.2s !important;
    }
    .stButton button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1) !important;
    }
</style>
""", unsafe_allow_html=True)

# ====================== FUNÇÕES DE NORMALIZAÇÃO E CORREÇÃO ======================
def remover_acentos(texto):
    """Remove acentuações para tornar a busca por palavras-chave infalível"""
    texto = texto.lower()
    texto = re.sub(r'[áàâã]', 'a', texto)
    texto = re.sub(r'[éèê]', 'e', texto)
    texto = re.sub(r'[íìî]', 'i', texto)
    texto = re.sub(r'[óòôõ]', 'o', texto)
    texto = re.sub(r'[úùû]', 'u', texto)
    texto = re.sub(r'[ç]', 'c', texto)
    return texto

def add_message(role, content):
    st.session_state.chat_history.append({"role": role, "content": content})

def processar_pergunta_com_previsao(pergunta):
    """Filtra a pergunta utilizando o motor ou envia para a IA"""
    pergunta_limpa = remover_acentos(pergunta)
    forecast_engine = ForecastEngine()
    
    # 1. VERIFICAÇÃO GLOBAL: RELATÓRIOS COMPLETOS / PREVISÕES EXTENSAS
    if 'relatorio' in pergunta_limpa and 'previsao' in pergunta_limpa:
        return forecast_engine.gerar_relatorio_previsao(dados, meses=3)
        
    if '6 meses' in pergunta_limpa or 'ultimos 6' in pergunta_limpa:
        return forecast_engine.gerar_relatorio_previsao(dados, meses=6)
        
    if 'previsao completa' in pergunta_limpa:
        return forecast_engine.gerar_relatorio_previsao(dados, meses=3)

    # Dicionário mapeado sem acentos
    meses_map = {
        'janeiro': 1, 'fevereiro': 2, 'marco': 3, 'abril': 4,
        'maio': 5, 'junho': 6, 'julho': 7, 'agosto': 8,
        'setembro': 9, 'outubro': 10, 'novembro': 11, 'dezembro': 12
    }
    
    # 2. PREVISÃO DE SALDO PARA MÊS ESPECÍFICO (Futuro)
    for mes_nome, mes_num in meses_map.items():
        if mes_nome in pergunta_limpa and ('saldo' in pergunta_limpa or 'previsao' in pergunta_limpa):
            anos = re.findall(r'\b(20\d{2})\b', pergunta)
            ano = int(anos[0]) if anos else datetime.now().year
            
            # Ajuste de ano para "ano que vem"
            if 'ano que vem' in pergunta_limpa or 'proximo ano' in pergunta_limpa:
                ano = datetime.now().year + 1
                
            data_alvo = datetime(ano, mes_num, 1)
            saldo_previsto, metodo = forecast_engine.prever_saldo_data(dados, data_alvo)
            if saldo_previsto is not None:
                status = "✅ Positivo" if saldo_previsto > 0 else "⚠️ Negativo"
                return f"📊 **Previsão de Saldo para {mes_nome.capitalize()}/{ano}:** R$ {saldo_previsto:,.2f}\n\n📌 Status: {status}\n\n💡 Base: {metodo}"

    # 3. ANÁLISE DE GASTOS DE MÊS ESPECÍFICO (Histórico) - CORRIGIDO
    for mes_nome, mes_num in meses_map.items():
        if mes_nome in pergunta_limpa:
            # Palavras-chave expandidas
            palavras_analise = ['gasto', 'analise', 'quanto', 'resumo', 'mes', 'relatorio', 'extrato', 'movimentacao', 'foi']
            tem_palavra = any(p in pergunta_limpa for p in palavras_analise)
            
            # Se a pergunta tem uma das palavras OU se é uma frase curta (ex: "junho 2025", "e junho?")
            if tem_palavra or len(pergunta_limpa.split()) <= 5:
                # Procura por um ano específico na frase, senão usa o ano atual
                anos = re.findall(r'\b(20\d{2})\b', pergunta)
                ano = int(anos[0]) if anos else datetime.now().year
                return forecast_engine.analisar_gastos_mes(dados, mes_num, ano)
    
    # 4. QUANDO ACABARÁ O DINHEIRO
    if 'quando ficarei sem dinheiro' in pergunta_limpa or 'quando acaba' in pergunta_limpa or 'vou ficar sem' in pergunta_limpa:
        data_fim, motivo = forecast_engine.prever_quando_acabar_dinheiro(dados)
        if data_fim:
            dias = (data_fim - datetime.now()).days
            return f"""⚠️ **ALERTA FINANCEIRO DE RITMO DIÁRIO**\n\n{motivo}\n\n💰 **Evolução de esgotamento estimado em:** {data_fim.strftime('%d/%m/%Y')}\n📅 **Dias de segurança restantes:** {dias} dias\n\n💡 **Ações de contenção recomendadas:**\n1. Otimize despesas extras imediatas.\n2. Evite a utilização de créditos rotativos."""
    
    # 5. PLANEJAMENTO DE METAS FINANCEIRAS
    if 'quanto preciso guardar' in pergunta_limpa or 'meta para' in pergunta_limpa:
        valores = re.findall(r'R?\$?\s*(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)', pergunta)
        if valores:
            valor_alvo = float(valores[0].replace('.', '').replace(',', '.'))
            meses_restantes = 12 - datetime.now().month
            if meses_restantes <= 0:
                meses_restantes = 12
            meta_mensal = valor_alvo / meses_restantes
            return f"🎯 **Planejamento de Meta Estipulada: R$ {valor_alvo:,.2f}**\n\n📅 Horizonte temporal calculado: {meses_restantes} meses\n💵 Depósito mensal necessário: **R$ {meta_mensal:,.2f}**"
    
    # FALLBACK INTELIGENTE CASO NÃO SEJA COMANDO DIRETO (LLM)
    return llm.gerar_resposta(pergunta, dados)

def fazer_pergunta(pergunta_texto):
    add_message("user", pergunta_texto)
    with st.spinner("🤔 Analisando..."):
        resposta = processar_pergunta_com_previsao(pergunta_texto)
    add_message("assistant", resposta)
    st.rerun()

# ====================== CARREGAR DADOS E LLM ======================
dados = carregar_todas_transacoes()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

@st.cache_resource(ttl=0)
def get_llm():
    return LLMService()

llm = get_llm()

# ====================== CABEÇALHO ======================
st.markdown("""
<div class="chat-title">
    <h1>💬 Assistente Financeiro</h1>
    <p>🤖 Seu consultor pessoal de finanças - Pergunte o que quiser!</p>
</div>
""", unsafe_allow_html=True)

col_status, col_clear = st.columns([3, 1])

with col_status:
    chave = st.session_state.configuracoes.get("groq_api_key", "")
    tem_chave = len(chave) > 10

    if tem_chave and llm.is_available:
        st.markdown('<div style="margin-bottom: 15px;"><span class="status-online"></span> <span style="color: #4CAF50; font-size: 0.8rem;">IA Conectada - Groq</span></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="margin-bottom: 15px;"><span style="color: #ff9800; font-size: 0.8rem;">⚠️ Modo Offline - Configure sua chave em Configurações</span></div>', unsafe_allow_html=True)

with col_clear:
    if len(st.session_state.chat_history) > 0:
        if st.button("🗑️ Limpar Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()

# ====================== MENSAGENS DO CHAT ======================
for msg in st.session_state.chat_history:
    if msg["role"] == "user":
        st.chat_message("user", avatar="👤").write(msg["content"])
    else:
        st.chat_message("assistant", avatar="🤖").write(msg["content"])

if not st.session_state.chat_history:
    st.info("""
    💡 **Bem-vindo ao seu Assistente Financeiro!**
    
    Digite sua pergunta abaixo ou clique nas sugestões para começar.
    """)

# ====================== SUGESTÕES (Apenas no início da sessão) ======================
if not st.session_state.chat_history:
    st.markdown("""
    <div class="suggestions-section">
        <div class="suggestions-title">
            💡 Sugestões de Perguntas
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("**📊 Finanças Básicas**")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("💰 Ver saldo", use_container_width=True): fazer_pergunta("Qual meu saldo atual?")
    with col2:
        if st.button("📊 Resumo", use_container_width=True): fazer_pergunta("Resumo das minhas finanças")
    with col3:
        if st.button("🏷️ Onde gasto mais?", use_container_width=True): fazer_pergunta("Onde estou gastando mais?")
    with col4:
        if st.button("💡 Dica economia", use_container_width=True): fazer_pergunta("Como posso economizar dinheiro?")

    st.markdown("---")
    
    st.markdown("**📈 Análises de Gastos Mês a Mês**")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("📊 Maio 2026", use_container_width=True): fazer_pergunta("Analise meus gastos de maio 2026")
    with col2:
        if st.button("📊 Junho 2026", use_container_width=True): fazer_pergunta("Analise meus gastos de junho 2026")
    with col3:
        if st.button("📊 Dezembro 2026", use_container_width=True): fazer_pergunta("Analise meus gastos de dezembro 2026")
    with col4:
        if st.button("📈 Análise 6 meses", use_container_width=True): fazer_pergunta("Analise meus gastos dos últimos 6 meses")

    st.markdown("---")
    
    st.markdown("**🔮 Previsões Estruturadas**")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("🔮 Saldo em dezembro", use_container_width=True): fazer_pergunta("Qual será meu saldo em dezembro?")
    with col2:
        if st.button("⚠️ Quando fico sem dinheiro?", use_container_width=True): fazer_pergunta("Quando ficarei sem dinheiro?")
    with col3:
        if st.button("📈 Relatório previsão", use_container_width=True): fazer_pergunta("Gerar relatório de previsão de gastos")
    with col4:
        if st.button("🎯 Meta R$ 10.000", use_container_width=True): fazer_pergunta("Quanto preciso guardar para bater meta de R$ 10.000")

# ====================== INPUT DO CHAT ======================
pergunta = st.chat_input("💬 Digite sua pergunta aqui...")

if pergunta:
    add_message("user", pergunta)
    with st.spinner("🤔 Analisando..."):
        resposta = processar_pergunta_com_previsao(pergunta)
    add_message("assistant", resposta)
    st.rerun()