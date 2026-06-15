"""
Serviço de Exportação - CSV, Excel, PDF, JSON
"""
import pandas as pd
import json
import os
from datetime import datetime
import io
import base64

class ExportService:
    """Serviço para exportar dados em diferentes formatos"""
    
    def __init__(self, output_dir="exports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def to_csv(self, df, filename=None):
        """Exporta para CSV"""
        if filename is None:
            filename = f"adaptfin_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        filepath = os.path.join(self.output_dir, filename)
        df.to_csv(filepath, index=False, encoding='utf-8-sig')
        
        return filepath
    
    def to_excel(self, df, filename=None, sheets=None):
        """Exporta para Excel com múltiplas abas"""
        if filename is None:
            filename = f"adaptfin_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        filepath = os.path.join(self.output_dir, filename)
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            if sheets:
                for sheet_name, sheet_df in sheets.items():
                    sheet_df.to_excel(writer, sheet_name=sheet_name, index=False)
            else:
                df.to_excel(writer, sheet_name='Dados', index=False)
        
        return filepath
    
    def to_json(self, df, filename=None):
        """Exporta para JSON"""
        if filename is None:
            filename = f"adaptfin_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        filepath = os.path.join(self.output_dir, filename)
        
        data = df.to_dict(orient='records')
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        
        return filepath
    
    def to_html(self, df, filename=None):
        """Exporta para HTML"""
        if filename is None:
            filename = f"adaptfin_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        
        filepath = os.path.join(self.output_dir, filename)
        
        html = df.to_html(classes='table table-striped', border=0)
        
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>AdaptFin - Relatório</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .table {{ border-collapse: collapse; width: 100%; }}
                .table th, .table td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                .table th {{ background-color: #4CAF50; color: white; }}
                h1 {{ color: #333; }}
            </style>
        </head>
        <body>
            <h1>🧠 AdaptFin - Relatório Financeiro</h1>
            <p>Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
            {html}
        </body>
        </html>
        """
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(full_html)
        
        return filepath
    
    def export_complete_report(self, df, df_mensal, gastos_categoria):
        """Exporta relatório completo com múltiplas abas"""
        filename = f"relatorio_completo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        filepath = os.path.join(self.output_dir, filename)
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # Aba de transações
            df.to_excel(writer, sheet_name='Transações', index=False)
            
            # Aba de resumo mensal
            if not df_mensal.empty:
                df_mensal.to_excel(writer, sheet_name='Resumo Mensal', index=False)
            
            # Aba de gastos por categoria
            if not gastos_categoria.empty:
                gastos_categoria.to_excel(writer, sheet_name='Gastos por Categoria')
            
            # Aba de estatísticas
            stats = pd.DataFrame({
                'Métrica': ['Total de Entradas', 'Total de Saídas', 'Saldo', 
                           'Número de Transações', 'Data do Relatório'],
                'Valor': [
                    df[df['Valor'] > 0]['Valor'].sum(),
                    df[df['Valor'] < 0]['Valor'].sum(),
                    df['Valor'].sum(),
                    len(df),
                    datetime.now().strftime('%d/%m/%Y %H:%M:%S')
                ]
            })
            stats.to_excel(writer, sheet_name='Estatísticas', index=False)
        
        return filepath
    
    def get_download_link(self, filepath, text="Download"):
        """Gera link para download"""
        with open(filepath, 'rb') as f:
            data = f.read()
        
        b64 = base64.b64encode(data).decode()
        filename = os.path.basename(filepath)
        href = f'<a href="data:file/octet-stream;base64,{b64}" download="{filename}">{text}</a>'
        
        return href