"""
Utilitários de Data - Formatação e manipulação de datas
"""
from datetime import datetime, timedelta, date
import calendar

def format_date_br(data, include_time=False):
    """
    Formata data para padrão brasileiro (dd/mm/yyyy)
    
    Args:
        data: datetime ou string
        include_time: incluir hora na formatação
    
    Returns:
        str: Data formatada
    """
    if data is None:
        return "N/A"
    
    if isinstance(data, str):
        try:
            data = datetime.fromisoformat(data)
        except:
            return data
    
    if include_time:
        return data.strftime("%d/%m/%Y %H:%M:%S")
    return data.strftime("%d/%m/%Y")

def parse_date(date_string):
    """
    Converte string para datetime tentando múltiplos formatos
    
    Args:
        date_string: String de data
    
    Returns:
        datetime ou None
    """
    formats = [
        "%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y",
        "%Y/%m/%d", "%d/%m/%y", "%Y-%m-%d %H:%M:%S"
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_string, fmt)
        except:
            continue
    
    return None

def get_current_month():
    """
    Retorna o mês atual como string
    
    Returns:
        tuple (ano, mes)
    """
    now = datetime.now()
    return now.year, now.month

def get_days_between(start_date, end_date):
    """
    Calcula número de dias entre duas datas
    
    Args:
        start_date: datetime
        end_date: datetime
    
    Returns:
        int: Número de dias
    """
    if isinstance(start_date, str):
        start_date = parse_date(start_date)
    if isinstance(end_date, str):
        end_date = parse_date(end_date)
    
    if start_date and end_date:
        return (end_date - start_date).days
    return 0

def add_months(date_obj, months):
    """
    Adiciona meses a uma data
    
    Args:
        date_obj: datetime
        months: número de meses para adicionar
    
    Returns:
        datetime: Nova data
    """
    if date_obj is None:
        return None
    
    month = date_obj.month - 1 + months
    year = date_obj.year + month // 12
    month = month % 12 + 1
    
    day = min(date_obj.day, calendar.monthrange(year, month)[1])
    
    return datetime(year, month, day)

def get_month_name(month_number, short=False):
    """
    Retorna nome do mês
    
    Args:
        month_number: 1-12
        short: nome abreviado (3 letras)
    
    Returns:
        str: Nome do mês
    """
    meses = [
        "Janeiro", "Fevereiro", "Março", "Abril",
        "Maio", "Junho", "Julho", "Agosto",
        "Setembro", "Outubro", "Novembro", "Dezembro"
    ]
    
    meses_short = [
        "Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
        "Jul", "Ago", "Set", "Out", "Nov", "Dez"
    ]
    
    if 1 <= month_number <= 12:
        return meses_short[month_number - 1] if short else meses[month_number - 1]
    return "Inválido"

def get_weekday_name(weekday_number, short=False):
    """
    Retorna nome do dia da semana
    
    Args:
        weekday_number: 0-6 (0=Segunda)
        short: nome abreviado
    
    Returns:
        str: Nome do dia
    """
    dias = [
        "Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira",
        "Sexta-feira", "Sábado", "Domingo"
    ]
    
    dias_short = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
    
    if 0 <= weekday_number <= 6:
        return dias_short[weekday_number] if short else dias[weekday_number]
    return "Inválido"

def is_weekend(date_obj):
    """Verifica se a data é fim de semana"""
    return date_obj.weekday() >= 5

def get_first_day_of_month(year, month):
    """Retorna primeiro dia do mês"""
    return datetime(year, month, 1)

def get_last_day_of_month(year, month):
    """Retorna último dia do mês"""
    last_day = calendar.monthrange(year, month)[1]
    return datetime(year, month, last_day)

def get_weeks_in_month(year, month):
    """Retorna número de semanas no mês"""
    first_day = datetime(year, month, 1)
    last_day = datetime(year, month, calendar.monthrange(year, month)[1])
    
    weeks = ((last_day - first_day).days // 7) + 1
    return weeks

def format_relative_date(date_obj):
    """
    Formata data relativa (hoje, ontem, etc)
    
    Args:
        date_obj: datetime
    
    Returns:
        str: Data relativa formatada
    """
    hoje = datetime.now().date()
    data = date_obj.date() if isinstance(date_obj, datetime) else date_obj
    
    diff = (hoje - data).days
    
    if diff == 0:
        return "Hoje"
    elif diff == 1:
        return "Ontem"
    elif 2 <= diff <= 7:
        return f"{diff} dias atrás"
    elif diff > 7:
        return format_date_br(data)
    
    return format_date_br(data)