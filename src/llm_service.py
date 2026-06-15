"""
Serviço de LLM - Integração com Groq (Recomendado)
"""
import streamlit as st
import pandas as pd
from datetime import datetime
import requests

class LLMService:
    """Serviço para integração com Groq API"""
    
    def __init__(self):
        # Recarregar configurações atuais
        if "configuracoes" not in st.session_state:
            st.session_state.configuracoes = {}
        
        self.api_key = st.session_state.configuracoes.get("groq_api_key", "")
        self.is_available = False
        self.base_url = "https://api.groq.com/openai/v1"
        
        # Verificar se a chave existe
        if self.api_key and len(self.api_key) > 10:
            self.is_available = True
            print(f"✅ Groq API configurada")
        else:
            print("⚠️ Groq API não configurada")
    
    def _call_groq(self, prompt, timeout=15):
        """Chama a API do Groq com timeout"""
        if not self.is_available:
            return None
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": "Você é um assistente financeiro especialista. Responda em português brasileiro de forma clara, prática e direta. Seja breve e objetivo."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=timeout
            )
            
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                print(f"Erro Groq: {response.status_code}")
                return None
        except requests.exceptions.Timeout:
            print("Timeout na chamada Groq")
            return None
        except Exception as e:
            print(f"Erro ao chamar Groq: {e}")
            return None
    
    def gerar_resposta(self, pergunta, df_transacoes):
        """Gera resposta usando Groq"""
        # Se não tem chave, usar fallback rápido
        if not self.is_available:
            return self._fallback_resposta(pergunta, df_transacoes)
        
        # Preparar contexto
        contexto = self._preparar_contexto(df_transacoes)
        
        prompt = f"""
        Você é um assistente financeiro especialista.
        
        DADOS DO USUÁRIO:
        {contexto}
        
        PERGUNTA: {pergunta}
        
        Responda de forma clara, prática e direta em português brasileiro.
        Seja amigável e dê recomendações acionáveis.
        """
        
        resposta = self._call_groq(prompt, timeout=10)
        
        if resposta:
            return resposta
        else:
            return self._fallback_resposta(pergunta, df_transacoes)
    
    def analisar_gastos_periodo(self, df_transacoes, meses=6):
        """Analisa gastos dos últimos meses"""
        if not self.is_available:
            return self._analisar_gastos_periodo_fallback(df_transacoes, meses)
        
        contexto = self._preparar_contexto(df_transacoes)
        
        prompt = f"""
        Analise os gastos dos ÚLTIMOS {meses} MESES do usuário.
        
        DADOS:
        {contexto}
        
        FORMATO DA RESPOSTA:
        1. Top 3 categorias de maior gasto
        2. Tendência dos gastos
        3. 3 recomendações práticas para economizar
        
        Seja objetivo e direto.
        """
        
        resposta = self._call_groq(prompt, timeout=15)
        
        if resposta:
            return resposta
        else:
            return self._analisar_gastos_periodo_fallback(df_transacoes, meses)
    
    def criar_plano_economia(self, df_transacoes, valor_alvo, prazo_meses=12):
        """Cria plano de economia"""
        if not self.is_available:
            return self._criar_plano_economia_fallback(df_transacoes, valor_alvo, prazo_meses)
        
        meta_mensal = valor_alvo / prazo_meses
        contexto = self._preparar_contexto(df_transacoes)
        
        prompt = f"""
        Crie um plano de economia PERSONALIZADO.
        
        DADOS DO USUÁRIO:
        {contexto}
        
        OBJETIVO: Economizar R$ {valor_alvo:,.2f} em {prazo_meses} meses
        META MENSAL: R$ {meta_mensal:,.2f}
        
        FORMATO DA RESPOSTA:
        1. Análise do orçamento atual
        2. Onde cortar gastos (baseado nos dados)
        3. Estratégias práticas
        
        Seja realista e motivador.
        """
        
        resposta = self._call_groq(prompt, timeout=15)
        
        if resposta:
            return resposta
        else:
            return self._criar_plano_economia_fallback(df_transacoes, valor_alvo, prazo_meses)
    
    def _preparar_contexto(self, df):
        """Prepara contexto das transações"""
        if df.empty:
            return "Nenhuma transação cadastrada ainda."
        
        entradas = df[df['Valor'] > 0]['Valor'].sum()
        saidas = abs(df[df['Valor'] < 0]['Valor'].sum())
        saldo = entradas - saidas
        
        gastos_categoria = df[df['Valor'] < 0].groupby('Categoria')['Valor'].sum().abs()
        
        contexto = f"""
        Resumo Financeiro:
        - Total de entradas: R$ {entradas:,.2f}
        - Total de saídas: R$ {saidas:,.2f}
        - Saldo: R$ {saldo:,.2f}
        - Total de transações: {len(df)}
        
        Gastos por categoria:
        """
        
        for cat, valor in gastos_categoria.nlargest(5).items():
            contexto += f"\n  * {cat}: R$ {valor:,.2f}"
        
        return contexto
    
    def _fallback_resposta(self, pergunta, df):
        """Resposta de fallback quando API não está disponível"""
        pergunta_lower = pergunta.lower()
        
        if "saldo" in pergunta_lower:
            entradas = df[df['Valor'] > 0]['Valor'].sum() if not df.empty else 0
            saidas = abs(df[df['Valor'] < 0]['Valor'].sum()) if not df.empty else 0
            return f"💰 **Seu saldo atual é de R$ {entradas - saidas:,.2f}**"
        
        elif "gasto" in pergunta_lower and "onde" in pergunta_lower:
            if not df.empty:
                gastos = df[df['Valor'] < 0].groupby('Categoria')['Valor'].sum().abs()
                if not gastos.empty:
                    top = gastos.idxmax()
                    return f"🏷️ **Sua categoria com maior gasto é '{top}'**"
            return "Adicione transações para análise."
        
        elif "resumo" in pergunta_lower:
            if not df.empty:
                entradas = df[df['Valor'] > 0]['Valor'].sum()
                saidas = abs(df[df['Valor'] < 0]['Valor'].sum())
                return f"📊 **Resumo:** Entradas R$ {entradas:,.2f} | Saídas R$ {saidas:,.2f} | Saldo R$ {entradas - saidas:,.2f}"
            return "Nenhuma transação cadastrada."
        
        elif "economizar" in pergunta_lower or "plano" in pergunta_lower:
            return "💡 **Dicas de economia:**\n1. Corte 20% dos gastos supérfluos\n2. Reveja assinaturas mensais\n3. Cozinhe mais em casa\n4. Use transporte público\n5. Cancele serviços não utilizados"
        
        return """
💬 **Posso ajudar com:**
- "Qual meu saldo?"
- "Resumo das minhas finanças"
- "Onde estou gastando mais?"
- "Como economizar dinheiro?"
- "Analise meus gastos"

💡 **Dica:** Configure sua API Key do Groq em Configurações para respostas mais avançadas!
"""
    
    def _analisar_gastos_periodo_fallback(self, df, meses):
        """Fallback para análise de período"""
        if df.empty:
            return "Adicione transações para análise."
        
        gastos = df[df['Valor'] < 0].copy()
        gastos['Valor'] = gastos['Valor'].abs()
        
        if 'Data' in gastos.columns:
            data_limite = datetime.now() - pd.DateOffset(months=meses)
            gastos = gastos[gastos['Data'] >= data_limite]
        
        gastos_cat = gastos.groupby('Categoria')['Valor'].sum()
        
        resultado = f"📊 **ÚLTIMOS {meses} MESES**\n\n"
        for cat, val in gastos_cat.nlargest(3).items():
            resultado += f"• {cat}: R$ {val:,.2f}\n"
        
        resultado += "\n💡 **Recomendações:**\n• Reduza gastos na maior categoria\n• Reveja assinaturas mensais"
        
        return resultado
    
    def _criar_plano_economia_fallback(self, df, valor_alvo, prazo_meses):
        """Fallback para plano de economia"""
        meta_mensal = valor_alvo / prazo_meses
        
        if not df.empty:
            entradas = df[df['Valor'] > 0]['Valor'].sum()
            saidas = abs(df[df['Valor'] < 0]['Valor'].sum())
            resultado = f"""
🎯 **PLANO PARA ECONOMIZAR R$ {valor_alvo:,.2f} EM {prazo_meses} MESES**

**Meta mensal:** R$ {meta_mensal:,.2f}
**Sua renda:** R$ {entradas:,.2f}
**Seus gastos:** R$ {saidas:,.2f}

**Estratégias:**
1. Corte 20% dos gastos na maior categoria
2. Reduza delivery e refeições fora
3. Reveja assinaturas mensais (streaming, apps)
4. Use transporte público 2x por semana
5. Cancele serviços não utilizados

**Desafio:** Tente implementar 2 dessas estratégias esta semana!
"""
        else:
            resultado = f"""
🎯 **PLANO PARA ECONOMIZAR R$ {valor_alvo:,.2f} EM {prazo_meses} MESES**

**Meta mensal:** R$ {meta_mensal:,.2f}

**Estratégias:**
1. Corte 20% dos gastos supérfluos
2. Reduza delivery e refeições fora
3. Reveja assinaturas mensais
4. Use transporte público
5. Cancele serviços não utilizados
"""
        return resultado