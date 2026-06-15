"""
Preditor de Gastos - Previsão de despesas futuras
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

class PredictorEngine:
    """Previsão de gastos futuros usando ML"""
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.is_trained = False
    
    def prepare_features(self, df_transacoes):
        """Prepara features para treinamento"""
        gastos = df_transacoes[df_transacoes['Valor'] < 0].copy()
        
        if len(gastos) < 30:
            return None, None
        
        gastos['Valor'] = gastos['Valor'].abs()
        gastos['dia_semana'] = gastos['Data'].dt.dayofweek
        gastos['dia_mes'] = gastos['Data'].dt.day
        gastos['mes'] = gastos['Data'].dt.month
        gastos['semana'] = gastos['Data'].dt.isocalendar().week
        
        # Features rolling
        gastos = gastos.sort_values('Data')
        gastos['gasto_medio_7d'] = gastos['Valor'].rolling(window=7, min_periods=1).mean()
        gastos['gasto_medio_30d'] = gastos['Valor'].rolling(window=30, min_periods=1).mean()
        gastos['tendencia'] = gastos['Valor'].rolling(window=7, min_periods=1).apply(lambda x: x.iloc[-1] - x.iloc[0] if len(x) > 1 else 0)
        
        # One-hot encoding para categorias
        categorias = pd.get_dummies(gastos['Categoria'], prefix='cat')
        
        features = pd.concat([
            gastos[['Valor', 'dia_semana', 'dia_mes', 'mes', 'semana', 'gasto_medio_7d', 'gasto_medio_30d', 'tendencia']],
            categorias
        ], axis=1)
        
        features = features.fillna(0)
        
        # Target: próximo gasto
        features['target'] = features['Valor'].shift(-1)
        features = features.dropna()
        
        X = features.drop('target', axis=1)
        y = features['target']
        
        return X, y
    
    def train(self, df_transacoes):
        """Treina o modelo preditor"""
        X, y = self.prepare_features(df_transacoes)
        
        if X is None or len(X) < 20:
            return False
        
        # Normalizar
        X_scaled = self.scaler.fit_transform(X)
        
        # Treinar Random Forest
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        self.model.fit(X_scaled, y)
        self.is_trained = True
        
        return True
    
    def predict_next_week(self, df_transacoes):
        """Prevê gastos para a próxima semana"""
        if not self.is_trained:
            self.train(df_transacoes)
        
        if not self.is_trained:
            return 0, []
        
        # Últimos dados para previsão
        gastos_recentes = df_transacoes[df_transacoes['Valor'] < 0].tail(30).copy()
        
        if len(gastos_recentes) < 7:
            return 0, []
        
        gastos_recentes['Valor'] = gastos_recentes['Valor'].abs()
        gastos_recentes['dia_semana'] = gastos_recentes['Data'].dt.dayofweek
        gastos_recentes['dia_mes'] = gastos_recentes['Data'].dt.day
        gastos_recentes['mes'] = gastos_recentes['Data'].dt.month
        gastos_recentes['semana'] = gastos_recentes['Data'].dt.isocalendar().week
        
        gastos_recentes['gasto_medio_7d'] = gastos_recentes['Valor'].rolling(window=7, min_periods=1).mean()
        gastos_recentes['gasto_medio_30d'] = gastos_recentes['Valor'].rolling(window=30, min_periods=1).mean()
        gastos_recentes['tendencia'] = gastos_recentes['Valor'].rolling(window=7, min_periods=1).apply(lambda x: x.iloc[-1] - x.iloc[0] if len(x) > 1 else 0)
        
        # Prever para os próximos 7 dias
        predictions = []
        ultimo_gasto = gastos_recentes.iloc[-1:].copy()
        
        for _ in range(7):
            # Preparar features
            categorias = pd.get_dummies(ultimo_gasto['Categoria'], prefix='cat')
            features = pd.concat([
                ultimo_gasto[['Valor', 'dia_semana', 'dia_mes', 'mes', 'semana', 'gasto_medio_7d', 'gasto_medio_30d', 'tendencia']],
                categorias
            ], axis=1)
            features = features.fillna(0)
            
            # Alinhar colunas
            for col in self.model.feature_names_in_:
                if col not in features.columns:
                    features[col] = 0
            
            features = features[self.model.feature_names_in_]
            features_scaled = self.scaler.transform(features)
            
            pred = self.model.predict(features_scaled)[0]
            predictions.append(max(0, pred))
            
            # Atualizar para próximo passo
            ultimo_gasto['Valor'] = pred
            ultimo_gasto['dia_semana'] = (ultimo_gasto['dia_semana'].values[0] + 1) % 7
        
        total_previsto = sum(predictions)
        
        return total_previsto, predictions
    
    def predict_monthly(self, df_transacoes):
        """Prevê gasto total do mês"""
        gasto_medio_diario = abs(df_transacoes[df_transacoes['Valor'] < 0]['Valor'].mean())
        dias_restantes = 30 - datetime.now().day
        
        previsao_simples = gasto_medio_diario * dias_restantes
        
        #