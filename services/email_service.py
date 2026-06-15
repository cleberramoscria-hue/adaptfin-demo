"""
Serviço de Email - Envio de relatórios e notificações
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from datetime import datetime

class EmailService:
    """Serviço para envio de emails"""
    
    def __init__(self, smtp_server="smtp.gmail.com", smtp_port=587):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = None
        self.sender_password = None
    
    def configure(self, email, password):
        """Configura credenciais de email"""
        self.sender_email = email
        self.sender_password = password
    
    def send_report(self, to_email, report_data, report_type="mensal"):
        """Envia relatório por email"""
        if not self.sender_email:
            return False, "Email não configurado"
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = to_email
            msg['Subject'] = f"AdaptFin - Relatório {report_type} - {datetime.now().strftime('%d/%m/%Y')}"
            
            # Corpo do email
            body = self._format_email_body(report_data, report_type)
            msg.attach(MIMEText(body, 'html', 'utf-8'))
            
            # Anexar relatório se for arquivo
            if isinstance(report_data, str) and os.path.exists(report_data):
                with open(report_data, 'rb') as f:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(f.read())
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(report_data)}"')
                    msg.attach(part)
            
            # Enviar email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            server.send_message(msg)
            server.quit()
            
            return True, "Relatório enviado com sucesso!"
        
        except Exception as e:
            return False, f"Erro ao enviar email: {str(e)}"
    
    def _format_email_body(self, data, report_type):
        """Formata o corpo do email em HTML"""
        return f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .header {{ background-color: #2ecc71; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .metric {{ background-color: #f0f2f6; padding: 15px; margin: 10px 0; border-radius: 10px; }}
                .footer {{ text-align: center; padding: 20px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🧠 AdaptFin</h1>
                <p>Relatório Financeiro - {report_type}</p>
            </div>
            <div class="content">
                <h2>Olá!</h2>
                <p>Este é seu relatório financeiro do período.</p>
                
                <div class="metric">
                    <h3>Resumo</h3>
                    <p>Total de Entradas: R$ {data.get('total_entradas', 0):,.2f}</p>
                    <p>Total de Saídas: R$ {data.get('total_saidas', 0):,.2f}</p>
                    <p>Saldo: R$ {data.get('saldo', 0):,.2f}</p>
                </div>
                
                <p>Acesse o AdaptFin para mais detalhes!</p>
            </div>
            <div class="footer">
                <p>AdaptFin - Seu assistente financeiro inteligente</p>
                <p>© 2024 AdaptFin</p>
            </div>
        </body>
        </html>
        """
    
    def send_alert(self, to_email, alert_type, message):
        """Envia alerta por email"""
        if not self.sender_email:
            return False
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = to_email
            msg['Subject'] = f"AdaptFin - Alerta: {alert_type}"
            
            body = f"""
            <html>
            <body>
                <h2>⚠️ Alerta Financeiro</h2>
                <p>{message}</p>
                <p>Acesse o AdaptFin para mais detalhes!</p>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(body, 'html', 'utf-8'))
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            server.send_message(msg)
            server.quit()
            
            return True
        
        except:
            return False