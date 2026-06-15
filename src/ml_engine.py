import pandas as pd
from datetime import datetime

class MLFinanceEngine:
    def __init__(self):
        self.is_trained = False
    
    def detect_anomalies(self, df):
        gastos = df[df['Valor'] < 0].copy()
        gastos['Valor'] = gastos['Valor'].abs()
        if len(gastos) < 10:
            return pd.DataFrame()
        limite = gastos['Valor'].quantile(0.95)
        return gastos[gastos['Valor'] > limite]
    
    def predict_next_month_expenses(self, df):
        gastos = df[df['Valor'] < 0].copy()
        gastos['Valor'] = gastos['Valor'].abs()
        if len(gastos) < 10:
            return {"error": "Dados insuficientes"}
        
        previsoes = {}
        for categoria in gastos['Categoria'].unique():
            valores = gastos[gastos['Categoria'] == categoria]['Valor']
            if len(valores) > 3:
                previsoes[categoria] = valores.mean() * 4  # Projeção mensal
        return {"previsoes_por_categoria": previsoes, "total_previsto": sum(previsoes.values())}
    
    def get_personalized_insights(self, df):
        insights = {"padroes": [], "recomendacoes": [], "alertas": []}
        gastos = df[df['Valor'] < 0].copy()
        gastos['Valor'] = gastos['Valor'].abs()
        
        if 'Data' in gastos.columns and len(gastos) > 7:
            gastos['dia_semana'] = gastos['Data'].dt.dayofweek
            if not gastos.empty:
                dias = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
                dia_maior = gastos.groupby('dia_semana')['Valor'].mean().idxmax()
                insights["padroes"].append(f"📅 Maiores gastos às {dias[dia_maior]}-feira")
        
        receitas = df[df['Valor'] > 0]['Valor'].sum()
        despesas = abs(df[df['Valor'] < 0]['Valor'].sum())
        if receitas > 0:
            economia = despesas * 0.1
            if economia > 50:
                insights["recomendacoes"].append(f"💡 Potencial de economia: R$ {economia:.2f}/mês")
        
        return insights
    
    def suggest_optimal_budget(self, df):
        gastos = df[df['Valor'] < 0].copy()
        gastos['Valor'] = gastos['Valor'].abs()
        if len(gastos) < 10:
            return {"error": "Dados insuficientes"}
        
        orcamento = {}
        for categoria in gastos['Categoria'].unique():
            orcamento[categoria] = gastos[gastos['Categoria'] == categoria]['Valor'].quantile(0.75)
        
        receitas = df[df['Valor'] > 0]['Valor'].sum()
        total = sum(orcamento.values())
        
        if receitas > 0:
            status = "SAUDÁVEL" if total <= receitas * 0.7 else "ATENÇÃO" if total <= receitas * 0.85 else "CRÍTICO"
        else:
            status = "SEM RECEITAS"
        
        return {"orcamento_por_categoria": orcamento, "total_sugerido": total, "status": status}