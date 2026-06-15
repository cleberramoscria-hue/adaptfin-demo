"""
Serviço de Análise - Análises estatísticas avançadas
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression

class AnalyticsService:
    """Análises estatísticas e preditivas"""
    
    def __init__(self, df):
        self.df = df
    
    def calculate_trends(self, periodo="mensal"):
        """Calcula tendências de gastos"""
        if self.df.empty:
            return {}
        
        gastos = self.df[self.df['Valor'] < 0].copy()
        gastos['Valor'] = gastos['Valor'].abs()
        
        if periodo == "mensal":
            gastos['periodo'] = gastos['Data'].dt.to_period('M')
            trend_data = gastos.groupby('periodo')['Valor'].sum()
        else:
            gastos['periodo'] = gastos['Data'].dt.to_period('W')
            trend_data = gastos.groupby('periodo')['Valor'].sum()
        
        if len(trend_data) < 2:
            return {'trend': 'stable', 'message': 'Dados insuficientes para tendência'}
        
        # Calcular tendência linear
        x = np.arange(len(trend_data)).reshape(-1, 1)
        y = trend_data.values.reshape(-1, 1)
        
        model = LinearRegression()
        model.fit(x, y)
        
        slope = model.coef_[0][0]
        
        if slope > 50:
            trend = "increasing"
            message = "Seus gastos estão aumentando significativamente"
        elif slope < -50:
            trend = "decreasing"
            message = "Seus gastos estão diminuindo - continue assim!"
        else:
            trend = "stable"
            message = "Seus gastos estão estáveis"
        
        return {
            'trend': trend,
            'message': message,
            'slope': slope,
            'prediction': model.predict([[len(trend_data)]])[0][0]
        }
    
    def analyze_seasonality(self):
        """Analisa sazonalidade dos gastos"""
        if self.df.empty:
            return {}
        
        gastos = self.df[self.df['Valor'] < 0].copy()
        gastos['Valor'] = gastos['Valor'].abs()
        
        # Análise por dia da semana
        gastos['dia_semana'] = gastos['Data'].dt.dayofweek
        dias_semana = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
        gastos_por_dia = gastos.groupby('dia_semana')['Valor'].mean()
        
        # Análise por mês
        gastos['mes'] = gastos['Data'].dt.month
        meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
        gastos_por_mes = gastos.groupby('mes')['Valor'].mean()
        
        # Análise por hora (apenas se tiver hora)
        if 'hora' in gastos.columns:
            gastos_por_hora = gastos.groupby('hora')['Valor'].mean()
        else:
            gastos_por_hora = {}
        
        return {
            'by_weekday': {dias_semana[k]: v for k, v in gastos_por_dia.items()},
            'by_month': {meses[k-1]: v for k, v in gastos_por_mes.items()},
            'by_hour': gastos_por_hora,
            'best_day_to_save': dias_semana[gastos_por_dia.idxmin()] if not gastos_por_dia.empty else "N/A",
            'worst_day_to_spend': dias_semana[gastos_por_dia.idxmax()] if not gastos_por_dia.empty else "N/A",
            'most_expensive_month': meses[gastos_por_mes.idxmax()-1] if not gastos_por_mes.empty else "N/A"
        }
    
    def identify_patterns(self):
        """Identifica padrões de gasto"""
        if self.df.empty:
            return {}
        
        gastos = self.df[self.df['Valor'] < 0].copy()
        gastos['Valor'] = gastos['Valor'].abs()
        
        # Padrões de repetição
        descricoes = gastos['Descrição'].value_counts()
        transacoes_repetidas = descricoes[descricoes > 1].to_dict()
        
        # Padrões de valor
        valores = gastos['Valor']
        
        # Detectar compras por impulso (gastos > 2 desvios padrão)
        impulso_threshold = valores.mean() + 2 * valores.std()
        compras_impulso = gastos[gastos['Valor'] > impulso_threshold]
        
        return {
            'recurring_transactions': transacoes_repetidas,
            'impulse_purchases': len(compras_impulso),
            'impulse_total': compras_impulso['Valor'].sum(),
            'average_ticket': valores.mean(),
            'median_ticket': valores.median(),
            'max_ticket': valores.max(),
            'min_ticket': valores.min()
        }
    
    def calculate_velocity(self):
        """Calcula velocidade de gastos (quanto gasta por dia/semana)"""
        if self.df.empty:
            return {}
        
        gastos = self.df[self.df['Valor'] < 0].copy()
        gastos['Valor'] = gastos['Valor'].abs()
        
        # Velocidade diária
        gastos_diarios = gastos.groupby(gastos['Data'].dt.date)['Valor'].sum()
        
        # Velocidade semanal
        gastos['semana'] = gastos['Data'].dt.isocalendar().week
        gastos_semanais = gastos.groupby('semana')['Valor'].sum()
        
        # Velocidade mensal
        gastos['mes'] = gastos['Data'].dt.to_period('M')
        gastos_mensais = gastos.groupby('mes')['Valor'].sum()
        
        return {
            'daily_avg': gastos_diarios.mean(),
            'daily_max': gastos_diarios.max(),
            'daily_min': gastos_diarios.min(),
            'weekly_avg': gastos_semanais.mean(),
            'monthly_avg': gastos_mensais.mean(),
            'burn_rate': gastos_diarios.mean() * 30,  # Taxa de consumo mensal
            'days_to_zero': (self.df[self.df['Valor'] > 0]['Valor'].sum() / gastos_diarios.mean()) if gastos_diarios.mean() > 0 else 0
        }
    
    def compare_periods(self, period1_start, period1_end, period2_start, period2_end):
        """Compara dois períodos diferentes"""
        mask1 = (self.df['Data'] >= period1_start) & (self.df['Data'] <= period1_end)
        mask2 = (self.df['Data'] >= period2_start) & (self.df['Data'] <= period2_end)
        
        df1 = self.df[mask1]
        df2 = self.df[mask2]
        
        entradas1 = df1[df1['Valor'] > 0]['Valor'].sum()
        entradas2 = df2[df2['Valor'] > 0]['Valor'].sum()
        
        saidas1 = abs(df1[df1['Valor'] < 0]['Valor'].sum())
        saidas2 = abs(df2[df2['Valor'] < 0]['Valor'].sum())
        
        return {
            'period1': {'start': period1_start, 'end': period1_end},
            'period2': {'start': period2_start, 'end': period2_end},
            'entradas': {
                'period1': entradas1,
                'period2': entradas2,
                'variation': ((entradas2 - entradas1) / entradas1 * 100) if entradas1 > 0 else 0
            },
            'saidas': {
                'period1': saidas1,
                'period2': saidas2,
                'variation': ((saidas2 - saidas1) / saidas1 * 100) if saidas1 > 0 else 0
            },
            'saldo': {
                'period1': entradas1 - saidas1,
                'period2': entradas2 - saidas2
            }
        }
    
    def get_financial_health_indicators(self):
        """Indicadores de saúde financeira"""
        if self.df.empty:
            return {}
        
        receitas = self.df[self.df['Valor'] > 0]['Valor'].sum()
        despesas = abs(self.df[self.df['Valor'] < 0]['Valor'].sum())
        saldo = receitas - despesas
        
        # Indicadores
        savings_rate = (saldo / receitas * 100) if receitas > 0 else 0
        
        # Proporção de gastos essenciais vs supérfluos
        gastos_essenciais = abs(self.df[(self.df['Valor'] < 0) & 
                                        (self.df['Categoria'].isin(['Moradia', 'Alimentação', 'Saúde', 'Transporte']))]['Valor'].sum())
        gastos_superfluos = despesas - gastos_essenciais
        
        return {
            'savings_rate': savings_rate,
            'essential_ratio': (gastos_essenciais / despesas * 100) if despesas > 0 else 0,
            'discretionary_ratio': (gastos_superfluos / despesas * 100) if despesas > 0 else 0,
            'status': 'SAUDÁVEL' if savings_rate > 20 else 'ATENÇÃO' if savings_rate > 0 else 'CRÍTICO',
            'recommendation': self._get_recommendation(savings_rate, gastos_superfluos / despesas if despesas > 0 else 0)
        }
    
    def _get_recommendation(self, savings_rate, discretionary_ratio):
        """Recomendação baseada nos indicadores"""
        if savings_rate > 20:
            return "Excelente! Continue investindo sua economia."
        elif savings_rate > 10:
            if discretionary_ratio > 30:
                return "Bom, mas pode reduzir gastos supérfluos para aumentar economia."
            else:
                return "Bom trabalho! Tente aumentar um pouco mais sua economia."
        elif savings_rate > 0:
            return "OK, mas você pode economizar mais. Reveja seus gastos."
        else:
            return "Atenção! Você está gastando mais do que ganha. Corte gastos supérfluos."