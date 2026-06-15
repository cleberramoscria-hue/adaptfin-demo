"""
Utilitários de Logging - Sistema de logs para debug e monitoramento
"""
import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
import traceback

# Configuração global
LOGGER_NAME = "adaptfin"
LOG_LEVEL = os.environ.get("ADAPTFIN_LOG_LEVEL", "INFO").upper()
LOG_DIR = "logs"

# Mapeamento de níveis
LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL
}

def setup_logger(name=LOGGER_NAME, level=LOG_LEVEL, log_file=None):
    """
    Configura logger com handlers para arquivo e console
    
    Args:
        name: Nome do logger
        level: Nível de log
        log_file: Arquivo de log (opcional)
    
    Returns:
        logging.Logger: Logger configurado
    """
    # Criar diretório de logs
    os.makedirs(LOG_DIR, exist_ok=True)
    
    # Definir arquivo de log padrão
    if log_file is None:
        log_file = os.path.join(LOG_DIR, f"adaptfin_{datetime.now().strftime('%Y%m%d')}.log")
    
    # Criar logger
    logger = logging.getLogger(name)
    logger.setLevel(LEVELS.get(level, logging.INFO))
    
    # Evitar duplicação de handlers
    if logger.handlers:
        return logger
    
    # Formato do log
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler para arquivo (com rotação)
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Handler para console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger

def get_logger(name=LOGGER_NAME):
    """
    Obtém logger existente ou cria novo
    
    Args:
        name: Nome do logger
    
    Returns:
        logging.Logger: Logger
    """
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        return setup_logger(name)
    
    return logger

def log_info(message, name=LOGGER_NAME):
    """Log nível INFO"""
    logger = get_logger(name)
    logger.info(message)

def log_warning(message, name=LOGGER_NAME):
    """Log nível WARNING"""
    logger = get_logger(name)
    logger.warning(message)

def log_error(message, name=LOGGER_NAME, exc_info=True):
    """Log nível ERROR com traceback"""
    logger = get_logger(name)
    logger.error(message, exc_info=exc_info)

def log_debug(message, name=LOGGER_NAME):
    """Log nível DEBUG"""
    logger = get_logger(name)
    logger.debug(message)

def log_critical(message, name=LOGGER_NAME):
    """Log nível CRITICAL"""
    logger = get_logger(name)
    logger.critical(message)

def log_exception(e, context="", name=LOGGER_NAME):
    """
    Log de exceção com contexto
    
    Args:
        e: Exceção capturada
        context: Contexto da exceção
        name: Nome do logger
    """
    logger = get_logger(name)
    error_msg = f"{context}: {str(e)}" if context else str(e)
    logger.error(error_msg, exc_info=True)

def log_function_call(func):
    """
    Decorator para log de chamada de função
    
    Args:
        func: Função a decorar
    
    Returns:
        wrapper: Função decorada
    """
    def wrapper(*args, **kwargs):
        logger = get_logger()
        logger.debug(f"Chamando {func.__name__} com args={args}, kwargs={kwargs}")
        
        try:
            result = func(*args, **kwargs)
            logger.debug(f"{func.__name__} retornou {result}")
            return result
        except Exception as e:
            logger.error(f"Erro em {func.__name__}: {e}", exc_info=True)
            raise
    
    return wrapper

def log_performance(func):
    """
    Decorator para log de performance
    
    Args:
        func: Função a decorar
    
    Returns:
        wrapper: Função decorada
    """
    def wrapper(*args, **kwargs):
        import time
        logger = get_logger()
        
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        
        logger.info(f"{func.__name__} executado em {end - start:.3f}s")
        return result
    
    return wrapper

class LoggerContext:
    """Context manager para logging temporário"""
    
    def __init__(self, name, level="INFO"):
        self.name = name
        self.level = level
        self.logger = get_logger(name)
        self.old_level = self.logger.level
    
    def __enter__(self):
        self.old_level = self.logger.level
        self.logger.setLevel(LEVELS.get(self.level, logging.INFO))
        return self.logger
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logger.setLevel(self.old_level)
        
        if exc_type:
            self.logger.error(f"Erro: {exc_val}", exc_info=True)
        
        return False

def log_to_file(message, file_name=None):
    """
    Log simples para arquivo (sem formato estruturado)
    
    Args:
        message: Mensagem a logar
        file_name: Nome do arquivo (opcional)
    """
    if file_name is None:
        file_name = f"adaptfin_{datetime.now().strftime('%Y%m%d')}.log"
    
    file_path = os.path.join(LOG_DIR, file_name)
    os.makedirs(LOG_DIR, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"{timestamp} - {message}\n"
    
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write(log_line)

def get_log_files():
    """
    Lista arquivos de log disponíveis
    
    Returns:
        list: Lista de arquivos de log
    """
    if not os.path.exists(LOG_DIR):
        return []
    
    files = []
    for f in os.listdir(LOG_DIR):
        if f.endswith('.log'):
            file_path = os.path.join(LOG_DIR, f)
            files.append({
                'name': f,
                'path': file_path,
                'size': os.path.getsize(file_path),
                'modified': datetime.fromtimestamp(os.path.getmtime(file_path))
            })
    
    return sorted(files, key=lambda x: x['modified'], reverse=True)

def clear_logs(days_old=30):
    """
    Limpa logs mais antigos que X dias
    
    Args:
        days_old: Dias de retenção
    
    Returns:
        int: Número de arquivos removidos
    """
    from datetime import timedelta
    
    if not os.path.exists(LOG_DIR):
        return 0
    
    cutoff = datetime.now() - timedelta(days=days_old)
    removed = 0
    
    for f in os.listdir(LOG_DIR):
        file_path = os.path.join(LOG_DIR, f)
        mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
        
        if mtime < cutoff:
            try:
                os.remove(file_path)
                removed += 1
            except:
                pass
    
    return removed