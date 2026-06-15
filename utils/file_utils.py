"""
Utilitários de Arquivo - Leitura, escrita e manipulação de arquivos
"""
import os
import json
import csv
import pandas as pd
from pathlib import Path
from datetime import datetime

def ensure_directory(directory_path):
    """
    Garante que o diretório existe, criando se necessário
    
    Args:
        directory_path: Caminho do diretório
    
    Returns:
        bool: True se sucesso
    """
    try:
        Path(directory_path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        print(f"Erro ao criar diretório {directory_path}: {e}")
        return False

def get_file_size(file_path, unit="MB"):
    """
    Retorna tamanho do arquivo
    
    Args:
        file_path: Caminho do arquivo
        unit: Unidade (B, KB, MB, GB)
    
    Returns:
        float: Tamanho do arquivo
    """
    if not os.path.exists(file_path):
        return 0
    
    size = os.path.getsize(file_path)
    
    units = {
        "B": 1,
        "KB": 1024,
        "MB": 1024 ** 2,
        "GB": 1024 ** 3
    }
    
    return size / units.get(unit.upper(), 1)

def read_json_safe(file_path, default=None):
    """
    Lê arquivo JSON com segurança
    
    Args:
        file_path: Caminho do arquivo
        default: Valor padrão se erro
    
    Returns:
        dict: Conteúdo do JSON
    """
    if default is None:
        default = {}
    
    if not os.path.exists(file_path):
        return default
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Erro ao ler {file_path}: {e}")
        return default

def write_json_safe(file_path, data, indent=2):
    """
    Escreve arquivo JSON com segurança
    
    Args:
        file_path: Caminho do arquivo
        data: Dados a escrever
        indent: Indentação
    
    Returns:
        bool: True se sucesso
    """
    try:
        ensure_directory(os.path.dirname(file_path))
        
        # Criar backup se arquivo existe
        if os.path.exists(file_path):
            backup_path = f"{file_path}.backup"
            try:
                os.rename(file_path, backup_path)
            except:
                pass
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False, default=str)
        
        return True
    except Exception as e:
        print(f"Erro ao escrever {file_path}: {e}")
        return False

def read_csv_safe(file_path, **kwargs):
    """
    Lê arquivo CSV com segurança
    
    Args:
        file_path: Caminho do arquivo
        **kwargs: Argumentos do pandas read_csv
    
    Returns:
        DataFrame: Dados do CSV
    """
    if not os.path.exists(file_path):
        return pd.DataFrame()
    
    try:
        return pd.read_csv(file_path, **kwargs)
    except Exception as e:
        print(f"Erro ao ler {file_path}: {e}")
        return pd.DataFrame()

def write_csv_safe(df, file_path, **kwargs):
    """
    Escreve arquivo CSV com segurança
    
    Args:
        df: DataFrame
        file_path: Caminho do arquivo
        **kwargs: Argumentos do pandas to_csv
    
    Returns:
        bool: True se sucesso
    """
    try:
        ensure_directory(os.path.dirname(file_path))
        df.to_csv(file_path, index=False, encoding='utf-8-sig', **kwargs)
        return True
    except Exception as e:
        print(f"Erro ao escrever {file_path}: {e}")
        return False

def read_excel_safe(file_path, sheet_name=0):
    """
    Lê arquivo Excel com segurança
    
    Args:
        file_path: Caminho do arquivo
        sheet_name: Nome ou índice da planilha
    
    Returns:
        DataFrame: Dados do Excel
    """
    if not os.path.exists(file_path):
        return pd.DataFrame()
    
    try:
        return pd.read_excel(file_path, sheet_name=sheet_name)
    except Exception as e:
        print(f"Erro ao ler {file_path}: {e}")
        return pd.DataFrame()

def write_excel_safe(df, file_path, sheet_name="Sheet1"):
    """
    Escreve arquivo Excel com segurança
    
    Args:
        df: DataFrame
        file_path: Caminho do arquivo
        sheet_name: Nome da planilha
    
    Returns:
        bool: True se sucesso
    """
    try:
        ensure_directory(os.path.dirname(file_path))
        
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        return True
    except Exception as e:
        print(f"Erro ao escrever {file_path}: {e}")
        return False

def get_file_info(file_path):
    """
    Retorna informações do arquivo
    
    Args:
        file_path: Caminho do arquivo
    
    Returns:
        dict: Informações do arquivo
    """
    if not os.path.exists(file_path):
        return None
    
    stat = os.stat(file_path)
    
    return {
        'name': os.path.basename(file_path),
        'path': file_path,
        'size': stat.st_size,
        'size_mb': round(stat.st_size / (1024 * 1024), 2),
        'created': datetime.fromtimestamp(stat.st_ctime),
        'modified': datetime.fromtimestamp(stat.st_mtime),
        'extension': os.path.splitext(file_path)[1].lower()
    }

def list_files(directory, extension=None, recursive=False):
    """
    Lista arquivos em um diretório
    
    Args:
        directory: Diretório a listar
        extension: Filtrar por extensão
        recursive: Buscar recursivamente
    
    Returns:
        list: Lista de arquivos
    """
    if not os.path.exists(directory):
        return []
    
    files = []
    
    if recursive:
        for root, dirs, filenames in os.walk(directory):
            for filename in filenames:
                if extension and not filename.endswith(extension):
                    continue
                files.append(os.path.join(root, filename))
    else:
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path):
                if extension and not filename.endswith(extension):
                    continue
                files.append(file_path)
    
    return sorted(files)

def delete_file(file_path):
    """
    Deleta arquivo com segurança
    
    Args:
        file_path: Caminho do arquivo
    
    Returns:
        bool: True se sucesso
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception as e:
        print(f"Erro ao deletar {file_path}: {e}")
        return False

def copy_file(source, destination):
    """
    Copia arquivo
    
    Args:
        source: Arquivo origem
        destination: Arquivo destino
    
    Returns:
        bool: True se sucesso
    """
    try:
        ensure_directory(os.path.dirname(destination))
        import shutil
        shutil.copy2(source, destination)
        return True
    except Exception as e:
        print(f"Erro ao copiar {source} para {destination}: {e}")
        return False

def get_temp_file(prefix="adaptfin_", suffix=".tmp"):
    """
    Cria arquivo temporário
    
    Args:
        prefix: Prefixo do arquivo
        suffix: Sufixo do arquivo
    
    Returns:
        str: Caminho do arquivo temporário
    """
    import tempfile
    fd, path = tempfile.mkstemp(prefix=prefix, suffix=suffix)
    os.close(fd)
    return path