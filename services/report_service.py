"""
Serviço de Relatórios - Geração de relatórios financeiros
"""
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import os

class ReportService:
    """Gera relatórios financeiros"""
    
    def __init__(self, output_dir="reports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_monthly_report(self, df, ano, mes):
        """Gera relatório mensal"""
        df_mes = df[(df['Data'].dt.year == ano) & (df['Data'].dt.month == mes)]
        
        if df_mes.empty:
            return None
        
        entradas = df_mes[df_mes['Valor'] > 0]['Valor'].sum()
        saidas = abs(df_mes[df_mes['Valor'] < 0]['Valor'].sum())
        saldo = entradas - saidas
        
        gastos_categoria = df_mes[df_mes['Valor'] < 0].groupby('Categoria')['Valor'].sum().abs()
        
        return {
            'ano': ano,
            'mes': mes,
            'entradas': entradas,
            'saidas': saidas,
            'saldo': saldo,
            'gastos_por_categoria': gastos_categoria.to_dict(),
            'total_transacoes': len(df_mes),
            'media_diaria': abs(df_mes[df_mes['Valor'] < 0]['Valor'].mean()) if len(df_mes) > 0 else 0
        }
    
    def generate_yearly_report(self, df, ano):
        """Gera relatório anual"""
        df_ano = df[df['Data'].dt.year == ano]
        
        meses_nomes = {1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr", 5: "Mai", 6: "Jun",
                       7: "Jul", 8: "Ago", 9: "Set", 10: "Out", 11: "Nov", 12: "Dez"}
        
        dados_mensais = []
        for mes in range(1, 13):
            df_mes = df_ano[df_ano['Data'].dt.month == mes]
            entradas = df_mes[df_mes['Valor'] > 0]['Valor'].sum()
            saidas = abs(df_mes[df_mes['Valor'] < 0]['Valor'].sum())
            
            dados_mensais.append({
                'mes': meses_nomes[mes],
                'entradas': entradas,
                'saidas': saidas,
                'saldo': entradas - saidas
            })
        
        total_entradas = df_ano[df_ano['Valor'] > 0]['Valor'].sum()
        total_saidas = abs(df_ano[df_ano['Valor'] < 0]['Valor'].sum())
        
        return {
            'ano': ano,
            'dados_mensais': dados_mensais,
            'total_entradas': total_entradas,
            'total_saidas': total_saidas,
            'saldo_anual': total_entradas - total_saidas,
            'melhor_mes': max(dados_mensais, key=lambda x: x['saldo']) if dados_mensais else None,
            'pior_mes': min(dados_mensais, key=lambda x: x['saldo']) if dados_mensais else None
        }
    
    def generate_category_report(self, df, categoria):
        """Gera relatório por categoria"""
        df_cat = df[df['Categoria'] == categoria]
        
        if df_cat.empty:
            return None
        
        gastos = df_cat[df_cat['Valor'] < 0].copy()
        gastos['Valor'] = gastos['Valor'].abs()
        
        return {
            'categoria': categoria,
            'total_gasto': gastos['Valor'].sum(),
            'media_por_transacao': gastos['Valor'].mean(),
            'total_transacoes': len(gastos),
            'maior_gasto': gastos['Valor'].max(),
            'menor_gasto': gastos['Valor'].min(),
            'detalhes_por_mes': gastos.groupby(gastos['Data'].dt.to_period('M'))['Valor'].sum().to_dict()
        }
    
    def generate_comparison_report(self, df, periodo1, periodo2):
        """Gera relatório comparativo entre períodos"""
        # período1 e período2 são tuplas (ano, mes) ou (ano)
        if len(periodo1) == 2:  # Mensal
            df_p1 = df[(df['Data'].dt.year == periodo1[0]) & (df['Data'].dt.month == periodo1[1])]
            df_p2 = df[(df['Data'].dt.year == periodo2[0]) & (df['Data'].dt.month == periodo2[1])]
        else:  # Anual
            df_p1 = df[df['Data'].dt.year == periodo1[0]]
            df_p2 = df[df['Data'].dt.year == periodo2[0]]
        
        entradas_p1 = df_p1[df_p1['Valor'] > 0]['Valor'].sum()
        entradas_p2 = df_p2[df_p2['Valor'] > 0]['Valor'].sum()
        
        saidas_p1 = abs(df_p1[df_p1['Valor'] < 0]['Valor'].sum())
        saidas_p2 = abs(df_p2[df_p2['Valor'] < 0]['Valor'].sum())
        
        return {
            'periodo1': periodo1,
            'periodo2': periodo2,
            'entradas_p1': entradas_p1,
            'entradas_p2': entradas_p2,
            'saidas_p1': saidas_p1,
            'saidas_p2': saidas_p2,
            'variacao_entradas': ((entradas_p2 - entradas_p1) / entradas_p1 * 100) if entradas_p1 > 0 else 0,
            'variacao_saidas': ((saidas_p2 - saidas_p1) / saidas_p1 * 100) if saidas_p1 > 0 else 0
        }
    
    def create_report_chart(self, report_data, chart_type="bar"):
        """Cria gráfico do relatório"""
        if chart_type == "bar":
            fig = go.Figure()
            fig.add_trace(go.Bar(x=['Entradas', 'Saídas'], 
                                 y=[report_data['entradas'], report_data['saidas']],
                                 marker_color=['#2ecc71', '#e74c3c']))
            fig.update_layout(title=f"Resumo - {report_data.get('mes', '')}/{report_data.get('ano', '')}",
                              yaxis_title="Valor (R$)")
            return fig
        elif chart_type == "pie":
            gastos = report_data.get('gastos_por_categoria', {})
            fig = px.pie(values=list(gastos.values()), names=list(gastos.keys()), 
                         title="Gastos por Categoria")
            return fig
        return None