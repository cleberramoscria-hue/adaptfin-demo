"""
Assistente Financeiro Conversacional com IA
"""
import re
import pandas as pd
from datetime import datetime, timedelta
import json

class FinancialChatbot:
    """Chatbot financeiro para responder perguntas sobre gastos"""
    
    def __init__(self, df_transacoes):
        self.df = df_transacoes
        self.historico = []
        
    def processar_pergunta(self, pergunta, resposta_anterior=""):
        """Processa a pergunta e retorna resposta inteligente"""
        pergunta = pergunta.lower().strip()
        
        # Análise de intenção
        if any(p in pergunta for p in ["quanto posso gastar", "posso gastar", "limite de gastos"]):
            return self._resposta_limite_gastos()
        
        elif any(p in pergunta for p in ["quanto sobra", "quanto economizar", "quanto economizei"]):
            return self._resposta_economia()
        
        elif any(p in pergunta for p in ["fatura aumentou", "gastei mais", "maior gasto", "por que aumentou"]):
            return self._resposta_analise_aumento()
        
        elif any(p in pergunta for p in ["onde estou desperdiçando", "desperdício", "gasto desnecessário"]):
            return self._resposta_desperdicio()
        
        elif any(p in pergunta for p in ["economizar", "como economizar", "dica economia", "reduzir gastos"]):
            return self._resposta_dica_economia()
        
        elif any(p in pergunta for p in ["categoria mais gasta", "onde gasto mais", "maior categoria"]):
            return self._resposta_categoria_mais_gasta()
        
        elif any(p in pergunta for p in ["ultimos gastos", "últimos gastos", "ultimas compras"]):
            return self._resposta_ultimos_gastos()
        
        elif any(p in pergunta for p in ["resumo", "relatório", "visão geral"]):
            return self._resposta_resumo()
        
        elif any(p in pergunta for p in ["meta", "objetivo", "planejamento"]):
            return self._resposta_meta()
        
        elif any(p in pergunta for p in ["previsão", "vou gastar", "projeção"]):
            return self._resposta_previsao()
        
        elif any(p in pergunta for p in ["alerta", "atenção", "urgente"]):
            return self._resposta_alerta()
        
        else:
            return self._resposta_generica()
    
    def _resposta_limite_gastos(self):
        """Quanto posso gastar hoje?"""
        receita_mensal = self.df[self.df['Valor'] > 0]['Valor'].sum()
        gasto_mensal = abs(self.df[self.df['Valor'] < 0]['Valor'].sum())
        dias_restantes = 30 - datetime.now().day
        
        orcamento_restante = receita_mensal - gasto_mensal
        orcamento_diario = orcamento_restante / dias_restantes if dias_restantes > 0 else 0
        
        if orcamento_diario > 0:
            return f"📊 **Quanto você pode gastar hoje:**\n\n" \
                   f"Com base no seu orçamento, você pode gastar aproximadamente **R$ {orcamento_diario:.2f} hoje**.\n\n" \
                   f"• Receita mensal: R$ {receita_mensal:.2f}\n" \
                   f"• Gasto até agora: R$ {gasto_mensal:.2f}\n" \
                   f"• Dias restantes no mês: {dias_restantes}\n\n" \
                   f"💡 **Dica:** Distribuir seus gastos igualmente pelos dias evita surpresas no fim do mês!"
        else:
            return f"⚠️ **Atenção!** Você já ultrapassou seu orçamento mensal em R$ {abs(orcamento_restante):.2f}.\n\n" \
                   f"• Receita mensal: R$ {receita_mensal:.2f}\n" \
                   f"• Gasto atual: R$ {gasto_mensal:.2f}\n\n" \
                   f"💡 **Recomendação:** Reveja gastos supérfluos e tente economizar onde for possível."
    
    def _resposta_economia(self):
        """Quanto economizei este mês?"""
        receita = self.df[self.df['Valor'] > 0]['Valor'].sum()
        despesa = abs(self.df[self.df['Valor'] < 0]['Valor'].sum())
        economia = receita - despesa
        
        if economia > 0:
            return f"💰 **Sua economia até agora:**\n\n" \
                   f"Você economizou **R$ {economia:.2f}** este mês!\n\n" \
                   f"• Total de entradas: R$ {receita:.2f}\n" \
                   f"• Total de saídas: R$ {despesa:.2f}\n\n" \
                   f"🎉 Parabéns! Continue assim!"
        else:
            return f"⚠️ **Situação financeira:**\n\n" \
                   f"Seus gastos superaram sua renda em **R$ {abs(economia):.2f}**.\n\n" \
                   f"💡 **Sugestão:** Tente reduzir gastos em categorias como lazer e alimentação fora."
    
    def _resposta_analise_aumento(self):
        """Por que minha fatura aumentou?"""
        # Comparar com mês anterior
        hoje = datetime.now()
        mes_atual = hoje.month
        ano_atual = hoje.year
        
        df_mes_atual = self.df[(self.df['Data'].dt.month == mes_atual) & (self.df['Data'].dt.year == ano_atual)]
        
        mes_anterior = mes_atual - 1 if mes_atual > 1 else 12
        ano_anterior = ano_atual if mes_atual > 1 else ano_atual - 1
        
        df_mes_anterior = self.df[(self.df['Data'].dt.month == mes_anterior) & (self.df['Data'].dt.year == ano_anterior)]
        
        gasto_atual = abs(df_mes_atual['Valor'].sum())
        gasto_anterior = abs(df_mes_anterior['Valor'].sum())
        
        if gasto_anterior > 0:
            variacao = ((gasto_atual - gasto_anterior) / gasto_anterior) * 100
        else:
            variacao = 0
        
        if variacao > 10:
            # Descobrir categorias que mais aumentaram
            gastos_cat_atual = df_mes_atual[df_mes_atual['Valor'] < 0].groupby('Categoria')['Valor'].sum().abs()
            gastos_cat_anterior = df_mes_anterior[df_mes_anterior['Valor'] < 0].groupby('Categoria')['Valor'].sum().abs()
            
            aumentos = []
            for cat in gastos_cat_atual.index:
                atual = gastos_cat_atual[cat]
                anterior = gastos_cat_anterior.get(cat, 0)
                if anterior > 0 and atual > anterior:
                    aumentos.append((cat, atual - anterior, (atual/anterior - 1)*100))
            
            aumentos.sort(key=lambda x: x[1], reverse=True)
            
            if aumentos:
                top_aumento = aumentos[0]
                return f"📈 **Análise do aumento da fatura:**\n\n" \
                       f"Sua fatura aumentou **{variacao:.1f}%** em relação ao mês passado.\n\n" \
                       f"• Gasto mês atual: R$ {gasto_atual:.2f}\n" \
                       f"• Gasto mês anterior: R$ {gasto_anterior:.2f}\n\n" \
                       f"🔍 **Principais responsáveis pelo aumento:**\n" \
                       f"→ {top_aumento[0]}: aumento de R$ {top_aumento[1]:.2f} ({top_aumento[2]:.1f}%)\n\n" \
                       f"💡 **Dica:** Revise seus gastos em {top_aumento[0]} para entender o motivo."
        
        return f"📊 **Análise mensal:**\n\n" \
               f"Seu gasto este mês foi de **R$ {gasto_atual:.2f}**.\n\n" \
               f"• Mês anterior: R$ {gasto_anterior:.2f}\n" \
               f"• Variação: {variacao:+.1f}%\n\n" \
               f"💡 {self._get_dica_baseada_variacao(variacao)}"
    
    def _resposta_desperdicio(self):
        """Onde estou desperdiçando dinheiro?"""
        # Identificar gastos supérfluos
        categorias_superfluas = ['Lazer', 'Serviços de Assinatura', 'Delivery', 'Compras impulsivas']
        
        gastos_por_categoria = self.df[self.df['Valor'] < 0].groupby('Categoria')['Valor'].sum().abs()
        
        sugestoes = []
        for categoria, valor in gastos_por_categoria.items():
            if valor > 500:  # Gasto significativo
                sugestoes.append(f"• {categoria}: R$ {valor:.2f} - Tente reduzir em 15% economizando R$ {valor*0.15:.2f}")
        
        if sugestoes:
            return f"🔍 **Identificamos possíveis pontos de desperdício:**\n\n" + "\n".join(sugestoes[:3]) + \
                   f"\n\n💡 **Potencial de economia total:** R$ {sum([float(re.findall(r'R\$ ([\d\.]+)', s)[0].replace('.', '')) for s in sugestoes[:3] if re.findall(r'R\$ ([\d\.]+)', s)]):.2f}"
        else:
            return self._resposta_dica_economia()
    
    def _resposta_dica_economia(self):
        """Como economizar R$X este mês?"""
        gasto_medio_diario = abs(self.df[self.df['Valor'] < 0]['Valor'].mean()) if len(self.df) > 0 else 100
        dias_restantes = 30 - datetime.now().day
        
        # Dicas personalizadas
        dicas = [
            "🍽️ **Alimentação:** Reduza delivery - cada pedido economiza R$30",
            "☕ **Cafezinho:** Levar café de casa pode economizar R$150/mês",
            "🎬 **Streaming:** Assine apenas o que você realmente usa",
            "🚗 **Transporte:** Use transporte público 2x por semana",
            "🛍️ **Compras:** Espere 24h antes de comprar por impulso",
            "💡 **Energia:** Desligue eletrônicos da tomada",
            "📱 **Plano celular:** Revise seu plano atual"
        ]
        
        economia_potencial = 300  # Meta padrão
        
        return f"💡 **Como economizar R$ {economia_potencial:.0f} este mês:**\n\n" + "\n".join(dicas[:3]) + \
               f"\n\n✨ **Desafio:** Tente implementar 2 dicas esta semana!"
    
    def _resposta_categoria_mais_gasta(self):
        """Onde gasto mais?"""
        gastos = self.df[self.df['Valor'] < 0].groupby('Categoria')['Valor'].sum().abs().sort_values(ascending=False)
        
        if not gastos.empty:
            top3 = gastos.head(3)
            total = gastos.sum()
            
            resposta = "🏆 **Top 3 categorias que mais consomem seu dinheiro:**\n\n"
            for i, (cat, valor) in enumerate(top3.items(), 1):
                percentual = (valor / total) * 100
                resposta += f"{i}º **{cat}**: R$ {valor:.2f} ({percentual:.1f}%)\n"
            
            resposta += f"\n📊 Essas 3 categorias representam {(top3.sum()/total)*100:.1f}% dos seus gastos!"
            return resposta
        
        return "Nenhum gasto registrado ainda."
    
    def _resposta_ultimos_gastos(self):
        """Quais foram meus últimos gastos?"""
        ultimos = self.df[self.df['Valor'] < 0].sort_values('Data', ascending=False).head(5)
        
        if not ultimos.empty:
            resposta = "📋 **Seus últimos 5 gastos:**\n\n"
            for _, row in ultimos.iterrows():
                data_str = row['Data'].strftime("%d/%m/%Y")
                resposta += f"• {data_str}: {row['Descrição']} - R$ {abs(row['Valor']):.2f} ({row['Categoria']})\n"
            return resposta
        return "Nenhum gasto registrado ainda."
    
    def _resposta_resumo(self):
        """Resumo financeiro geral"""
        receitas = self.df[self.df['Valor'] > 0]['Valor'].sum()
        despesas = abs(self.df[self.df['Valor'] < 0]['Valor'].sum())
        saldo = receitas - despesas
        
        gastos_por_categoria = self.df[self.df['Valor'] < 0].groupby('Categoria')['Valor'].sum().abs()
        top_categoria = gastos_por_categoria.idxmax() if not gastos_por_categoria.empty else "Nenhum"
        valor_top = gastos_por_categoria.max() if not gastos_por_categoria.empty else 0
        
        return f"📊 **Resumo Financeiro Completo:**\n\n" \
               f"💰 Total de Receitas: R$ {receitas:.2f}\n" \
               f"📤 Total de Despesas: R$ {despesas:.2f}\n" \
               f"💵 Saldo: R$ {saldo:.2f}\n\n" \
               f"🏆 Categoria mais gasta: {top_categoria} (R$ {valor_top:.2f})\n" \
               f"📈 Número de transações: {len(self.df)}\n\n" \
               f"💡 {self._get_motivacao_frase(saldo)}"
    
    def _resposta_meta(self):
        """Dicas de planejamento financeiro"""
        receitas = self.df[self.df['Valor'] > 0]['Valor'].sum()
        meta_economia = receitas * 0.2  # 20% da renda
        
        return f"🎯 **Planejamento Financeiro Inteligente:**\n\n" \
               f"Baseado na sua renda de R$ {receitas:.2f}:\n\n" \
               f"• **Meta ideal de economia:** R$ {meta_economia:.2f} (20% da renda)\n" \
               f"• **Gastos essenciais:** limite de R$ {receitas*0.5:.2f} (50%)\n" \
               f"• **Gastos extras/lazer:** até R$ {receitas*0.3:.2f} (30%)\n\n" \
               f"💡 **Regra 50-30-20:** 50% essencial, 30% lazer, 20% economia/investimento"
    
    def _resposta_previsao(self):
        """Previsão de gastos futuros"""
        gasto_medio_diario = abs(self.df[self.df['Valor'] < 0]['Valor'].mean()) if len(self.df) > 0 else 0
        dias_restantes = 30 - datetime.now().day
        previsao = gasto_medio_diario * dias_restantes
        
        return f"🔮 **Previsão de gastos para o restante do mês:**\n\n" \
               f"• Média de gasto diária: R$ {gasto_medio_diario:.2f}\n" \
               f"• Dias restantes: {dias_restantes}\n" \
               f"• Previsão total: **R$ {previsao:.2f}**\n\n" \
               f"💡 Mantenha seus gastos controlados para bater a meta!"
    
    def _resposta_alerta(self):
        """Alertas importantes"""
        receitas = self.df[self.df['Valor'] > 0]['Valor'].sum()
        despesas = abs(self.df[self.df['Valor'] < 0]['Valor'].sum())
        saldo = receitas - despesas
        
        alertas = []
        
        if saldo < 0:
            alertas.append(f"🚨 **CRÍTICO:** Saldo negativo de R$ {abs(saldo):.2f}")
        
        # Verificar gastos em categorias problemáticas
        gastos_lazer = self.df[(self.df['Valor'] < 0) & (self.df['Categoria'] == 'Lazer')]['Valor'].sum()
        if abs(gastos_lazer) > receitas * 0.3:
            alertas.append(f"🎮 **ATENÇÃO:** Lazer já consumiu {abs(gastos_lazer)/receitas*100:.0f}% da renda")
        
        if alertas:
            return "⚠️ **ALERTAS FINANCEIROS:**\n\n" + "\n\n".join(alertas)
        return "✅ **Sem alertas críticos!** Suas finanças estão saudáveis."
    
    def _resposta_generica(self):
        """Resposta para perguntas não reconhecidas"""
        return "🤖 **Sou seu assistente financeiro!**\n\n" \
               "Posso ajudar com perguntas como:\n\n" \
               "• 💰 'Quanto posso gastar hoje?'\n" \
               "• 📈 'Por que minha fatura aumentou?'\n" \
               "• 🔍 'Onde estou desperdiçando dinheiro?'\n" \
               "• 💡 'Como economizar R$300 este mês?'\n" \
               "• 📊 'Resumo das minhas finanças'\n\n" \
               "O que você gostaria de saber?"
    
    def _get_dica_baseada_variacao(self, variacao):
        if variacao > 20:
            return "Seus gastos aumentaram muito! Reveja compras não essenciais."
        elif variacao < -10:
            return "Parabéns! Seus gastos diminuíram. Continue assim!"
        return "Seus gastos estão estáveis. Continue monitorando!"
    
    def _get_motivacao_frase(self, saldo):
        if saldo > 1000:
            return "Excelente! Você está construindo uma boa reserva financeira!"
        elif saldo > 0:
            return "Bom trabalho! Tente aumentar ainda mais sua economia."
        return "Hora de reavaliar seus gastos e cortar despesas desnecessárias!"


def inicializar_chatbot(df):
    """Inicializa o chatbot com os dados"""
    return FinancialChatbot(df)