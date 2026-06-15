"""
Componente de Cards e Métricas
"""
import streamlit as st

class CardComponent:
    """Componente para exibir cards e métricas"""
    
    @staticmethod
    def metric_card(title, value, delta=None, delta_color="normal", icon="📊"):
        """Card de métrica única"""
        with st.container():
            st.markdown(f"""
            <div style="
                background-color: #f0f2f6;
                padding: 15px;
                border-radius: 10px;
                text-align: center;
                margin: 5px;">
                <span style="font-size: 2rem;">{icon}</span>
                <h3 style="margin: 5px 0;">{title}</h3>
                <p style="font-size: 1.5rem; font-weight: bold; margin: 0;">{value}</p>
            </div>
            """, unsafe_allow_html=True)
    
    @staticmethod
    def info_card(title, value, color="#2ecc71", icon="💰"):
        """Card informativo colorido"""
        st.markdown(f"""
        <div style="
            background-color: {color};
            padding: 20px;
            border-radius: 10px;
            color: white;
            text-align: center;
            margin: 10px 0;">
            <span style="font-size: 2rem;">{icon}</span>
            <h3 style="margin: 10px 0;">{title}</h3>
            <p style="font-size: 1.8rem; font-weight: bold; margin: 0;">{value}</p>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def progress_card(title, current, target, icon="🎯"):
        """Card com barra de progresso"""
        percent = min(100, (current / target) * 100) if target > 0 else 0
        st.markdown(f"""
        <div style="
            background-color: #f0f2f6;
            padding: 15px;
            border-radius: 10px;
            margin: 10px 0;">
            <span style="font-size: 1.5rem;">{icon}</span>
            <strong>{title}</strong>
            <div style="background-color: #ddd; border-radius: 5px; margin: 10px 0;">
                <div style="width: {percent}%; background-color: #2ecc71; padding: 5px; border-radius: 5px; text-align: center; color: white;">
                    {percent:.1f}%
                </div>
            </div>
            <p>Progresso: R$ {current:,.2f} de R$ {target:,.2f}</p>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def comparison_card(title, value1, label1, value2, label2, icon="📊"):
        """Card de comparação entre dois valores"""
        st.markdown(f"""
        <div style="
            background-color: #f0f2f6;
            padding: 15px;
            border-radius: 10px;
            margin: 10px 0;">
            <span style="font-size: 1.5rem;">{icon}</span>
            <strong>{title}</strong>
            <div style="display: flex; justify-content: space-between; margin-top: 10px;">
                <div style="text-align: center; flex: 1;">
                    <p style="font-size: 1.2rem; font-weight: bold; margin: 0;">{value1}</p>
                    <p style="margin: 0;">{label1}</p>
                </div>
                <div style="text-align: center; flex: 1;">
                    <p style="font-size: 1.2rem; font-weight: bold; margin: 0;">{value2}</p>
                    <p style="margin: 0;">{label2}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def insight_card(insight_text, type="info"):
        """Card para insights e dicas"""
        colors = {
            "info": "#3498db",
            "success": "#2ecc71",
            "warning": "#f39c12",
            "danger": "#e74c3c"
        }
        icons = {
            "info": "💡",
            "success": "✅",
            "warning": "⚠️",
            "danger": "🚨"
        }
        
        st.markdown(f"""
        <div style="
            background-color: {colors.get(type, '#3498db')};
            padding: 15px;
            border-radius: 10px;
            color: white;
            margin: 10px 0;">
            <span style="font-size: 1.2rem;">{icons.get(type, '💡')}</span>
            <span style="margin-left: 10px;">{insight_text}</span>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def expense_card(category, amount, percentage, color="#e74c3c"):
        """Card de gasto por categoria"""
        st.markdown(f"""
        <div style="
            background-color: white;
            border-left: 5px solid {color};
            padding: 10px;
            border-radius: 5px;
            margin: 5px 0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
            <strong>{category}</strong>
            <div style="float: right;">{amount}</div>
            <div style="color: #666; font-size: 0.8rem;">{percentage}% dos gastos</div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def date_card(date, description, amount, color="#3498db"):
        """Card para transações individuais"""
        st.markdown(f"""
        <div style="
            background-color: white;
            padding: 10px;
            border-radius: 5px;
            margin: 5px 0;
            border-left: 3px solid {color};
            display: flex;
            justify-content: space-between;">
            <div>
                <strong>{description}</strong>
                <div style="color: #666; font-size: 0.8rem;">{date}</div>
            </div>
            <div style="font-weight: bold; color: {color};">{amount}</div>
        </div>
        """, unsafe_allow_html=True)