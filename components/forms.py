"""
Componente de Formulários
"""
import streamlit as st
from datetime import datetime

class FormComponent:
    """Componente para formulários reutilizáveis"""
    
    @staticmethod
    def transaction_form(title, button_text, categories):
        """Formulário genérico de transação"""
        with st.form(f"form_{title.replace(' ', '_')}"):
            st.subheader(title)
            
            col1, col2 = st.columns(2)
            with col1:
                descricao = st.text_input("Descrição", placeholder="Ex: Salário, Compra...")
            with col2:
                valor = st.number_input("Valor (R$)", min_value=0.0, step=50.0, format="%.2f")
            
            col3, col4 = st.columns(2)
            with col3:
                categoria = st.selectbox("Categoria", categories)
            with col4:
                data = st.date_input("Data", value=datetime.now().date())
            
            submitted = st.form_submit_button(button_text, use_container_width=True)
            
            return submitted, descricao, valor, categoria, data
    
    @staticmethod
    def recurring_form():
        """Formulário para contas recorrentes"""
        with st.form("recurring_form"):
            st.subheader("🔄 Configurar Conta Recorrente")
            
            col1, col2 = st.columns(2)
            with col1:
                descricao = st.text_input("Descrição", placeholder="Ex: Netflix, Academia...")
            with col2:
                valor = st.number_input("Valor (R$)", min_value=0.0, step=50.0, format="%.2f")
            
            col3, col4 = st.columns(2)
            with col3:
                categoria = st.selectbox("Categoria", ["Moradia", "Serviços", "Lazer", "Educação", "Saúde"])
            with col4:
                dia_vencimento = st.number_input("Dia do Vencimento", min_value=1, max_value=28, value=10)
            
            num_meses = st.slider("Repetir por quantos meses?", 1, 24, 12)
            
            submitted = st.form_submit_button("✅ Criar Conta Recorrente", use_container_width=True)
            
            return submitted, descricao, valor, categoria, dia_vencimento, num_meses
    
    @staticmethod
    def goal_form():
        """Formulário para metas financeiras"""
        with st.form("goal_form"):
            st.subheader("🎯 Nova Meta Financeira")
            
            col1, col2 = st.columns(2)
            with col1:
                nome = st.text_input("Nome da Meta", placeholder="Ex: Viagem, Casa Nova...")
            with col2:
                valor_alvo = st.number_input("Valor Alvo (R$)", min_value=0.0, step=500.0, format="%.2f")
            
            col3, col4 = st.columns(2)
            with col3:
                prazo = st.date_input("Prazo", value=datetime.now() + st.timedelta(days=365))
            with col4:
                aporte_mensal = st.number_input("Aporte Mensal (R$)", min_value=0.0, step=100.0, format="%.2f")
            
            submitted = st.form_submit_button("✅ Criar Meta", use_container_width=True)
            
            return submitted, nome, valor_alvo, prazo, aporte_mensal
    
    @staticmethod
    def budget_form():
        """Formulário para definir orçamento"""
        with st.form("budget_form"):
            st.subheader("📊 Definir Orçamento Mensal")
            
            col1, col2 = st.columns(2)
            with col1:
                mes = st.selectbox("Mês", list(range(1, 13)), format_func=lambda x: f"{x}/2024")
            with col2:
                orcamento_total = st.number_input("Orçamento Total (R$)", min_value=0.0, step=500.0, format="%.2f")
            
            st.write("**Orçamento por Categoria:**")
            categorias = {
                "Moradia": st.number_input("Moradia", min_value=0.0, step=100.0, format="%.2f"),
                "Alimentação": st.number_input("Alimentação", min_value=0.0, step=100.0, format="%.2f"),
                "Transporte": st.number_input("Transporte", min_value=0.0, step=50.0, format="%.2f"),
                "Lazer": st.number_input("Lazer", min_value=0.0, step=50.0, format="%.2f"),
                "Saúde": st.number_input("Saúde", min_value=0.0, step=50.0, format="%.2f"),
                "Educação": st.number_input("Educação", min_value=0.0, step=50.0, format="%.2f"),
                "Outros": st.number_input("Outros", min_value=0.0, step=50.0, format="%.2f")
            }
            
            submitted = st.form_submit_button("💾 Salvar Orçamento", use_container_width=True)
            
            return submitted, mes, orcamento_total, categorias
    
    @staticmethod
    def filter_form():
        """Formulário de filtros para relatórios"""
        with st.expander("🔍 Filtros Avançados"):
            col1, col2 = st.columns(2)
            with col1:
                data_inicio = st.date_input("Data Inicial", value=datetime.now().replace(day=1))
            with col2:
                data_fim = st.date_input("Data Final", value=datetime.now())
            
            col3, col4 = st.columns(2)
            with col3:
                categorias = st.multiselect("Categorias", 
                    ["Todas", "Moradia", "Alimentação", "Transporte", "Lazer", "Saúde", "Educação", "Renda"])
            with col4:
                valor_min = st.number_input("Valor Mínimo (R$)", min_value=0.0, step=100.0, format="%.2f")
                valor_max = st.number_input("Valor Máximo (R$)", min_value=0.0, step=100.0, format="%.2f", value=10000.0)
            
            aplicar = st.button("📊 Aplicar Filtros", use_container_width=True)
            
            return aplicar, data_inicio, data_fim, categorias, valor_min, valor_max