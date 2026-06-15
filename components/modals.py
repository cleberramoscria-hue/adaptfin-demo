"""
Componente de Modais e Popups
"""
import streamlit as st

class ModalComponent:
    """Componente para exibir modais e diálogos"""
    
    @staticmethod
    def confirm_dialog(title, message, confirm_text="Confirmar", cancel_text="Cancelar"):
        """Diálogo de confirmação"""
        col1, col2 = st.columns(2)
        with col1:
            confirm = st.button(confirm_text, use_container_width=True)
        with col2:
            cancel = st.button(cancel_text, use_container_width=True)
        
        return confirm, cancel
    
    @staticmethod
    def alert_dialog(title, message, type="info"):
        """Alerta modal"""
        icons = {
            "info": "ℹ️",
            "success": "✅",
            "warning": "⚠️",
            "error": "❌"
        }
        
        st.markdown(f"""
        <div style="
            border: 2px solid #ddd;
            border-radius: 10px;
            padding: 20px;
            margin: 10px 0;
            background-color: #f9f9f9;">
            <h3>{icons.get(type, 'ℹ️')} {title}</h3>
            <p>{message}</p>
        </div>
        """, unsafe_allow_html=True)
        
        close = st.button("Fechar", use_container_width=True)
        return close
    
    @staticmethod
    def form_modal(title, form_function):
        """Modal com formulário"""
        with st.expander(f"📝 {title}", expanded=False):
            result = form_function()
            return result
    
    @staticmethod
    def help_modal():
        """Modal de ajuda"""
        with st.expander("🆘 Ajuda e Dicas", expanded=False):
            st.markdown("""
            ### 📚 Como usar o AdaptFin
            
            **Adicionar Receitas:**
            1. Na barra lateral, vá em "💰 Receitas"
            2. Preencha descrição, valor e data
            3. Clique em "Adicionar"
            
            **Adicionar Despesas:**
            1. Use "🏠 Despesas Fixas" para contas mensais
            2. Use "🛍️ Gastos Variáveis" para gastos do dia a dia
            3. Use "🔄 Contas Recorrentes" para assinaturas
            
            **Analisar Dados:**
            1. Dashboard: Visão geral rápida
            2. Relatórios: Análise detalhada
            3. Chat Financeiro: Pergunte em linguagem natural
            
            **Dicas:**
            - Quanto mais dados, melhor a IA
            - Use datas corretas para análise precisa
            - Configure contas recorrentes para economizar tempo
            """)
    
    @staticmethod
    def export_modal(export_callback):
        """Modal de exportação"""
        with st.expander("📤 Exportar Dados", expanded=False):
            st.markdown("### Escolha o formato de exportação")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📄 CSV", use_container_width=True):
                    export_callback("csv")
            with col2:
                if st.button("📊 Excel", use_container_width=True):
                    export_callback("excel")
            
            st.markdown("### Opções de exportação")
            
            periodo = st.selectbox("Período", ["Todos", "Último Mês", "Últimos 3 Meses", "Ano"])
            incluir_graficos = st.checkbox("Incluir gráficos", value=False)
            
            return periodo, incluir_graficos