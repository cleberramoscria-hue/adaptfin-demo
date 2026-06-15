"""
Serviço de Notificações - Alertas e lembretes
"""
from datetime import datetime, timedelta
import json
import os

class NotificationService:
    """Gerencia notificações e alertas do sistema"""
    
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.notifications_file = os.path.join(data_dir, "notifications.json")
        self._init_storage()
    
    def _init_storage(self):
        """Inicializa armazenamento"""
        os.makedirs(self.data_dir, exist_ok=True)
        
        if not os.path.exists(self.notifications_file):
            with open(self.notifications_file, 'w') as f:
                json.dump([], f)
    
    def add_notification(self, title, message, type="info", days_before=0):
        """Adiciona uma notificação"""
        with open(self.notifications_file, 'r') as f:
            notifications = json.load(f)
        
        notification = {
            'id': len(notifications) + 1,
            'title': title,
            'message': message,
            'type': type,
            'created_at': datetime.now().isoformat(),
            'read': False,
            'trigger_date': (datetime.now() + timedelta(days=days_before)).isoformat()
        }
        
        notifications.append(notification)
        
        with open(self.notifications_file, 'w') as f:
            json.dump(notifications, f, indent=2)
        
        return notification
    
    def get_unread_notifications(self):
        """Retorna notificações não lidas"""
        with open(self.notifications_file, 'r') as f:
            notifications = json.load(f)
        
        return [n for n in notifications if not n['read']]
    
    def mark_as_read(self, notification_id):
        """Marca notificação como lida"""
        with open(self.notifications_file, 'r') as f:
            notifications = json.load(f)
        
        for n in notifications:
            if n['id'] == notification_id:
                n['read'] = True
                break
        
        with open(self.notifications_file, 'w') as f:
            json.dump(notifications, f, indent=2)
    
    def check_budget_alert(self, gasto_atual, limite, categoria=""):
        """Verifica alertas de orçamento"""
        percentual = (gasto_atual / limite) * 100 if limite > 0 else 0
        
        if percentual >= 100:
            self.add_notification(
                f"🚨 Orçamento Excedido - {categoria}",
                f"Você já gastou R$ {gasto_atual:.2f} de R$ {limite:.2f} ({(percentual-100):.0f}% acima do limite)",
                "danger"
            )
        elif percentual >= 80:
            self.add_notification(
                f"⚠️ Atenção - {categoria}",
                f"Você já utilizou {percentual:.0f}% do orçamento de R$ {limite:.2f}",
                "warning"
            )
    
    def check_bill_reminder(self, contas):
        """Verifica lembretes de contas a vencer"""
        hoje = datetime.now().date()
        
        for conta in contas:
            dias_para_vencer = (conta['data'] - hoje).days
            
            if dias_para_vencer == 7:
                self.add_notification(
                    f"📅 Lembrete - {conta['descricao']}",
                    f"Conta vence em 7 dias. Valor: R$ {conta['valor']:.2f}",
                    "info",
                    dias_before=7
                )
            elif dias_para_vencer == 3:
                self.add_notification(
                    f"📅 Lembrete - {conta['descricao']}",
                    f"Conta vence em 3 dias. Valor: R$ {conta['valor']:.2f}",
                    "warning",
                    dias_before=3
                )
            elif dias_para_vencer == 1:
                self.add_notification(
                    f"🚨 Último dia - {conta['descricao']}",
                    f"Conta vence amanhã! Valor: R$ {conta['valor']:.2f}",
                    "danger",
                    dias_before=1
                )
    
    def check_goal_alert(self, meta):
        """Verifica alertas de metas"""
        percentual = (meta['economizado'] / meta['valor']) * 100 if meta['valor'] > 0 else 0
        
        if percentual >= 100:
            self.add_notification(
                f"🎉 Meta Alcançada - {meta['nome']}",
                f"Parabéns! Você atingiu sua meta de R$ {meta['valor']:.2f}!",
                "success"
            )
        elif percentual >= 75:
            self.add_notification(
                f"📈 Quase lá - {meta['nome']}",
                f"Faltam apenas R$ {meta['valor'] - meta['economizado']:.2f} para atingir sua meta!",
                "info"
            )
    
    def check_low_balance_alert(self, saldo, limite_minimo=1000):
        """Verifica alerta de saldo baixo"""
        if saldo < 0:
            self.add_notification(
                "🚨 Conta negativada!",
                f"Seu saldo está negativo em R$ {abs(saldo):.2f}",
                "danger"
            )
        elif saldo < limite_minimo:
            self.add_notification(
                "⚠️ Saldo Baixo",
                f"Seu saldo está em R$ {saldo:.2f}. Recomendamos cautela nos gastos.",
                "warning"
            )
    
    def get_all_notifications(self):
        """Retorna todas as notificações"""
        with open(self.notifications_file, 'r') as f:
            return json.load(f)
    
    def clear_all(self):
        """Limpa todas as notificações"""
        with open(self.notifications_file, 'w') as f:
            json.dump([], f)