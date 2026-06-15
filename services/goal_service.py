"""
Serviço de Metas - Gerenciamento de metas financeiras
"""
import json
import os
from datetime import datetime, timedelta

class GoalService:
    """Gerencia metas financeiras do usuário"""
    
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.goals_file = os.path.join(data_dir, "goals.json")
        self._init_storage()
    
    def _init_storage(self):
        """Inicializa armazenamento"""
        os.makedirs(self.data_dir, exist_ok=True)
        
        if not os.path.exists(self.goals_file):
            with open(self.goals_file, 'w') as f:
                json.dump([], f)
    
    def add_goal(self, name, target_value, deadline, monthly_contribution=0):
        """Adiciona nova meta"""
        with open(self.goals_file, 'r') as f:
            goals = json.load(f)
        
        new_goal = {
            'id': len(goals) + 1,
            'name': name,
            'target_value': target_value,
            'current_value': 0,
            'deadline': deadline,
            'monthly_contribution': monthly_contribution,
            'created_at': datetime.now().isoformat(),
            'status': 'active'
        }
        
        goals.append(new_goal)
        
        with open(self.goals_file, 'w') as f:
            json.dump(goals, f, indent=2)
        
        return new_goal
    
    def update_goal_progress(self, goal_id, amount):
        """Atualiza progresso da meta"""
        with open(self.goals_file, 'r') as f:
            goals = json.load(f)
        
        for goal in goals:
            if goal['id'] == goal_id:
                goal['current_value'] += amount
                
                if goal['current_value'] >= goal['target_value']:
                    goal['status'] = 'completed'
                    goal['completed_at'] = datetime.now().isoformat()
                
                break
        
        with open(self.goals_file, 'w') as f:
            json.dump(goals, f, indent=2)
        
        return True
    
    def get_active_goals(self):
        """Retorna metas ativas"""
        with open(self.goals_file, 'r') as f:
            goals = json.load(f)
        
        return [g for g in goals if g['status'] == 'active']
    
    def get_completed_goals(self):
        """Retorna metas concluídas"""
        with open(self.goals_file, 'r') as f:
            goals = json.load(f)
        
        return [g for g in goals if g['status'] == 'completed']
    
    def get_goal_progress(self, goal_id):
        """Calcula progresso da meta"""
        with open(self.goals_file, 'r') as f:
            goals = json.load(f)
        
        for goal in goals:
            if goal['id'] == goal_id:
                percent = (goal['current_value'] / goal['target_value']) * 100 if goal['target_value'] > 0 else 0
                remaining = goal['target_value'] - goal['current_value']
                
                # Calcular projeção
                if goal['monthly_contribution'] > 0:
                    months_needed = remaining / goal['monthly_contribution']
                    projected_date = datetime.now() + timedelta(days=months_needed * 30)
                else:
                    projected_date = None
                
                return {
                    'percent': min(100, percent),
                    'remaining': remaining,
                    'projected_date': projected_date.isoformat() if projected_date else None,
                    'monthly_needed': remaining / 30 if remaining > 0 else 0
                }
        
        return None
    
    def delete_goal(self, goal_id):
        """Remove uma meta"""
        with open(self.goals_file, 'r') as f:
            goals = json.load(f)
        
        goals = [g for g in goals if g['id'] != goal_id]
        
        with open(self.goals_file, 'w') as f:
            json.dump(goals, f, indent=2)
        
        return True
    
    def get_goal_summary(self):
        """Resumo de todas as metas"""
        active = self.get_active_goals()
        completed = self.get_completed_goals()
        
        total_target = sum(g['target_value'] for g in active)
        total_current = sum(g['current_value'] for g in active)
        total_completed_value = sum(g['target_value'] for g in completed)
        
        return {
            'total_goals': len(active) + len(completed),
            'active_goals': len(active),
            'completed_goals': len(completed),
            'total_target': total_target,
            'total_current': total_current,
            'total_progress_percent': (total_current / total_target * 100) if total_target > 0 else 0,
            'total_completed_value': total_completed_value
        }
    
    def suggest_goal_contributions(self, monthly_income):
        """Sugere contribuições mensais para metas"""
        active_goals = self.get_active_goals()
        
        if not active_goals:
            return []
        
        # Orçamento recomendado para metas (20% da renda)
        total_budget = monthly_income * 0.2
        
        suggestions = []
        for goal in active_goals:
            remaining = goal['target_value'] - goal['current_value']
            days_remaining = max(1, (datetime.fromisoformat(goal['deadline']) - datetime.now()).days)
            months_remaining = days_remaining / 30
            
            suggested = remaining / months_remaining if months_remaining > 0 else 0
            
            # Ajustar se ultrapassar orçamento total
            if suggested > total_budget / len(active_goals):
                suggested = total_budget / len(active_goals)
            
            suggestions.append({
                'goal_id': goal['id'],
                'goal_name': goal['name'],
                'current_contribution': goal['monthly_contribution'],
                'suggested_contribution': round(suggested, 2),
                'remaining': remaining,
                'months_remaining': round(months_remaining, 1)
            })
        
        return suggestions