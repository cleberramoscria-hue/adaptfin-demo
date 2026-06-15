"""
Engine de Detecção de Anomalias Financeiras
Identifica gastos fora do padrão e comportamentos atípicos
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

class AnomalyEngine:
    """Detecta anomalias em transações financeiras"""
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.is_trained = False
        self.anomaly_threshold = 0.1  # 10% de anomalias esperadas
    
    def train_model(self, df_transacoes):
        """Treina o modelo de detecção de anomalias"""
        gastos = df_transacoes[df_transacoes['Valor'] < 0].copy()
        
        if len(gastos) < 20:
            return False
        
        # Preparar features
        gastos['Valor'] = gastos['Valor'].abs()
        gastos['dia_semana'] = gastos['Data'].dt.dayofweek
        gastos['dia_mes'] = gastos['Data'].dt.day
        gastos['mes'] = gastos['Data'].dt.month
        
        # Features por categoria
        categorias = pd.get_dummies(gastos['Categoria'], prefix='cat')
        
        features = pd.concat([
            gastos[['Valor', 'dia_semana', 'dia_mes', 'mes']],
            categorias
        ], axis=1)
        
        features = features.fillna(0)
        
        # Normalizar
        features_scaled = self.scaler.fit_transform(features)
        
        # Treinar Isolation Forest
        self.model = IsolationForest(
            contamination=self.anomaly_threshold,
            random_state=42,
            n_estimators=100
        )
        self.model.fit(features_scaled)
        self.is_trained = True
        
        return True
    
    def detect_anomalies(self, df_transacoes):
        """Detecta transações anômalas"""
        if not self.is_trained:
            self.train_model(df_transacoes)
        
        if not self.is_trained:
            return pd.DataFrame()
        
        gastos = df_transacoes[df_transacoes['Valor'] < 0].copy()
        
        if gastos.empty:
            return pd.DataFrame()
        
        # Preparar features
        gastos['Valor'] = gastos['Valor'].abs()
        gastos['dia_semana'] = gastos['Data'].dt.dayofweek
        gastos['dia_mes'] = gastos['Data'].dt.day
        gastos['mes'] = gastos['Data'].dt.month
        
        categorias = pd.get_dummies(gastos['Categoria'], prefix='cat')
        
        features = pd.concat([
            gastos[['Valor', 'dia_semana', 'dia_mes', 'mes']],
            categorias
        ], axis=1)
        
        features = features.fillna(0)
        
        # Alinhar colunas com o treino
        for col in features.columns:
            if col not in self.scaler.mean_:
                features[col] = 0
        
        features_scaled = self.scaler.transform(features)
        
        # Prever anomalias (-1 = anomalia, 1 = normal)
        predictions = self.model.predict(features_scaled)
        
        gastos['is_anomaly'] = predictions == -1
        gastos['anomaly_score'] = self.model.score_samples(features_scaled)
        
        return gastos[gastos['is_anomaly'] == True]
    
    def get_anomaly_summary(self, df_transacoes):
        """Resumo das anomalias detectadas"""
        anomalies = self.detect_anomalies(df_transacoes)
        
        if anomalies.empty:
            return {
                'total_anomalies': 0,
                'message': 'Nenhuma anomalia detectada. Seus gastos estão dentro do padrão esperado!',
                'total_value': 0,
                'suggestions': []
            }
        
        total_value = anomalies['Valor'].sum()
        
        # Sugestões baseadas nas anomalias
        suggestions = []
        for _, row in anomalies.iterrows():
            suggestions.append({
                'description': row['Descrição'],
                'value': row['Valor'],
                'category': row['Categoria'],
                'suggestion': f"Gasto de R$ {row['Valor']:.2f} em {row['Categoria']} está acima do normal. Revise se foi necessário."
            })
        
        return {
            'total_anomalies': len(anomalies),
            'message': f"Detectadas {len(anomalies)} transações anômalas, totalizando R$ {total_value:.2f}",
            'total_value': total_value,
            'suggestions': suggestions[:5]  # Top 5
        }