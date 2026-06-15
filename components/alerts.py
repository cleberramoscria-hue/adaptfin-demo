"""
Componente de Alertas e Notificações
"""
import streamlit as st
from datetime import datetime, timedelta

class AlertComponent:
    """Componente para exibir alertas e notificações"""
    
    @staticmethod
    def success_alert(message, duration=3):
        """Alerta de sucesso"""
        st.success(f"✅ {message}")
    
    @staticmethod
    def error_alert(message, duration=5):
        """Alerta de erro"""
        st.error(f"❌ {message}")
    
    @staticmethod
    def warning_alert(message, duration=4):
        """Alerta de aviso"""
        st.warning(f"⚠️ {message}")
    
    @staticmethod
    def info_alert(message, duration=3):
        """Alerta informativo"""
        st.info(f"ℹ️ {message}")
    
    @staticmethod
    def budget_alert(gasto_atual, limite, categoria=""):
        """Alerta de orçamento"""
        percentual = (gasto_atual / limite) * 100 if limite > 0 else 0
        
        if percentual >= 100:
            st.error(f"🚨 **ALERTA CRÍTICO!** {categoria} ultrapassou o orçamento em R$ {gasto_atual - limite:.2f}")
        elif percentual >= 80:
            st.warning(f"⚠️ **ATENÇÃO!** {categoria} já consumiu {percentual:.0f}% do orçamento")
        elif percentual >= 50:
            st.info(f"ℹ️ {categoria} já consumiu {percentual:.0f}% do orçamento")
    
    @staticmethod
    def due_date_alert(contas_proximas):
        """Alerta de contas a vencer"""
        if not contas_proximas:
            return
        
        st.info(f"📅 **Lembrete:** {len(contas_proximas)} conta(s) a vencer nos próximos 5 dias")
        for _, conta in contas_proximas.head(3).iterrows():
            st.caption(f"• {conta['Descrição']} - Vence em {conta['Data'].strftime('%d/%m/%Y')}")
    
    @staticmethod
    def anomaly_alert(anomalias):
        """Alerta de gastos anômalos"""
        if not anomalias:
            return
        
        st.warning(f"🚨 **Alerta de Gastos Anômalos:** {len(anomalias)} gastos fora do padrão detectados")
        for _, gasto in anomalias.head(3).iterrows():
            st.caption(f"• {gasto['Descrição']}: R$ {abs(gasto['Valor']):.2f} - {gasto['Categoria']}")
    
    @staticmethod
    def goal_alert(metas):
        """Alerta de metas"""
        for meta in metas:
            percentual = (meta['economizado'] / meta['valor']) * 100 if meta['valor'] > 0 else 0
            
            if percentual >= 100:
                st.success(f"🎉 **PARABÉNS!** Meta '{meta['nome']}' alcançada!")
            elif percentual >= 75:
                st.info(f"📈 Meta '{meta['nome']}' está em {percentual:.0f}% - Quase lá!")
    
    @staticmethod
    def daily_tip():
        """Dica diária aleatória"""
        import random
        dicas = [
            "💡 Cozinhar em casa 3x por semana pode economizar R$200/mês",
            "💡 Levar café de casa economiza até R$150/mês",
            "💡 Reveja assinaturas de streaming - você usa todas?",
            "💡 Use transporte público 2x por semana e economize combustível",
            "💡 Espere 24h antes de comprar por impulso",
            "💡 Desligue eletrônicos da tomada para economizar energia",
            "💡 Revise seu plano de celular - talvez tenha opções mais baratas"
        ]
        
        st.info(random.choice(dicas))
    
    @staticmethod
    def health_score_alert(score, grade):
        """Alerta de score financeiro"""
        if score >= 800:
            st.success(f"🏆 Seu score financeiro é **{score:.0f}** ({grade}) - Excelente!")
        elif score >= 600:
            st.info(f"👍 Seu score financeiro é **{score:.0f}** ({grade}) - Bom")
        elif score >= 400:
            st.warning(f"⚠️ Seu score financeiro é **{score:.0f}** ({grade}) - Pode melhorar")
        else:
            st.error(f"🚨 Seu score financeiro é **{score:.0f}** ({grade}) - Atenção necessária!")