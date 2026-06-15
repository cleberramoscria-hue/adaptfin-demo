"""
Engine do Chatbot Financeiro Inteligente
"""
import re
from datetime import datetime, timedelta
import pandas as pd

class ChatbotEngine:
    """Chatbot para conversas financeiras naturais"""
    
    def __init__(self, df_transacoes):
        self.df = df_transacoes
        self.contexto = {}
        self.historico_conversa = []
        
    def processar_mensagem(self, mensagem):
        """Processa mensagem do usuário e retorna resposta"""
        mensagem = mensagem.lower().strip()
        self.historico_conversa.append({"role": "user", "content": mensagem})
        
        # Detectar intenção
        intencao = self._detectar_intencao(mensagem)
        
        # Gerar resposta baseada na intenção
        resposta = self._gerar_resposta(intencao, mensagem)
        
        self.historico_conversa.append({"role": "assistant", "content": resposta})
        return resposta
    
    def _detectar_intencao(self, mensagem):
        """Detecta a intenção da mensagem"""
        intencoes = {
            'saldo': ['saldo', 'quanto tenho', 'quanto sobrou', 'situação atual'],
            'gastos': ['gastei', 'quanto gastei', 'total de gastos', 'despesas'],
            'categoria': ['categoria', 'onde gasto', 'maior gasto', 'categoria mais'],
            'economia': ['economizar', 'economia', 'sobra', 'poupar', 'guardar'],
            'previsao': ['previsão', 'vou gastar', 'projeção', 'próximo mês'],
            'aumento': ['aumentou', 'por que', 'motivo', 'razão'],
            'dica': ['dica', 'sugestão', 'recomendação', 'ajuda'],
            'resumo': ['resumo', 'relatório', 'visão geral', 'dashboard'],
            'anomalia': ['anormal', 'estranho', 'diferente', 'fora do comum'],
            'meta': ['meta', 'objetivo', 'alvo', 'planejamento']
        }
        
        for intencao, palavras in intencoes.items():
            if any(palavra in mensagem for palavra in palavras):
                return intencao
        
        return 'geral'
    
    def _gerar_resposta(self, intencao, mensagem):
        """Gera resposta baseada na intenção"""
        respostas = {
            'saldo': self._resposta_saldo,
            'gastos': self._resposta_gastos,
            'categoria': self._resposta_categoria,
            'economia': self._resposta_economia,
            'previsao': self._resposta_previsao,
            'aumento': self._resposta_aumento,
            'dica': self._resposta_dica,
            'resumo': self._resposta_resumo,
            'anomalia': self._resposta_anomalia,
            'meta': self._resposta_meta
        }
        
        if intencao in respostas:
            return respostas[intencao]()
        
        return self._resposta_geral()
    
    def _resposta_saldo(self):
        """Resposta sobre saldo"""
        receitas = self.df[self.df['Valor'] > 0]['Valor'].sum()
        despesas = abs(self.df[self.df['Valor'] < 0]['Valor'].sum())
        saldo = receitas - despesas
        
        if saldo > 0:
            return f"💰 Seu saldo atual é de **R$ {saldo:.2f}**. Você está no azul! Continue assim! 🎉"
        elif saldo < 0:
            return f"⚠️ Seu saldo atual é de **R$ {saldo:.2f}**. Você está no vermelho. Hora de rever seus gastos! 📉"
        else:
            return f"⚖️ Seu saldo está zerado. Suas receitas e despesas estão equilibradas."
    
    def _resposta_gastos(self):
        """Resposta sobre gastos"""
        total_gastos = abs(self.df[self.df['Valor'] < 0]['Valor'].sum())
        media_gasto = abs(self.df[self.df['Valor'] < 0]['Valor'].mean())
        
        return f"📊 Seus gastos totais são de **R$ {total_gastos:.2f}**. Em média, você gasta **R$ {media_gasto:.2f}** por transação."
    
    def _resposta_categoria(self):
        """Resposta sobre categorias"""
        gastos_cat = self.df[self.df['Valor'] < 0].groupby('Categoria')['Valor'].sum().abs()
        
        if not gastos_cat.empty:
            top_cat = gastos_cat.idxmax()
            top_valor = gastos_cat.max()
            return f"🏆 Sua categoria com maior gasto é **{top_cat}** com **R$ {top_valor:.2f}**."
        
        return "Nenhum gasto registrado ainda."
    
    def _resposta_economia(self):
        """Resposta sobre economia"""
        receitas = self.df[self.df['Valor'] > 0]['Valor'].sum()
        despesas = abs(self.df[self.df['Valor'] < 0]['Valor'].sum())
        economia = receitas - despesas
        
        if economia > 0:
            percentual = (economia / receitas) * 100 if receitas > 0 else 0
            return f"💪 Você está economizando **R$ {economia:.2f}** ({percentual:.1f}% da renda). Continue firme!"
        else:
            return f"⚠️ Você precisa economizar **R$ {abs(economia):.2f}** para equilibrar suas contas."
    
    def _resposta_previsao(self):
        """Resposta com previsões"""
        gasto_medio_diario = abs(self.df[self.df['Valor'] < 0]['Valor'].mean())
        dias_restantes = 30 - datetime.now().day
        previsao = gasto_medio_diario * dias_restantes
        
        return f"🔮 Baseado no seu histórico, você deve gastar aproximadamente **R$ {previsao:.2f}** nos próximos {dias_restantes} dias."
    
    def _resposta_aumento(self):
        """Resposta sobre aumento de gastos"""
        hoje = datetime.now()
        mes_atual = hoje.month
        mes_anterior = mes_atual - 1 if mes_atual > 1 else 12
        
        gasto_atual = abs(self.df[self.df['Data'].dt.month == mes_atual]['Valor'].sum())
        gasto_anterior = abs(self.df[self.df['Data'].dt.month == mes_anterior]['Valor'].sum())
        
        if gasto_anterior > 0:
            variacao = ((gasto_atual - gasto_anterior) / gasto_anterior) * 100
        else:
            variacao = 0
        
        if variacao > 10:
            return f"📈 Seus gastos aumentaram **{variacao:.1f}%** em relação ao mês passado. Reveja suas despesas!"
        elif variacao < -10:
            return f"📉 Seus gastos diminuíram **{abs(variacao):.1f}%**. Parabéns!"
        else:
            return f"⚖️ Seus gastos estão estáveis, com variação de **{variacao:.1f}%** em relação ao mês passado."
    
    def _resposta_dica(self):
        """Resposta com dicas"""
        dicas = [
            "🍽️ Cozinhar em casa 3x por semana pode economizar R$ 200/mês",
            "☕ Levar café de casa economiza até R$ 150/mês",
            "🎬 Reveja suas assinaturas de streaming - você usa todas?",
            "🚗 Use transporte público 2x por semana e economize combustível",
            "🛍️ Espere 24h antes de comprar por impulso",
            "💡 Desligue eletrônicos da tomada para economizar energia",
            "📱 Revise seu plano de celular - talvez tenha opções mais baratas"
        ]
        
        import random
        return f"💡 Dica do dia: {random.choice(dicas)}"
    
    def _resposta_resumo(self):
        """Resumo completo"""
        receitas = self.df[self.df['Valor'] > 0]['Valor'].sum()
        despesas = abs(self.df[self.df['Valor'] < 0]['Valor'].sum())
        saldo = receitas - despesas
        
        gastos_cat = self.df[self.df['Valor'] < 0].groupby('Categoria')['Valor'].sum().abs()
        top_cat = gastos_cat.idxmax() if not gastos_cat.empty else "Nenhuma"
        
        return f"""📊 **SEU RESUMO FINANCEIRO**

💰 Receitas: R$ {receitas:.2f}
📤 Despesas: R$ {despesas:.2f}
💵 Saldo: R$ {saldo:.2f}
🏆 Maior categoria: {top_cat}
📈 Total de transações: {len(self.df)}

{self._get_motivacao(saldo)}"""
    
    def _resposta_anomalia(self):
        """Resposta sobre anomalias"""
        from .anomaly_engine import AnomalyEngine
        anomaly_engine = AnomalyEngine()
        anomalies = anomaly_engine.detect_anomalies(self.df)
        
        if not anomalies.empty:
            return f"🚨 Detectei {len(anomalies)} gastos fora do padrão. O maior foi R$ {anomalies['Valor'].max():.2f}. Recomendo revisar sua fatura."
        else:
            return "✅ Não identifiquei nenhum gasto anormal. Seus padrões de consumo estão consistentes!"
    
    def _resposta_meta(self):
        """Resposta sobre metas"""
        receitas = self.df[self.df['Valor'] > 0]['Valor'].sum()
        meta_ideal = receitas * 0.2
        
        return f"🎯 **Meta Financeira Ideal**\n\nBaseado na sua renda de R$ {receitas:.2f}:\n• Economizar: R$ {meta_ideal:.2f}/mês (20%)\n• Gastos essenciais: R$ {receitas*0.5:.2f} (50%)\n• Lazer: R$ {receitas*0.3:.2f} (30%)\n\nSiga a regra 50-30-20!"
    
    def _resposta_geral(self):
        """Resposta geral para perguntas não reconhecidas"""
        return """🤖 **Como posso ajudar?**

Posso responder perguntas como:
• 💰 "Qual meu saldo?"
• 📊 "Resumo das minhas finanças"
• 🏷️ "Onde gasto mais?"
• 💡 "Dica de economia"
• 📈 "Por que minha fatura aumentou?"
• 🔮 "Previsão para próximo mês"

O que você gostaria de saber?"""
    
    def _get_motivacao(self, saldo):
        """Frase motivacional baseada no saldo"""
        if saldo > 1000:
            return "🎉 EXCELENTE! Você está construindo uma ótima reserva financeira!"
        elif saldo > 0:
            return "👍 Bom trabalho! Continue assim e aumente sua economia!"
        elif saldo == 0:
            return "⚖️ Equilibrado! Tente economizar um pouco para imprevistos."
        else:
            return "💪 Força! Com planejamento você vai reverter esse quadro. Comece cortando gastos supérfluos."