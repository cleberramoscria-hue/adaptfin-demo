"""
Componente de Tabelas e DataFrames
"""
import streamlit as st
import pandas as pd
from datetime import datetime

class TableComponent:
    """Componente para exibir tabelas interativas"""
    
    @staticmethod
    def transaction_table(df, title="Transações"):
        """Tabela de transações formatada"""
        st.subheader(title)
        
        if df.empty:
            st.info("Nenhuma transação encontrada")
            return
        
        # Cópia para exibição
        df_display = df.copy()
        
        # Formatar colunas
        if 'Valor' in df_display.columns:
            df_display['Valor'] = df_display['Valor'].apply(lambda x: f"R$ {x:,.2f}")
        
        if 'Data' in df_display.columns:
            df_display['Data'] = pd.to_datetime(df_display['Data']).dt.strftime('%d/%m/%Y')
        
        # Ordenar por data
        if 'Data' in df_display.columns:
            df_display = df_display.sort_values('Data', ascending=False)
        
        st.dataframe(df_display, use_container_width=True, height=400)
        
        return df_display
    
    @staticmethod
    def monthly_summary(df_mensal):
        """Tabela de resumo mensal"""
        st.subheader("📅 Resumo Mensal")
        
        if df_mensal.empty:
            st.info("Nenhum dado mensal disponível")
            return
        
        # Formatar valores
        df_formatado = df_mensal.copy()
        for col in ['Entradas', 'Saídas', 'Saldo']:
            if col in df_formatado.columns:
                df_formatado[col] = df_formatado[col].apply(lambda x: f"R$ {x:,.2f}")
        
        if 'Economia %' in df_formatado.columns:
            df_formatado['Economia %'] = df_formatado['Economia %'].apply(lambda x: f"{x:.1f}%")
        
        st.dataframe(df_formatado, use_container_width=True, hide_index=True)
    
    @staticmethod
    def category_table(gastos_categoria):
        """Tabela de gastos por categoria"""
        st.subheader("🏷️ Gastos por Categoria")
        
        if gastos_categoria.empty:
            st.info("Nenhum gasto registrado")
            return
        
        df_cat = pd.DataFrame({
            'Categoria': gastos_categoria.index,
            'Valor': gastos_categoria.values
        })
        df_cat = df_cat.sort_values('Valor', ascending=False)
        df_cat['Valor'] = df_cat['Valor'].apply(lambda x: f"R$ {x:,.2f}")
        
        # Adicionar percentual
        total = gastos_categoria.sum()
        df_cat['Percentual'] = (gastos_categoria.values / total * 100).round(1).astype(str) + '%'
        
        st.dataframe(df_cat, use_container_width=True, hide_index=True)
        
        return df_cat
    
    @staticmethod
    def recurring_table(df_recorrentes):
        """Tabela de contas recorrentes"""
        st.subheader("🔄 Contas Recorrentes")
        
        if df_recorrentes.empty:
            st.info("Nenhuma conta recorrente cadastrada")
            return
        
        df_display = df_recorrentes.copy()
        df_display['Valor'] = df_display['Valor'].abs().apply(lambda x: f"R$ {x:,.2f}")
        
        st.dataframe(df_display, use_container_width=True, hide_index=True)
    
    @staticmethod
    def comparison_table(ano1_data, ano2_data, labels):
        """Tabela comparativa entre períodos"""
        df_comp = pd.DataFrame({
            labels[0]: ano1_data,
            labels[1]: ano2_data,
            'Variação': ((ano2_data - ano1_data) / ano1_data * 100) if (ano1_data != 0).all() else 0
        })
        
        df_comp['Variação'] = df_comp['Variação'].apply(lambda x: f"{x:+.1f}%")
        
        st.dataframe(df_comp, use_container_width=True)
    
    @staticmethod
    def budget_vs_actual_table(budget, actual, categories):
        """Tabela de orçamento vs realizado"""
        df_ba = pd.DataFrame({
            'Categoria': categories,
            'Orçamento': budget,
            'Realizado': actual,
            'Diferença': budget - actual,
            'Status': ['✅' if b >= a else '⚠️' for b, a in zip(budget, actual)]
        })
        
        df_ba['Orçamento'] = df_ba['Orçamento'].apply(lambda x: f"R$ {x:,.2f}")
        df_ba['Realizado'] = df_ba['Realizado'].apply(lambda x: f"R$ {x:,.2f}")
        df_ba['Diferença'] = df_ba['Diferença'].apply(lambda x: f"R$ {x:,.2f}")
        
        st.dataframe(df_ba, use_container_width=True, hide_index=True)