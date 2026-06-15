"""
Utilitários de Validação - Validação de dados de entrada
"""
import re
from datetime import datetime, date

def validate_email(email):
    """
    Valida formato de email usando regex
    
    Args:
        email: String do email
    
    Returns:
        tuple (is_valid, message)
    """
    if not email:
        return False, "Email não pode estar vazio"
    
    # Regex simples para validação de email
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(pattern, email):
        return True, "Email válido"
    return False, "Email inválido"

def validate_phone(phone):
    """
    Valida formato de telefone brasileiro
    
    Args:
        phone: String do telefone
    
    Returns:
        tuple (is_valid, message)
    """
    if not phone:
        return False, "Telefone não pode estar vazio"
    
    # Remove caracteres não numéricos
    phone_clean = re.sub(r'\D', '', str(phone))
    
    if len(phone_clean) == 10:
        return True, "Telefone válido"
    elif len(phone_clean) == 11:
        return True, "Celular válido"
    else:
        return False, "Telefone deve ter 10 ou 11 dígitos"

def validate_cpf(cpf):
    """
    Valida CPF brasileiro
    
    Args:
        cpf: String do CPF
    
    Returns:
        tuple (is_valid, message)
    """
    cpf = re.sub(r'\D', '', str(cpf))
    
    if len(cpf) != 11:
        return False, "CPF deve ter 11 dígitos"
    
    # Verifica dígitos repetidos
    if cpf == cpf[0] * 11:
        return False, "CPF inválido"
    
    # Valida primeiro dígito
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    digito = 11 - (soma % 11)
    if digito >= 10:
        digito = 0
    
    if digito != int(cpf[9]):
        return False, "CPF inválido"
    
    # Valida segundo dígito
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    digito = 11 - (soma % 11)
    if digito >= 10:
        digito = 0
    
    if digito != int(cpf[10]):
        return False, "CPF inválido"
    
    return True, "CPF válido"

def validate_cnpj(cnpj):
    """
    Valida CNPJ brasileiro
    
    Args:
        cnpj: String do CNPJ
    
    Returns:
        tuple (is_valid, message)
    """
    cnpj = re.sub(r'\D', '', str(cnpj))
    
    if len(cnpj) != 14:
        return False, "CNPJ deve ter 14 dígitos"
    
    # Verifica dígitos repetidos
    if cnpj == cnpj[0] * 14:
        return False, "CNPJ inválido"
    
    # Valida primeiro dígito
    pesos = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma = sum(int(cnpj[i]) * pesos[i] for i in range(12))
    digito = 11 - (soma % 11)
    if digito >= 10:
        digito = 0
    
    if digito != int(cnpj[12]):
        return False, "CNPJ inválido"
    
    # Valida segundo dígito
    pesos = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma = sum(int(cnpj[i]) * pesos[i] for i in range(13))
    digito = 11 - (soma % 11)
    if digito >= 10:
        digito = 0
    
    if digito != int(cnpj[13]):
        return False, "CNPJ inválido"
    
    return True, "CNPJ válido"

def validate_date(date_string, format="%Y-%m-%d"):
    """
    Valida se string é uma data válida
    
    Args:
        date_string: String da data
        format: Formato esperado
    
    Returns:
        tuple (is_valid, message, date_object)
    """
    if not date_string:
        return False, "Data não pode estar vazia", None
    
    try:
        parsed = datetime.strptime(date_string, format).date()
        return True, "Data válida", parsed
    except ValueError:
        return False, f"Data deve estar no formato {format}", None

def validate_value(value, min_value=0, max_value=1000000, field_name="Valor"):
    """
    Valida valor numérico
    
    Args:
        value: Valor a validar
        min_value: Valor mínimo permitido
        max_value: Valor máximo permitido
        field_name: Nome do campo para mensagem
    
    Returns:
        tuple (is_valid, message)
    """
    if value is None:
        return False, f"{field_name} não pode estar vazio"
    
    try:
        value_float = float(value)
        
        if value_float < min_value:
            return False, f"{field_name} deve ser maior ou igual a {min_value}"
        
        if value_float > max_value:
            return False, f"{field_name} deve ser menor ou igual a {max_value}"
        
        return True, f"{field_name} válido"
    except (ValueError, TypeError):
        return False, f"{field_name} deve ser um número válido"

def validate_description(description, max_length=100, min_length=1):
    """
    Valida descrição de transação
    
    Args:
        description: Texto da descrição
        max_length: Tamanho máximo
        min_length: Tamanho mínimo
    
    Returns:
        tuple (is_valid, message)
    """
    if not description:
        return False, "Descrição não pode estar vazia"
    
    description = str(description).strip()
    
    if len(description) < min_length:
        return False, f"Descrição deve ter pelo menos {min_length} caracteres"
    
    if len(description) > max_length:
        return False, f"Descrição deve ter no máximo {max_length} caracteres"
    
    return True, "Descrição válida"

def sanitize_input(text, allow_empty=False):
    """
    Sanitiza texto de entrada
    
    Args:
        text: Texto original
        allow_empty: Permitir texto vazio
    
    Returns:
        str: Texto sanitizado
    """
    if text is None:
        return "" if allow_empty else None
    
    # Remove espaços extras
    text = str(text).strip()
    
    # Remove caracteres especiais perigosos
    text = re.sub(r'[<>{}()\[\]\\]', '', text)
    
    # Remove múltiplos espaços
    text = re.sub(r'\s+', ' ', text)
    
    if not text and not allow_empty:
        return None
    
    return text

def validate_password(password, min_length=6):
    """
    Valida força da senha
    
    Args:
        password: Senha
        min_length: Tamanho mínimo
    
    Returns:
        tuple (is_valid, message, strength)
    """
    if not password:
        return False, "Senha não pode estar vazia", 0
    
    if len(password) < min_length:
        return False, f"Senha deve ter pelo menos {min_length} caracteres", 0
    
    strength = 0
    
    if len(password) >= 8:
        strength += 1
    
    if re.search(r'[A-Z]', password):
        strength += 1
    
    if re.search(r'[a-z]', password):
        strength += 1
    
    if re.search(r'\d', password):
        strength += 1
    
    if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        strength += 1
    
    if strength >= 4:
        return True, "Senha forte", strength
    elif strength >= 2:
        return True, "Senha média", strength
    else:
        return False, "Senha fraca", strength

def validate_url(url):
    """
    Valida formato de URL
    
    Args:
        url: String da URL
    
    Returns:
        tuple (is_valid, message)
    """
    if not url:
        return False, "URL não pode estar vazia"
    
    pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    if pattern.match(url):
        return True, "URL válida"
    return False, "URL inválida"

def validate_date_range(start_date, end_date):
    """
    Valida se o intervalo de datas é válido
    
    Args:
        start_date: Data inicial
        end_date: Data final
    
    Returns:
        tuple (is_valid, message)
    """
    if start_date is None or end_date is None:
        return False, "Datas não podem estar vazias"
    
    if start_date > end_date:
        return False, "Data inicial não pode ser maior que data final"
    
    return True, "Intervalo de datas válido"