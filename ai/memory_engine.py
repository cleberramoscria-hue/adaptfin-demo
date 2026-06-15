"""
Engine de Memória - Armazena e recupera informações contextuais
"""
import json
import os
from datetime import datetime
import pandas as pd

class MemoryEngine:
    """Gerencia a memória de longo prazo do sistema"""
    
    def __init__(self, memory_file="data/memory.json"):
        self.memory_file = memory_file
        self.memory = self._load_memory()
    
    def _load_memory(self):
        """Carrega memória do arquivo"""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return self._create_empty_memory()
        return self._create_empty_memory()
    
    def _create_empty_memory(self):
        """Cria memória vazia"""
        return {
            'user_preferences': {},
            'frequent_questions': {},
            'learned_patterns': [],
            'important_dates': [],
            'saved_insights': [],
            'last_interaction': None
        }
    
    def save_memory(self):
        """Salva memória no arquivo"""
        os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            json.dump(self.memory, f, indent=2, ensure_ascii=False)
    
    def remember_question(self, question, answer):
        """Lembra de perguntas frequentes"""
        if question in self.memory['frequent_questions']:
            self.memory['frequent_questions'][question]['count'] += 1
            self.memory['frequent_questions'][question]['last_asked'] = datetime.now().isoformat()
        else:
            self.memory['frequent_questions'][question] = {
                'count': 1,
                'answer': answer,
                'first_asked': datetime.now().isoformat(),
                'last_asked': datetime.now().isoformat()
            }
        
        self.save_memory()
    
    def get_frequent_questions(self, limit=5):
        """Retorna perguntas mais frequentes"""
        sorted_questions = sorted(
            self.memory['frequent_questions'].items(),
            key=lambda x: x[1]['count'],
            reverse=True
        )
        return sorted_questions[:limit]
    
    def remember_preference(self, key, value):
        """Lembra de preferências do usuário"""
        self.memory['user_preferences'][key] = value
        self.save_memory()
    
    def get_preference(self, key, default=None):
        """Recupera preferência do usuário"""
        return self.memory['user_preferences'].get(key, default)
    
    def add_insight(self, insight):
        """Adiciona insight aprendido"""
        self.memory['saved_insights'].append({
            'insight': insight,
            'date': datetime.now().isoformat()
        })
        # Manter apenas últimos 50 insights
        if len(self.memory['saved_insights']) > 50:
            self.memory['saved_insights'] = self.memory['saved_insights'][-50:]
        self.save_memory()
    
    def add_pattern(self, pattern):
        """Adiciona padrão aprendido"""
        self.memory['learned_patterns'].append({
            'pattern': pattern,
            'date': datetime.now().isoformat()
        })
        self.save_memory()
    
    def update_interaction(self):
        """Atualiza timestamp da última interação"""
        self.memory['last_interaction'] = datetime.now().isoformat()
        self.save_memory()
    
    def get_recent_insights(self, limit=5):
        """Retorna insights recentes"""
        return self.memory['saved_insights'][-limit:]
    
    def clear_memory(self):
        """Limpa toda a memória"""
        self.memory = self._create_empty_memory()
        self.save_memory()