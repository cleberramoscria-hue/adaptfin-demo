import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class ForecastEngine:
    """Engine para previsões financeiras e análise de gastos"""
    
    def __init__(self):
        self.prophet_model = None
        self.is_trained = False
    
    def _get_nome_mes(self, mes_num):
        """Retorna nome do mês em português"""
        meses = {
            1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
            5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
            9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
        }
        return meses.get(mes_num, 'Mês inválido')
    
    def analisar_gastos_mes(self, df_transacoes, mes, ano):
        """Analisa gastos de um mês específico (APENAS aquele mês)"""
        if df_transacoes.empty:
            return "❌ Nenhum dado disponível. Importe suas transações primeiro."
        
        df_transacoes = df_transacoes.copy()
        df_transacoes['Data'] = pd.to_datetime(df_transacoes['Data'], errors='coerce').dt.tz_localize(None)
        
        # Filtrar apenas o mês e ano solicitados
        df_mes = df_transacoes[
            (df_transacoes['Data'].dt.month == mes) & 
            (df_transacoes['Data'].dt.year == ano)
        ]
        
        if df_mes.empty:
            return f"⚠️ Não há dados para {self._get_nome_mes(mes)} de {ano}.\n\n💡 Verifique se você importou os dados corretamente ou se o período está correto."
        
        entradas = df_mes[df_mes['Valor'] > 0]['Valor'].sum()
        saidas = abs(df_mes[df_mes['Valor'] < 0]['Valor'].sum())
        saldo = entradas - saidas
        
        gastos_categoria = df_mes[df_mes['Valor'] < 0].groupby('Categoria')['Valor'].sum().abs()
        
        transacoes = df_mes[['Data', 'Descrição', 'Valor', 'Categoria']].copy()
        transacoes['Valor'] = transacoes['Valor'].abs()
        
        resultado = f"""📊 **ANÁLISE DE {self._get_nome_mes(mes).upper()}/{ano}**

💰 **Resumo do Mês:**
• Total de Entradas: R$ {entradas:,.2f}
• Total de Saídas: R$ {saidas:,.2f}
• Saldo do Mês: R$ {saldo:,.2f}
• Taxa de Economia: {(saldo/entradas*100) if entradas > 0 else 0:.1f}%
• Número de transações: {len(df_mes)}

📈 **Gastos por Categoria:**
"""
        for cat, valor in gastos_categoria.nlargest(5).items():
            percentual = (valor / saidas * 100) if saidas > 0 else 0
            resultado += f"• **{cat}**: R$ {valor:,.2f} ({percentual:.1f}%)\n"
        
        # Comparação com mês anterior
        mes_anterior = mes - 1 if mes > 1 else 12
        ano_anterior = ano if mes > 1 else ano - 1
        df_mes_ant = df_transacoes[
            (df_transacoes['Data'].dt.month == mes_anterior) & 
            (df_transacoes['Data'].dt.year == ano_anterior)
        ]
        
        if not df_mes_ant.empty:
            saidas_ant = abs(df_mes_ant[df_mes_ant['Valor'] < 0]['Valor'].sum())
            entradas_ant = df_mes_ant[df_mes_ant['Valor'] > 0]['Valor'].sum()
            variacao_gastos = ((saidas - saidas_ant) / saidas_ant * 100) if saidas_ant > 0 else 0
            variacao_entradas = ((entradas - entradas_ant) / entradas_ant * 100) if entradas_ant > 0 else 0
            
            resultado += f"\n📉 **Comparação com mês anterior ({self._get_nome_mes(mes_anterior)}/{ano_anterior}):**\n"
            if variacao_gastos > 0:
                resultado += f"• ⚠️ Gastos aumentaram {variacao_gastos:.1f}%\n"
            else:
                resultado += f"• ✅ Gastos diminuíram {abs(variacao_gastos):.1f}%\n"
            
            if variacao_entradas > 0:
                resultado += f"• ✅ Entradas aumentaram {variacao_entradas:.1f}%\n"
            else:
                resultado += f"• ⚠️ Entradas diminuíram {abs(variacao_entradas):.1f}%\n"
        
        resultado += f"\n📋 **Principais transações do mês:**\n"
        for _, row in transacoes.nlargest(5, 'Valor').iterrows():
            data_str = row['Data'].strftime('%d/%m/%Y')
            resultado += f"• {data_str}: {row['Descrição']} - R$ {row['Valor']:,.2f} ({row['Categoria']})\n"
        
        resultado += f"\n💡 **Recomendações para {self._get_nome_mes(mes)}/{ano}:**\n"
        if saldo < 0:
            resultado += "⚠️ **ATENÇÃO:** Você gastou mais do que ganhou neste mês!\n• Reveja seus gastos em categorias de maior peso.\n"
        elif saldo < entradas * 0.1 and entradas > 0:
            resultado += "📊 Você economizou menos de 10% da renda. Evite gastos supérfluos.\n"
        else:
            resultado += "✅ **Ótimo trabalho!** Você manteve uma boa taxa de economia.\n"
            
        if not gastos_categoria.empty:
            resultado += f"\n🎯 **Foco de melhoria:** Maior gasto em **{gastos_categoria.idxmax()}** (R$ {gastos_categoria.max():,.2f})."
            
        return resultado

    def prever_saldo_data(self, df_transacoes, data_alvo):
        """Prevê saldo para uma data específica"""
        if df_transacoes.empty:
            return None, "❌ Dados insuficientes para previsão"
        
        df = df_transacoes.copy()
        df['Data'] = pd.to_datetime(df['Data'], errors='coerce').dt.tz_localize(None)
        
        df['Periodo'] = df['Data'].dt.to_period('M')
        gastos_mensais = df[df['Valor'] < 0].groupby('Periodo')['Valor'].sum().abs()
        entradas_mensais = df[df['Valor'] > 0].groupby('Periodo')['Valor'].sum()
        
        if gastos_mensais.empty and entradas_mensais.empty:
            return None, "❌ Dados insuficientes para cálculo de médias"
            
        gasto_medio = gastos_mensais.mean() if not gastos_mensais.empty else 0
        entrada_media = entradas_mensais.mean() if not entradas_mensais.empty else 0
        saldo_atual = df['Valor'].sum()
        
        hoje = datetime.now()
        if data_alvo <= hoje:
            saldo_real = df[df['Data'] <= data_alvo]['Valor'].sum()
            return saldo_real, "✅ Data já passada (valor real em conta)"
        
        meses_restantes = (data_alvo.year - hoje.year) * 12 + (data_alvo.month - hoje.month)
        if meses_restantes <= 0:
            meses_restantes = 1
            
        saldo_projetado = saldo_atual + (entrada_media - gasto_medio) * meses_restantes
        return saldo_projetado, f"Média calculada (Gastos: R$ {gasto_medio:,.2f}/mês | Receitas: R$ {entrada_media:,.2f}/mês)"

    def prever_quando_acabar_dinheiro(self, df_transacoes):
        """Prevê quando o dinheiro vai acabar baseado no ritmo diário"""
        if df_transacoes.empty:
            return None, "❌ Dados insuficientes para análise"
            
        df = df_transacoes.copy()
        df['Data'] = pd.to_datetime(df['Data'], errors='coerce').dt.tz_localize(None)
        
        data_limite = datetime.now() - timedelta(days=30)
        gastos_recentes = df[(df['Valor'] < 0) & (df['Data'] >= data_limite)]
        
        if gastos_recentes.empty:
            gastos_recentes = df[df['Valor'] < 0]
            
        if gastos_recentes.empty:
            return None, "❌ Sem gastos registrados para avaliação."
            
        gasto_medio_diario = abs(gastos_recentes['Valor'].sum() / 30)
        saldo_atual = df['Valor'].sum()
        
        if saldo_atual <= 0:
            return datetime.now(), "⚠️ Você já se encontra com saldo consolidado zerado ou negativo!"
            
        dias_restantes = int(saldo_atual / gasto_medio_diario) if gasto_medio_diario > 0 else 999
        data_fim = datetime.now() + timedelta(days=dias_restantes)
        
        return data_fim, f"📉 Ritmo diário atual apurado em: R$ {gasto_medio_diario:,.2f}/dia"

    def gerar_relatorio_previsao(self, df_transacoes, meses=3):
        """Gera relatório completo evolutivo mês a mês (Histórico + Futuro)"""
        if df_transacoes.empty:
            return "❌ Adicione transações para gerar previsões."
            
        df = df_transacoes.copy()
        df['Data'] = pd.to_datetime(df['Data'], errors='coerce').dt.tz_localize(None)
        df = df.dropna(subset=['Data'])
        df['Periodo'] = df['Data'].dt.to_period('M')
        
        # Agrupamento Histórico Mês a Mês
        gastos_mensais = df[df['Valor'] < 0].groupby('Periodo')['Valor'].sum().abs()
        entradas_mensais = df[df['Valor'] > 0].groupby('Periodo')['Valor'].sum()
        
        periodos_historicos = sorted(df['Periodo'].unique())
        
        relatorio = "📊 **RELATÓRIO FINANCEIRO EVOLUTIVO MÊS A MÊS**\n\n"
        relatorio += "📅 **Histórico Recente Verificado:**\n"
        
        # Exibe os últimos 5 meses reais indexados
        for p in periodos_historicos[-5:]:
            ent = entradas_mensais.get(p, 0.0)
            gai = gastos_mensais.get(p, 0.0)
            sal = ent - gai
            marcado = "🟢" if sal >= 0 else "🔴"
            relatorio += f"• **{p}**: Entradas: R$ {ent:,.2f} | Saídas: R$ {gai:,.2f} | Saldo: {marcado} R$ {sal:,.2f}\n"
            
        gasto_medio = gastos_mensais.mean() if not gastos_mensais.empty else 0
        entrada_media = entradas_mensais.mean() if not entradas_mensais.empty else 0
        saldo_atual = df['Valor'].sum()
        
        relatorio += f"\n💡 **Métricas Médias Identificadas:**\n"
        relatorio += f"• Faturamento Médio: R$ {entrada_media:,.2f}/mês\n"
        relatorio += f"• Custo Médio Consolidado: R$ {gasto_medio:,.2f}/mês\n"
        relatorio += f"• Saldo Atual em Conta: R$ {saldo_atual:,.2f}\n"
        
        relatorio += f"\n🔮 **Prospecção de Cenários (Próximos {meses} meses):**\n"
        
        hoje = datetime.now()
        saldo_acumulado = saldo_atual
        
        for i in range(1, meses + 1):
            # Lógica precisa para avançar meses sem estourar dias do calendário
            ano_alvo = hoje.year + (hoje.month + i - 1) // 12
            mes_alvo = (hoje.month + i - 1) % 12 + 1
            nome_mes = self._get_nome_mes(mes_alvo)
            
            saldo_acumulado += (entrada_media - gasto_medio)
            marcador_prev = "🟢 Positivo" if saldo_acumulado > 0 else "🔴 Deficitário"
            relatorio += f"• **{nome_mes}/{ano_alvo}**: Saldo Previsto: R$ {saldo_acumulado:,.2f} ({marcador_prev})\n"
            
        if gasto_medio > entrada_media:
            deficit = gasto_medio - entrada_media
            relatorio += f"\n⚠️ **ALERTA DE DIRECIONAMENTO:** Sua operação gera um déficit médio de R$ {deficit:,.2f}/mês. Recomenda-se reduzir despesas fixas imediatas."
        else:
            relatorio += f"\n✅ **PANORAMA:** Mantendo a constância atual, sua projeção aponta crescimento sustentável."
            
        return relatorio