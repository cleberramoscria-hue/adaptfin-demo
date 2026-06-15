"""
Scoring Financeiro - Avalia saúde financeira do usuário
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class ScoringEngine:
    """Calcula score de saúde financeira"""
    
    def __init__(self):
        self.score = 0
        self.factors = {}
    
    def calculate_score(self, df_transacoes):
        """Calcula score financeiro (0-1000)"""
        receitas = df_transacoes[df_transacoes['Valor'] > 0]['Valor'].sum()
        despesas = abs(df_transacoes[df_transacoes['Valor'] < 0]['Valor'].sum())
        saldo = receitas - despesas
        
        scores = {
            'savings_rate': self._score_savings_rate(receitas, despesas),
            'expense_stability': self._score_expense_stability(df_transacoes),
            'income_diversity': self._score_income_diversity(df_transacoes),
            'emergency_fund': self._score_emergency_fund(saldo, despesas),
            'debt_ratio': self._score_debt_ratio(df_transacoes),
            'spending_pattern': self._score_spending_pattern(df_transacoes)
        }
        
        self.factors = scores
        
        # Calcular score total (média ponderada)
        pesos = {
            'savings_rate': 0.25,
            'expense_stability': 0.15,
            'income_diversity': 0.15,
            'emergency_fund': 0.20,
            'debt_ratio': 0.15,
            'spending_pattern': 0.10
        }
        
        self.score = sum(scores[k] * pesos[k] for k in pesos)
        
        return self.score
    
    def _score_savings_rate(self, receitas, despesas):
        """Score baseado na taxa de economia"""
        if receitas == 0:
            return 0
        
        savings_rate = (receitas - despesas) / receitas
        
        if savings_rate >= 0.2:
            return 100
        elif savings_rate >= 0.1:
            return 75
        elif savings_rate >= 0:
            return 50
        else:
            return max(0, 25 + (savings_rate * 100))
    
    def _score_expense_stability(self, df_transacoes):
        """Score baseado na estabilidade dos gastos"""
        gastos_mensais = df_transacoes[df_transacoes['Valor'] < 0].groupby(
            df_transacoes['Data'].dt.to_period('M')
        )['Valor'].sum().abs()
        
        if len(gastos_mensais) < 2:
            return 50
        
        coeficiente_variacao = gastos_mensais.std() / gastos_mensais.mean() if gastos_mensais.mean() > 0 else 1
        
        if coeficiente_variacao < 0.1:
            return 100
        elif coeficiente_variacao < 0.2:
            return 75
        elif coeficiente_variacao < 0.3:
            return 50
        else:
            return 25
    
    def _score_income_diversity(self, df_transacoes):
        """Score baseado na diversidade de fontes de renda"""
        receitas = df_transacoes[df_transacoes['Valor'] > 0]
        
        if receitas.empty:
            return 0
        
        num_fontes = receitas['Categoria'].nunique()
        proporcao_principal = receitas['Valor'].max() / receitas['Valor'].sum() if receitas['Valor'].sum() > 0 else 1
        
        score_fontes = min(100, num_fontes * 20)
        score_proporcao = 100 - (proporcao_principal * 100)
        
        return (score_fontes + score_proporcao) / 2
    
    def _score_emergency_fund(self, saldo, despesa_mensal):
        """Score baseado em reserva de emergência"""
        if despesa_mensal == 0:
            return 0
        
        meses_reserva = saldo / despesa_mensal
        
        if meses_reserva >= 6:
            return 100
        elif meses_reserva >= 3:
            return 75
        elif meses_reserva >= 1:
            return 50
        elif meses_reserva >= 0:
            return 25
        else:
            return 0
    
    def _score_debt_ratio(self, df_transacoes):
        """Score baseado em nível de endividamento"""
        # Identificar possíveis dívidas (parcelamentos, financiamentos)
        dividas = df_transacoes[
            (df_transacoes['Descrição'].str.contains('parcela|financiamento|cartão', case=False, na=False)) &
            (df_transacoes['Valor'] < 0)
        ]['Valor'].sum()
        
        receita_mensal = df_transacoes[df_transacoes['Valor'] > 0]['Valor'].mean()
        
        if receita_mensal <= 0:
            return 0
        
        divida_ratio = abs(dividas) / receita_mensal
        
        if divida_ratio == 0:
            return 100
        elif divida_ratio < 0.2:
            return 75
        elif divida_ratio < 0.4:
            return 50
        elif divida_ratio < 0.6:
            return 25
        else:
            return 10
    
    def _score_spending_pattern(self, df_transacoes):
        """Score baseado em padrão de gastos saudável"""
        gastos = df_transacoes[df_transacoes['Valor'] < 0].copy()
        
        if gastos.empty:
            return 50
        
        # Verificar compras por impulso (gastos acima de 2 desvios padrão)
        gastos['Valor'] = gastos['Valor'].abs()
        limite_impulso = gastos['Valor'].mean() + 2 * gastos['Valor'].std()
        compras_impulso = len(gastos[gastos['Valor'] > limite_impulso])
        
        # Verificar gastos em lazer
        gastos_lazer = gastos[gastos['Categoria'] == 'Lazer']['Valor'].sum()
        total_gastos = gastos['Valor'].sum()
        
        score_impulso = max(0, 100 - (compras_impulso * 10))
        
        if total_gastos > 0:
            score_lazer = max(0, 100 - ((gastos_lazer / total_gastos) * 100))
        else:
            score_lazer = 50
        
        return (score_impulso + score_lazer) / 2
    
    def get_score_grade(self, score=None):
        """Retorna a classificação do score"""
        if score is None:
            score = self.score
        
        if score >= 800:
            return "Excelente 🏆", "#2ecc71"
        elif score >= 600:
            return "Bom 👍", "#3498db"
        elif score >= 400:
            return "Regular ⚠️", "#f39c12"
        elif score >= 200:
            return "Atenção 🔴", "#e67e22"
        else:
            return "Crítico 🚨", "#e74c3c"
    
    def get_recommendations(self, score=None):
        """Recomendações baseadas no score"""
        if score is None:
            score = self.score
        
        recommendations = []
        
        if score < 400:
            recommendations.append("🚨 **Prioridade máxima:** Reduza gastos supérfluos urgentemente")
            recommendations.append("📋 Crie um orçamento mensal e siga rigorosamente")
            recommendations.append("🎯 Estabeleça metas pequenas e alcançáveis")
        elif score < 600:
            recommendations.append("📊 Revise suas assinaturas e serviços recorrentes")
            recommendations.append("💰 Tente economizar 10% da sua renda mensal")
            recommendations.append("📱 Use aplicativos de controle financeiro diariamente")
        elif score < 800:
            recommendations.append("🏦 Comece a construir uma reserva de emergência")
            recommendations.append("📈 Considere investir parte da sua economia")
            recommendations.append("🎓 Invista em educação financeira")
        else:
            recommendations.append("🌟 Continue mantendo seus bons hábitos financeiros")
            recommendations.append("📊 Considere diversificar seus investimentos")
            recommendations.append("🤝 Compartilhe suas estratégias com outras pessoas")
        
        return recommendations