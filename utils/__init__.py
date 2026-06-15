"""
Utils Module - Funções utilitárias para o AdaptFin
"""
from .date_utils import (
    format_date_br, parse_date, get_current_month, 
    get_days_between, add_months, get_month_name
)
from .format_utils import (
    format_currency, format_percentage, format_number,
    format_compact_number, truncate_string
)
from .validation_utils import (
    validate_email, validate_phone, validate_date,
    validate_value, validate_description, sanitize_input
)
from .file_utils import (
    read_csv_safe, read_json_safe, write_json_safe,
    get_file_size, ensure_directory
)
from .crypto_utils import (
    hash_password, verify_password, generate_token,
    encrypt_data, decrypt_data
)
from .logging_utils import (
    setup_logger, log_info, log_error, log_warning,
    get_logger
)
from .cache_utils import (
    CacheManager, cached, invalidate_cache,
    memory_cache, disk_cache, get_cache_stats,
    get_from_cache, set_in_cache, clear_cache
)
from .constants import (
    CATEGORIAS_RECEITA, CATEGORIAS_DESPESA,
    MESES_NOMES, DIAS_SEMANA,
    LIMITE_VALOR_MINIMO, LIMITE_VALOR_MAXIMO,
    COLORS, ICONS
)

__all__ = [
    # Date utils
    'format_date_br', 'parse_date', 'get_current_month',
    'get_days_between', 'add_months', 'get_month_name',
    # Format utils
    'format_currency', 'format_percentage', 'format_number',
    'format_compact_number', 'truncate_string',
    # Validation utils
    'validate_email', 'validate_phone', 'validate_date',
    'validate_value', 'validate_description', 'sanitize_input',
    # File utils
    'read_csv_safe', 'read_json_safe', 'write_json_safe',
    'get_file_size', 'ensure_directory',
    # Crypto utils
    'hash_password', 'verify_password', 'generate_token',
    'encrypt_data', 'decrypt_data',
    # Logging utils
    'setup_logger', 'log_info', 'log_error', 'log_warning', 'get_logger',
    # Cache utils
    'CacheManager', 'cached', 'invalidate_cache', 'memory_cache', 'disk_cache',
    # Constants
    'CATEGORIAS_RECEITA', 'CATEGORIAS_DESPESA',
    'MESES_NOMES', 'DIAS_SEMANA',
    'LIMITE_VALOR_MINIMO', 'LIMITE_VALOR_MAXIMO',
    'COLORS', 'ICONS'
]