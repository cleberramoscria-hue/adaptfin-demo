"""
Utilitários de Formatação - Formatação de valores, números, textos
"""
import locale
from decimal import Decimal, ROUND_HALF_UP

# Tentar configurar locale para português
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'portuguese')
    except:
        pass

def format_currency(value, show_symbol=True, decimal_places=2):
    """
    Formata valor para moeda brasileira
    
    Args:
        value: Valor numérico
        show_symbol: Mostrar símbolo R$
        decimal_places: Casas decimais
    
    Returns:
        str: Valor formatado (ex: R$ 1.234,56)
    """
    if value is None:
        value = 0
    
    try:
        valor_formatado = f"{value:,.{decimal_places}f}"
        valor_formatado = valor_formatado.replace(",", "X").replace(".", ",").replace("X", ".")
        
        if show_symbol:
            return f"R$ {valor_formatado}"
        return valor_formatado
    except:
        return "R$ 0,00"

def format_percentage(value, decimal_places=1, show_symbol=True):
    """
    Formata valor como porcentagem
    
    Args:
        value: Valor numérico (0-100)
        decimal_places: Casas decimais
        show_symbol: Mostrar símbolo %
    
    Returns:
        str: Porcentagem formatada (ex: 25.5%)
    """
    if value is None:
        value = 0
    
    try:
        formatted = f"{value:.{decimal_places}f}".replace(".", ",")
        if show_symbol:
            return f"{formatted}%"
        return formatted
    except:
        return "0%"

def format_number(value, decimal_places=0, use_separator=True):
    """
    Formata número com separadores de milhar
    
    Args:
        value: Valor numérico
        decimal_places: Casas decimais
        use_separator: Usar separador de milhar
    
    Returns:
        str: Número formatado
    """
    if value is None:
        value = 0
    
    try:
        if use_separator:
            formatted = f"{value:,.{decimal_places}f}"
            formatted = formatted.replace(",", "X").replace(".", ",").replace("X", ".")
        else:
            formatted = f"{value:.{decimal_places}f}".replace(".", ",")
        return formatted
    except:
        return str(value)

def format_compact_number(value):
    """
    Formata número de forma compacta (K, M, B)
    
    Args:
        value: Valor numérico
    
    Returns:
        str: Número compactado (ex: 1.5K, 2.3M)
    """
    if value is None:
        return "0"
    
    abs_value = abs(value)
    sign = "-" if value < 0 else ""
    
    if abs_value >= 1_000_000_000:
        return f"{sign}{abs_value / 1_000_000_000:.1f}B"
    elif abs_value >= 1_000_000:
        return f"{sign}{abs_value / 1_000_000:.1f}M"
    elif abs_value >= 1_000:
        return f"{sign}{abs_value / 1_000:.1f}K"
    else:
        return f"{sign}{abs_value:.0f}"

def truncate_string(text, max_length=50, suffix="..."):
    """
    Trunca string se exceder tamanho máximo
    
    Args:
        text: Texto original
        max_length: Tamanho máximo
        suffix: Sufixo para texto truncado
    
    Returns:
        str: Texto truncado
    """
    if not text:
        return ""
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix

def slugify(text):
    """
    Converte texto para slug (URL amigável)
    
    Args:
        text: Texto original
    
    Returns:
        str: Slug
    """
    import re
    try:
        from unidecode import unidecode
        text = unidecode(str(text).lower().strip())
    except:
        # Fallback simples se unidecode não estiver instalado
        text = str(text).lower().strip()
    
    text = re.sub(r'[^a-z0-9]+', '-', text)
    text = re.sub(r'-+', '-', text)
    text = text.strip('-')
    
    return text

def format_plural(count, singular, plural=None):
    """
    Formata plural de palavras
    
    Args:
        count: Número
        singular: Forma singular
        plural: Forma plural (se None, adiciona 's')
    
    Returns:
        str: Palavra no plural correto
    """
    if count == 1:
        return singular
    
    if plural:
        return plural
    return f"{singular}s"

def format_bytes(size):
    """
    Formata bytes para formato legível
    
    Args:
        size: Tamanho em bytes
    
    Returns:
        str: Tamanho formatado (ex: 1.5 MB)
    """
    if size is None:
        return "0 B"
    
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    
    for unit in units:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    
    return f"{size:.1f} PB"

def format_duration(seconds):
    """
    Formata duração em segundos para formato legível
    
    Args:
        seconds: Segundos
    
    Returns:
        str: Duração formatada (ex: 2h 30min)
    """
    if seconds is None:
        return "0s"
    
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    
    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if seconds > 0 or not parts:
        parts.append(f"{seconds}s")
    
    return " ".join(parts)

def format_cpf(cpf):
    """Formata CPF (XXX.XXX.XXX-XX)"""
    cpf = str(cpf).zfill(11)
    return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"

def format_cnpj(cnpj):
    """Formata CNPJ (XX.XXX.XXX/XXXX-XX)"""
    cnpj = str(cnpj).zfill(14)
    return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"

def format_phone(phone):
    """Formata telefone ((XX) XXXX-XXXX ou (XX) XXXXX-XXXX)"""
    phone = str(phone).replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    
    if len(phone) == 10:
        return f"({phone[:2]}) {phone[2:6]}-{phone[6:]}"
    elif len(phone) == 11:
        return f"({phone[:2]}) {phone[2:7]}-{phone[7:]}"
    return phone

def format_cep(cep):
    """Formata CEP (XXXXX-XXX)"""
    cep = str(cep).zfill(8)
    return f"{cep[:5]}-{cep[5:]}"

def capitalize_words(text):
    """Capitaliza cada palavra do texto"""
    if not text:
        return ""
    return " ".join(word.capitalize() for word in text.split())

def remove_accents(text):
    """Remove acentos do texto"""
    try:
        from unidecode import unidecode
        return unidecode(str(text))
    except:
        # Fallback simples
        replacements = {
            'á': 'a', 'à': 'a', 'ã': 'a', 'â': 'a', 'ä': 'a',
            'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
            'í': 'i', 'ì': 'i', 'î': 'i', 'ï': 'i',
            'ó': 'o', 'ò': 'o', 'õ': 'o', 'ô': 'o', 'ö': 'o',
            'ú': 'u', 'ù': 'u', 'û': 'u', 'ü': 'u',
            'ç': 'c', 'ñ': 'n'
        }
        result = str(text)
        for k, v in replacements.items():
            result = result.replace(k, v).replace(k.upper(), v.upper())
        return result

def mask_string(text, show_first=2, show_last=2, mask_char="*"):
    """
    Mascara parte de uma string
    
    Args:
        text: Texto original
        show_first: Número de caracteres para mostrar no início
        show_last: Número de caracteres para mostrar no fim
        mask_char: Caractere de máscara
    
    Returns:
        str: Texto mascarado
    """
    if not text:
        return ""
    
    if len(text) <= show_first + show_last:
        return text
    
    masked = text[:show_first]
    masked += mask_char * (len(text) - show_first - show_last)
    masked += text[-show_last:]
    
    return masked