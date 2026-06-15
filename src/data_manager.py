import json
import pandas as pd
from datetime import datetime
from pathlib import Path
import shutil

class DataManager:
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.transactions_file = self.data_dir / "transactions.json"
        self.config_file = self.data_dir / "config.json"
        self.backup_dir = self.data_dir / "backups"
        self.backup_dir.mkdir(exist_ok=True)
    
    def save_transactions(self, df):
        try:
            df_dict = df.to_dict(orient='records')
            with open(self.transactions_file, 'w', encoding='utf-8') as f:
                json.dump(df_dict, f, indent=2, default=str, ensure_ascii=False)
            return True
        except:
            return False
    
    def load_transactions(self):
        if self.transactions_file.exists():
            with open(self.transactions_file, 'r', encoding='utf-8') as f:
                return pd.DataFrame(json.load(f))
        return None
    
    def save_config(self, config):
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
    
    def load_config(self):
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def export_to_csv(self, df, filename=None):
        if filename is None:
            filename = f"adaptfin_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        path = self.data_dir / filename
        df.to_csv(path, index=False, encoding='utf-8-sig')
        return str(path)
    
    def export_to_excel(self, df, filename=None):
        if filename is None:
            filename = f"adaptfin_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        path = self.data_dir / filename
        df.to_excel(path, index=False)
        return str(path)