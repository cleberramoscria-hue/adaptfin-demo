"""
Engine de Análise de Comportamento Financeiro
Identifica padrões de gasto e perfil do usuário
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

class BehaviorEngine:
    """Analisa comportamento financeiro do usuário"""
    
    def __init__(self):
        self.user_profile = None
        self.spending_patterns = {}
        self.seasonal_patterns = {}
    
    def analyze_spending_patterns(self, df_transacoes):
        """Analisa padrões de gasto"""
        gastos = df_transacoes[df_transacoes['Valor'] < 0].copy()
        
        if gastos.empty:
            return {}
        
        gastos['Valor'] = gastos['Valor'].abs()
        if 'Data' in gastos.columns:
            gastos['dia_semana'] = gastos['Data'].dt.dayofweek
            gastos['mes'] = gastos['Data'].dt.month
        else:
            gastos['dia_semana'] = 0
            gastos['mes'] = 1
        
        patterns = {
            'dia_mais_gasta': self._get_day_with_most_spending(gastos),
            'categoria_preferida': self._get_favorite_category(gastos),
            'gasto_medio_diario': gastos.groupby('Data')['Valor'].sum().mean() if 'Data' in gastos.columns else 0,
            'variabilidade': gastos['Valor'].std() / gastos['Valor'].mean() if gastos['Valor'].mean() > 0 else 0,
            'tendencia': self._calculate_trend(gastos)
        }
        
        self.spending_patterns = patterns
        return patterns
    
    def _get_day_with_most_spending(self, gastos):
        """Dia da semana com maior gasto"""
        if 'dia_semana' not in gastos.columns or gastos['dia_semana'].empty:
            return "N/A"
        
        gasto_por_dia = gastos.groupby('dia_semana')['Valor'].sum()
        if not gasto_por_dia.empty:
            dias = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
            idx = gasto_por_dia.idxmax()
            if 0 <= idx <= 6:
                return dias[idx]
        return "N/A"
    
    def _get_favorite_category(self, gastos):
        """Categoria favorita (mais gasta)"""
        if 'Categoria' not in gastos.columns or gastos.empty:
            return "N/A"
        
        gasto_por_cat = gastos.groupby('Categoria')['Valor'].sum()
        if not gasto_por_cat.empty:
            return gasto_por_cat.idxmax()
        return "N/A"
    
    def _calculate_trend(self, gastos):
        """Calcula tendência de gastos (crescente/decrescente)"""
        if len(gastos) < 10:
            return "Estável"
        
        if 'Data' not in gastos.columns:
            return "Estável"
        
        gastos_por_mes = gastos.groupby(gastos['Data'].dt.to_period('M'))['Valor'].sum()
        if len(gastos_por_mes) < 2:
            return "Estável"
        
        # Calcular inclinação da reta de regressão
        x = np.arange(len(gastos_por_mes))
        y = gastos_por_mes.values
        slope = np.polyfit(x, y, 1)[0]
        
        if slope > 100:
            return "Crescente ⬆️"
        elif slope < -100:
            return "Decrescente ⬇️"
        else:
            return "Estável ➡️"
    
    def determine_user_profile(self, df_transacoes):
        """Determina o perfil financeiro do usuário"""
        gastos = df_transacoes[df_transacoes['Valor'] < 0].copy()
        receitas = df_transacoes[df_transacoes['Valor'] > 0].copy()
        
        if gastos.empty:
            return "Novato"
        
        gasto_medio = gastos['Valor'].abs().mean()
        num_transacoes = len(gastos)
        categorias = gastos['Categoria'].nunique() if 'Categoria' in gastos.columns else 1
        
        # Calcular scores
        total_receitas = receitas['Valor'].sum() if not receitas.empty else 0
        total_gastos = abs(gastos['Valor'].sum())
        
        economia_score = (total_receitas - total_gastos) / total_receitas if total_receitas > 0 else 0
        frequencia_score = num_transacoes / 30  # Transações por dia
        diversidade_score = categorias / 10  # Diversidade de categorias
        
        if economia_score > 0.2 and frequencia_score < 2:
            profile_name = "Econômico"
            profile_desc = "Você controla bem seus gastos e economiza regularmente"
        elif economia_score < 0 and frequencia_score > 3:
            profile_name = "Gastador"
            profile_desc = "Seus gastos estão acima da renda, atenção!"
        elif diversidade_score > 0.7:
            profile_name = "Diversificado"
            profile_desc = "Seus gastos estão bem distribuídos entre categorias"
        elif frequencia_score < 1:
            profile_name = "Ocasional"
            profile_desc = "Você faz poucas transações, mas de valores significativos"
        else:
            profile_name = "Equilibrado"
            profile_desc = "Seus hábitos de consumo são balanceados"
        
        self.user_profile = {
            'profile': f"🎯 {profile_name} - {profile_desc}",
            'profile_name': profile_name,
            'profile_desc': profile_desc,
            'economy_score': economia_score,
            'frequency_score': frequencia_score,
            'diversity_score': diversidade_score,
            'avg_spending': gasto_medio,
            'total_transactions': num_transacoes
        }
        
        return self.user_profile
    
    def get_behavior_insights(self, df_transacoes):
        """Gera insights comportamentais"""
        patterns = self.analyze_spending_patterns(df_transacoes)
        profile = self.determine_user_profile(df_transacoes)
        
        insights = []
        
        # Verificar se profile é dicionário
        if isinstance(profile, dict):
            if profile.get('economy_score', 0) < 0:
                insights.append(f"🚨 Você está gastando mais do que ganha! Revise suas despesas.")
            elif profile.get('economy_score', 0) > 0.2:
                insights.append(f"💰 Parabéns! Você está economizando {profile['economy_score']*100:.0f}% da sua renda")
            
            if profile.get('profile_name'):
                insights.append(f"📊 Perfil identificado: {profile['profile_name']}")
        
        if patterns.get('dia_mais_gasta') and patterns['dia_mais_gasta'] != "N/A":
            insights.append(f"📅 Seus maiores gastos ocorrem às {patterns['dia_mais_gasta']}-feira")
        
        if patterns.get('categoria_preferida') and patterns['categoria_preferida'] != "N/A":
            insights.append(f"🏷️ Sua categoria com maior gasto é: {patterns['categoria_preferida']}")
        
        if patterns.get('tendencia') and patterns['tendencia'] != "Estável":
            insights.append(f"📈 Tendência de gastos: {patterns['tendencia']}")
        
        if patterns.get('variabilidade', 0) > 1:
            insights.append(f"⚠️ Seus gastos têm alta variabilidade - considere um planejamento mais consistente")
        
        if not insights:
            insights.append("📊 Adicione mais transações para obter insights personalizados")
        
        return insights