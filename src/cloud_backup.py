"""
Backup automático para a nuvem
"""
import json
import os
from datetime import datetime
import requests

class CloudBackup:
    """Gerencia backup dos dados para a nuvem"""
    
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.backup_url = "https://api.github.com/gists"  # Exemplo com GitHub Gist
        
    def fazer_backup_local(self):
        """Faz backup local dos dados"""
        backup_dir = os.path.join(self.data_dir, "backups")
        os.makedirs(backup_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(backup_dir, f"backup_{timestamp}.json")
        
        # Copiar arquivos
        import shutil
        shutil.copy(os.path.join(self.data_dir, "transactions.json"), backup_file)
        
        return backup_file
    
    def restaurar_backup(self, backup_file):
        """Restaura um backup anterior"""
        import shutil
        shutil.copy(backup_file, os.path.join(self.data_dir, "transactions.json"))
        return True