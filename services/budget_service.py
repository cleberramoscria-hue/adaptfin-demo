"""
Serviço de Orçamento - Gerenciamento de orçamentos mensais
"""
import json
import os
from datetime import datetime

class BudgetService:
    """Gerencia orçamentos mensais por categoria"""
    
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.budget_file = os.path.join(data_dir, "budgets.json")
        self._init_storage()
    
    def _init_storage(self):
        """Inicializa armazenamento"""
        os.makedirs(self.data_dir, exist_ok=True)
        
        if not os.path.exists(self.budget_file):
            with open(self.budget_file, 'w') as f:
                json.dump({}, f)
    
    def set_budget(self, ano, mes, categoria, limite):
        """Define orçamento para uma categoria em um mês específico"""
        with open(self.budget_file, 'r') as f:
            budgets = json.load(f)
        
        key = f"{ano}_{mes}"
        if key not in budgets:
            budgets[key] = {}
        
        budgets[key][categoria] = limite
        
        with open(self.budget_file, 'w') as f:
            json.dump(budgets, f, indent=2)
        
        return True
    
    def get_budget(self, ano, mes, categoria):
        """Obtém orçamento de uma categoria"""
        with open(self.budget_file, 'r') as f:
            budgets = json.load(f)
        
        key = f"{ano}_{mes}"
        return budgets.get(key, {}).get(categoria, 0)
    
    def get_all_budgets(self, ano, mes):
        """Obtém todos os orçamentos de um mês"""
        with open(self.budget_file, 'r') as f:
            budgets = json.load(f)
        
        key = f"{ano}_{mes}"
        return budgets.get(key, {})
    
    def check_budget_status(self, ano, mes, gastos_reais):
        """Verifica status do orçamento vs gastos reais"""
        budgets = self.get_all_budgets(ano, mes)
        
        if not budgets:
            return []
        
        status = []
        for categoria, limite in budgets.items():
            gasto_real = gastos_reais.get(categoria, 0)
            percentual = (gasto_real / limite) * 100 if limite > 0 else 0
            
            if percentual >= 100:
                status_level = "critical"
            elif percentual >= 80:
                status_level = "warning"
            elif percentual >= 50:
                status_level = "attention"
            else:
                status_level = "good"
            
            status.append({
                'categoria': categoria,
                'limite': limite,
                'gasto_real': gasto_real,
                'percentual': percentual,
                'restante': max(0, limite - gasto_real),
                'excedente': max(0, gasto_real - limite),
                'status': status_level
            })
        
        return status
    
    def suggest_budget(self, df, meses_anteriores=3):
        """Sugere orçamento baseado em histórico"""
        from datetime import timedelta
        
        sugestoes = {}
        hoje = datetime.now()
        
        for i in range(meses_anteriores):
            mes = hoje.month - i
            ano = hoje.year
            if mes <= 0:
                mes += 12
                ano -= 1
            
            df_mes = df[(df['Data'].dt.month == mes) & (df['Data'].dt.year == ano)]
            gastos_mes = df_mes[df_mes['Valor'] < 0].groupby('Categoria')['Valor'].sum().abs()
            
            for cat, valor in gastos_mes.items():
                if cat not in sugestoes:
                    sugestoes[cat] = []
                sugestoes[cat].append(valor)
        
        # Calcular média + margem de 10%
        resultado = {}
        for cat, valores in sugestoes.items():
            media = sum(valores) / len(valores)
            resultado[cat] = media * 1.1  # 10% a mais que a média
        
        return resultado
    
    def reset_month_budget(self, ano, mes):
        """Reseta orçamentos de um mês"""
        with open(self.budget_file, 'r') as f:
            budgets = json.load(f)
        
        key = f"{ano}_{mes}"
        if key in budgets:
            del budgets[key]
            
            with open(self.budget_file, 'w') as f:
                json.dump(budgets, f, indent=2)
            
            return True
        
        return False
    
    def copy_budget_from_previous_month(self, ano, mes):
        """Copia orçamento do mês anterior"""
        mes_anterior = mes - 1 if mes > 1 else 12
        ano_anterior = ano if mes > 1 else ano - 1
        
        budgets_anteriores = self.get_all_budgets(ano_anterior, mes_anterior)
        
        if not budgets_anteriores:
            return False
        
        for categoria, limite in budgets_anteriores.items():
            self.set_budget(ano, mes, categoria, limite)
        
        return True