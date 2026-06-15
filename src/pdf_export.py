"""
Exportação de relatórios em PDF
"""
import pandas as pd
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
import io
import base64

class PDFExporter:
    """Exporta relatórios financeiros para PDF"""
    
    def __init__(self, df):
        self.df = df
        
    def exportar_resumo_mensal(self, ano, mes):
        """Exporta resumo mensal em PDF"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Título
        titulo = Paragraph(f"Relatório Financeiro - {mes}/{ano}", styles['Title'])
        story.append(titulo)
        story.append(Spacer(1, 0.5*cm))
        
        # Filtrar dados do mês
        df_mes = self.df[(self.df['Data'].dt.year == ano) & 
                         (self.df['Data'].dt.month == mes)]
        
        if not df_mes.empty:
            entradas = df_mes[df_mes['Valor'] > 0]['Valor'].sum()
            saidas = abs(df_mes[df_mes['Valor'] < 0]['Valor'].sum())
            saldo = entradas - saidas
            
            # Dados principais
            dados = [
                ['Descrição', 'Valor'],
                ['Total de Entradas', f'R$ {entradas:,.2f}'],
                ['Total de Saídas', f'R$ {saidas:,.2f}'],
                ['Saldo do Mês', f'R$ {saldo:,.2f}']
            ]
            
            tabela = Table(dados)
            tabela.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(tabela)
            
            # Gastos por categoria
            story.append(Spacer(1, 0.5*cm))
            story.append(Paragraph("Gastos por Categoria", styles['Heading2']))
            
            gastos_cat = df_mes[df_mes['Valor'] < 0].groupby('Categoria')['Valor'].sum().abs()
            dados_cat = [['Categoria', 'Valor']]
            for cat, val in gastos_cat.items():
                dados_cat.append([cat, f'R$ {val:,.2f}'])
            
            tabela_cat = Table(dados_cat)
            tabela_cat.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(tabela_cat)
        
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def exportar_relatorio_completo(self):
        """Exporta relatório completo"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=landscape(A4))
        styles = getSampleStyleSheet()
        story = []
        
        # Título
        story.append(Paragraph("Relatório Financeiro Completo", styles['Title']))
        story.append(Spacer(1, 0.5*cm))
        story.append(Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
        story.append(Spacer(1, 0.5*cm))
        
        # Resumo geral
        entradas = self.df[self.df['Valor'] > 0]['Valor'].sum()
        saidas = abs(self.df[self.df['Valor'] < 0]['Valor'].sum())
        
        story.append(Paragraph("Resumo Geral", styles['Heading1']))
        story.append(Paragraph(f"Total de Entradas: R$ {entradas:,.2f}", styles['Normal']))
        story.append(Paragraph(f"Total de Saídas: R$ {saidas:,.2f}", styles['Normal']))
        story.append(Paragraph(f"Saldo: R$ {entradas - saidas:,.2f}", styles['Normal']))
        
        doc.build(story)
        buffer.seek(0)
        return buffer