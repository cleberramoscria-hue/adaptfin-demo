"""
Serviço de Backup - Backup automático e restauração
"""
import json
import os
import shutil
from datetime import datetime
import zipfile
import glob

class BackupService:
    """Gerencia backups automáticos dos dados do usuário"""
    
    def __init__(self, data_dir="data", backup_dir="data/backups"):
        self.data_dir = data_dir
        self.backup_dir = backup_dir
        os.makedirs(backup_dir, exist_ok=True)
    
    def create_backup(self, backup_name=None):
        """Cria um backup dos dados"""
        if backup_name is None:
            backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        backup_path = os.path.join(self.backup_dir, backup_name)
        os.makedirs(backup_path, exist_ok=True)
        
        files_copied = []
        for file in os.listdir(self.data_dir):
            if file.endswith('.json') and file != 'backups':
                src = os.path.join(self.data_dir, file)
                dst = os.path.join(backup_path, file)
                shutil.copy2(src, dst)
                files_copied.append(file)
        
        metadata = {
            'backup_name': backup_name,
            'created_at': datetime.now().isoformat(),
            'files': files_copied,
            'version': '2.0.0',
            'total_files': len(files_copied)
        }
        
        with open(os.path.join(backup_path, 'metadata.json'), 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        return backup_path
    
    def create_zip_backup(self, backup_name=None):
        """Cria backup compactado em ZIP"""
        backup_path = self.create_backup(backup_name)
        zip_path = os.path.join(self.backup_dir, f"{os.path.basename(backup_path)}.zip")
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(backup_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, backup_path)
                    zipf.write(file_path, arcname)
        
        shutil.rmtree(backup_path)
        return zip_path
    
    def restore_backup(self, backup_path):
        """Restaura um backup"""
        temp_dir = None
        
        if backup_path.endswith('.zip'):
            temp_dir = os.path.join(self.backup_dir, 'temp_restore')
            os.makedirs(temp_dir, exist_ok=True)
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                zipf.extractall(temp_dir)
            backup_path = temp_dir
        
        metadata_file = os.path.join(backup_path, 'metadata.json')
        if not os.path.exists(metadata_file):
            if temp_dir:
                shutil.rmtree(temp_dir)
            return False, "Backup inválido: metadata.json não encontrado"
        
        restored_files = []
        for file in os.listdir(backup_path):
            if file.endswith('.json') and file != 'metadata.json':
                src = os.path.join(backup_path, file)
                dst = os.path.join(self.data_dir, file)
                if os.path.exists(dst):
                    old_backup = os.path.join(self.backup_dir, f"pre_restore_{file}")
                    shutil.copy2(dst, old_backup)
                shutil.copy2(src, dst)
                restored_files.append(file)
        
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        
        return True, f"Restaurados {len(restored_files)} arquivos"
    
    def list_backups(self):
        """Lista todos os backups disponíveis"""
        backups = []
        
        for item in os.listdir(self.backup_dir):
            item_path = os.path.join(self.backup_dir, item)
            
            if item.endswith('.zip'):
                stat = os.stat(item_path)
                backups.append({
                    'name': item,
                    'type': 'zip',
                    'path': item_path,
                    'size': stat.st_size,
                    'size_mb': round(stat.st_size / (1024 * 1024), 2),
                    'created_at': datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
            elif os.path.isdir(item_path):
                metadata_file = os.path.join(item_path, 'metadata.json')
                if os.path.exists(metadata_file):
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                    backups.append({
                        'name': item,
                        'type': 'folder',
                        'path': item_path,
                        'created_at': metadata.get('created_at'),
                        'files': metadata.get('files', []),
                        'total_files': metadata.get('total_files', 0)
                    })
        
        backups.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        return backups
    
    def auto_backup(self, max_backups=10):
        """Faz backup automático (mantém apenas últimos N backups)"""
        zip_path = self.create_zip_backup()
        backups = self.list_backups()
        zip_backups = [b for b in backups if b['type'] == 'zip']
        
        if len(zip_backups) > max_backups:
            for backup in zip_backups[max_backups:]:
                if os.path.exists(backup['path']):
                    os.remove(backup['path'])
        return zip_path
    
    def delete_backup(self, backup_name):
        """Deleta um backup específico"""
        backup_path = os.path.join(self.backup_dir, backup_name)
        
        if os.path.exists(backup_path):
            if os.path.isdir(backup_path):
                shutil.rmtree(backup_path)
            else:
                os.remove(backup_path)
            return True, "Backup removido"
        
        zip_path = os.path.join(self.backup_dir, f"{backup_name}.zip")
        if os.path.exists(zip_path):
            os.remove(zip_path)
            return True, "Backup removido"
        
        return False, "Backup não encontrado"
    
    def get_backup_info(self, backup_name):
        """Obtém informações detalhadas de um backup"""
        backup_path = os.path.join(self.backup_dir, backup_name)
        
        if not os.path.exists(backup_path):
            zip_path = os.path.join(self.backup_dir, f"{backup_name}.zip")
            if os.path.exists(zip_path):
                backup_path = zip_path
            else:
                return None
        
        if backup_path.endswith('.zip'):
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                file_list = zipf.namelist()
                total_size = sum(zipf.getinfo(f).file_size for f in file_list)
            return {
                'name': backup_name,
                'type': 'zip',
                'path': backup_path,
                'size_mb': round(total_size / (1024 * 1024), 2),
                'files': file_list,
                'total_files': len(file_list)
            }
        else:
            metadata_file = os.path.join(backup_path, 'metadata.json')
            if os.path.exists(metadata_file):
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        return None
    
    def schedule_daily_backup(self):
        """Agenda backup diário"""
        today = datetime.now().strftime('%Y%m%d')
        backups = self.list_backups()
        
        for backup in backups:
            created_at = backup.get('created_at', '')
            if created_at and created_at.startswith(today):
                return None
        
        return self.auto_backup()
    
    def export_backup(self, backup_name, export_path):
        """Exporta backup para local específico"""
        backup_info = self.get_backup_info(backup_name)
        
        if not backup_info:
            return False, "Backup não encontrado"
        
        src = backup_info['path']
        dst = os.path.join(export_path, os.path.basename(src))
        shutil.copy2(src, dst)
        return True, f"Backup exportado para {dst}"