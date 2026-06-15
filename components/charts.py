"""
Componente de Gráficos Interativos
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta

class ChartComponent:
    """Componente para exibir gráficos interativos"""
    
    @staticmethod
    def line_chart(df, x_col, y_col, title="", x_label="", y_label="", height=400):
        """Gráfico de linha"""
        fig = px.line(
            df, 
            x=x_col, 
            y=y_col, 
            title=title,
            labels={x_col: x_label, y_col: y_label},
            markers=True
        )
        fig.update_layout(height=height, hovermode='x unified')
        st.plotly_chart(fig, use_container_width=True)
        return fig
    
    @staticmethod
    def bar_chart(df, x_col, y_col, title="", x_label="", y_label="", color=None, height=400):
        """Gráfico de barras"""
        fig = px.bar(
            df, 
            x=x_col, 
            y=y_col, 
            title=title,
            labels={x_col: x_label, y_col: y_label},
            color=color,
            text_auto='.2s'
        )
        fig.update_layout(height=height)
        fig.update_traces(textposition='outside')
        st.plotly_chart(fig, use_container_width=True)
        return fig
    
    @staticmethod
    def pie_chart(df, names_col, values_col, title="", height=400):
        """Gráfico de pizza"""
        fig = px.pie(
            df, 
            names=names_col, 
            values=values_col, 
            title=title,
            hole=0.3
        )
        fig.update_layout(height=height)
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
        return fig
    
    @staticmethod
    def area_chart(df, x_col, y_col, title="", x_label="", y_label="", height=400):
        """Gráfico de área"""
        fig = px.area(
            df, 
            x=x_col, 
            y=y_col, 
            title=title,
            labels={x_col: x_label, y_col: y_label},
            groupnorm='percent'
        )
        fig.update_layout(height=height)
        st.plotly_chart(fig, use_container_width=True)
        return fig
    
    @staticmethod
    def heatmap(df, title="", height=500):
        """Mapa de calor"""
        fig = px.imshow(
            df,
            title=title,
            color_continuous_scale='RdYlGn',
            aspect='auto'
        )
        fig.update_layout(height=height)
        st.plotly_chart(fig, use_container_width=True)
        return fig
    
    @staticmethod
    def gauge_chart(value, title="", min_value=0, max_value=100, height=300):
        """Gráfico de medidor (gauge)"""
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=value,
            title={'text': title},
            gauge={
                'axis': {'range': [min_value, max_value]},
                'bar': {'color': "#2ecc71"},
                'steps': [
                    {'range': [0, 33], 'color': "lightgray"},
                    {'range': [33, 66], 'color': "gray"},
                    {'range': [66, 100], 'color': "darkgray"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 70
                }
            }
        ))
        fig.update_layout(height=height)
        st.plotly_chart(fig, use_container_width=True)
        return fig
    
    @staticmethod
    def comparison_chart(df, x_col, y1_col, y2_col, title="", height=400):
        """Gráfico de comparação (Entradas vs Saídas)"""
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df[x_col], y=df[y1_col], name='Entradas', marker_color='#2ecc71'))
        fig.add_trace(go.Bar(x=df[x_col], y=df[y2_col], name='Saídas', marker_color='#e74c3c'))
        fig.update_layout(
            title=title,
            barmode='group',
            height=height,
            xaxis_title=x_col,
            yaxis_title="Valor (R$)"
        )
        st.plotly_chart(fig, use_container_width=True)
        return fig
    
    @staticmethod
    def trend_chart(df, date_col, value_col, title="", height=400):
        """Gráfico de tendência com média móvel"""
        df['media_7d'] = df[value_col].rolling(window=7, min_periods=1).mean()
        df['media_30d'] = df[value_col].rolling(window=30, min_periods=1).mean()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df[date_col], y=df[value_col], mode='lines', name='Real', line=dict(color='blue', width=1)))
        fig.add_trace(go.Scatter(x=df[date_col], y=df['media_7d'], mode='lines', name='Média 7d', line=dict(color='orange', width=2, dash='dash')))
        fig.add_trace(go.Scatter(x=df[date_col], y=df['media_30d'], mode='lines', name='Média 30d', line=dict(color='green', width=2, dash='dot')))
        
        fig.update_layout(title=title, height=height, hovermode='x unified')
        st.plotly_chart(fig, use_container_width=True)
        return fig