"""
Constantes do Sistema - Valores fixos usados em todo o projeto
"""
from enum import Enum

# ====================== CATEGORIAS ======================
CATEGORIAS_RECEITA = [
    "💼 Salário",
    "📝 Freelance",
    "📈 Investimentos",
    "🏦 Rendimentos",
    "🎁 Presentes",
    "💸 Extra",
    "🎓 Bolsa",
    "💰 Reembolso",
    "🏆 Bônus",
    "📊 Dividendos",
    "🏠 Aluguel Recebido",
    "💵 Vendas",
    "🎨 Serviços",
    "🌐 Online",
    "📦 Produtos",
    "🏪 Comércio",
    "🎯 Premiação",
    "💶 Câmbio",
    "📈 Crypto",
    "🏦 Juros",
    "🎰 Outros"
]

CATEGORIAS_DESPESA = [
    "🏠 Moradia",
    "🍽️ Alimentação",
    "🚗 Transporte",
    "🎬 Lazer",
    "🏥 Saúde",
    "📚 Educação",
    "🛍️ Compras",
    "📱 Serviços",
    "💳 Contas",
    "🏦 Impostos",
    "🐶 Pets",
    "👕 Vestuário",
    "💇 Beleza",
    "🏋️ Academia",
    "✈️ Viagem",
    "🎄 Presentes",
    "📞 Comunicação",
    "⚡ Energia",
    "💧 Água",
    "📡 Internet",
    "📺 Streaming",
    "📱 Celular",
    "🏥 Plano Saúde",
    "🚌 Transporte Público",
    "⛽ Combustível",
    "🍔 Delivery",
    "☕ Café",
    "🎮 Games",
    "📖 Livros",
    "🎵 Música",
    "🏀 Esportes",
    "🎭 Cultura",
    "👶 Filhos",
    "👴 Idosos",
    "🏡 Manutenção",
    "🔧 Reparos",
    "🧹 Limpeza",
    "🏥 Farmácia",
    "🦷 Dentista",
    "👓 Óculos",
    "💍 Joias",
    "📱 Eletrônicos",
    "💻 Computador",
    "📷 Fotografia",
    "🎥 Vídeo",
    "🎤 Música",
    "🎨 Arte",
    "🍷 Vinhos",
    "🚬 Tabaco",
    "🎲 Apostas",
    "🎰 Cassino",
    "📰 Assinaturas",
    "💳 Taxas",
    "🏦 Juros",
    "🎯 Outros"
]

# ====================== MESES E DIAS ======================
MESES_NOMES = [
    "Janeiro", "Fevereiro", "Março", "Abril",
    "Maio", "Junho", "Julho", "Agosto",
    "Setembro", "Outubro", "Novembro", "Dezembro"
]

MESES_ABREV = [
    "Jan", "Fev", "Mar", "Abr",
    "Mai", "Jun", "Jul", "Ago",
    "Set", "Out", "Nov", "Dez"
]

DIAS_SEMANA = [
    "Segunda-feira", "Terça-feira", "Quarta-feira",
    "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"
]

DIAS_SEMANA_ABREV = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]

# ====================== LIMITES ======================
LIMITE_VALOR_MINIMO = 0.01
LIMITE_VALOR_MAXIMO = 1_000_000_000  # 1 Bilhão
LIMITE_DESCRICAO_MINIMO = 1
LIMITE_DESCRICAO_MAXIMO = 200
LIMITE_META_VALOR_MINIMO = 10
LIMITE_META_VALOR_MAXIMO = 100_000_000  # 100 Milhões
LIMITE_META_PRAZO_MAXIMO = 3650  # 10 anos em dias

# ====================== CORES ======================
COLORS = {
    # Cores principais
    'primary': '#4CAF50',
    'secondary': '#2196F3',
    'success': '#2ecc71',
    'danger': '#e74c3c',
    'warning': '#f39c12',
    'info': '#3498db',
    'dark': '#2c3e50',
    'light': '#ecf0f1',
    
    # Categorias de gastos
    'moradia': '#e74c3c',
    'alimentacao': '#f39c12',
    'transporte': '#3498db',
    'lazer': '#9b59b6',
    'saude': '#1abc9c',
    'educacao': '#e67e22',
    'compras': '#e84393',
    'servicos': '#95a5a6',
    
    # Status
    'positive': '#2ecc71',
    'negative': '#e74c3c',
    'neutral': '#95a5a6',
    
    # Fundos
    'background_dark': '#2c3e50',
    'background_light': '#ecf0f1',
    'card_background': '#ffffff',
    'sidebar_background': '#f8f9fa'
}

# ====================== ÍCONES ======================
ICONS = {
    # Navegação
    'dashboard': '📊',
    'transactions': '💰',
    'reports': '📈',
    'insights': '🤖',
    'settings': '⚙️',
    'chat': '💬',
    'goals': '🎯',
    
    # Ações
    'add': '➕',
    'edit': '✏️',
    'delete': '🗑️',
    'save': '💾',
    'cancel': '❌',
    'search': '🔍',
    'filter': '🔧',
    'export': '📤',
    'import': '📥',
    'backup': '💿',
    'restore': '🔄',
    
    # Status
    'success': '✅',
    'error': '❌',
    'warning': '⚠️',
    'info': 'ℹ️',
    'pending': '⏳',
    'completed': '🎉',
    
    # Finanças
    'income': '💰',
    'expense': '📤',
    'balance': '💵',
    'savings': '💾',
    'investment': '📈',
    'debt': '💳',
    'credit': '💳',
    'cash': '💵',
    'bill': '📄',
    'tax': '🏦',
    
    # Categorias
    'food': '🍽️',
    'housing': '🏠',
    'transport': '🚗',
    'health': '🏥',
    'education': '📚',
    'entertainment': '🎬',
    'shopping': '🛍️',
    'services': '📱',
    'salary': '💼',
    'freelance': '✏️',
    'investment_icon': '📊',
    'gift': '🎁',
    'travel': '✈️',
    'pet': '🐶',
    'clothing': '👕',
    'beauty': '💇',
    'gym': '🏋️',
    'streaming': '📺',
    'mobile': '📱',
    'internet': '📡',
    'energy': '⚡',
    'water': '💧',
    'gas': '🔥',
    
    # Alertas
    'alert': '🔔',
    'reminder': '⏰',
    'urgent': '🚨',
    'tip': '💡',
    
    # Misc
    'calendar': '📅',
    'clock': '🕐',
    'location': '📍',
    'link': '🔗',
    'lock': '🔒',
    'unlock': '🔓',
    'star': '⭐',
    'heart': '❤️',
    'thumbs_up': '👍',
    'thumbs_down': '👎'
}

# ====================== TIPOS DE TRANSAÇÃO ======================
class TipoTransacao(Enum):
    """Tipos de transação financeira"""
    RECEITA = "receita"
    DESPESA = "despesa"
    TRANSFERENCIA = "transferencia"
    INVESTIMENTO = "investimento"
    
    @classmethod
    def choices(cls):
        return [(item.value, item.name) for item in cls]

class StatusTransacao(Enum):
    """Status da transação"""
    PENDENTE = "pendente"
    CONFIRMADA = "confirmada"
    CANCELADA = "cancelada"
    AGENDADA = "agendada"
    
    @classmethod
    def choices(cls):
        return [(item.value, item.name) for item in cls]

class Periodicidade(Enum):
    """Periodicidade de transações recorrentes"""
    DIARIA = "diaria"
    SEMANAL = "semanal"
    QUINZENAL = "quinzenal"
    MENSAL = "mensal"
    BIMESTRAL = "bimestral"
    TRIMESTRAL = "trimestral"
    SEMESTRAL = "semestral"
    ANUAL = "anual"
    
    @classmethod
    def choices(cls):
        return [(item.value, item.name) for item in cls]

# ====================== CONFIGURAÇÕES DE RELATÓRIO ======================
RELATORIO_TIPOS = {
    'mensal': 'Relatório Mensal',
    'anual': 'Relatório Anual',
    'categoria': 'Relatório por Categoria',
    'comparativo': 'Relatório Comparativo',
    'detalhado': 'Relatório Detalhado'
}

RELATORIO_FORMATOS = {
    'csv': 'CSV',
    'excel': 'Excel',
    'pdf': 'PDF',
    'json': 'JSON',
    'html': 'HTML'
}

# ====================== CONFIGURAÇÕES DE GRÁFICO ======================
GRAFICO_TIPOS = {
    'bar': 'Barras',
    'line': 'Linha',
    'pie': 'Pizza',
    'area': 'Área',
    'scatter': 'Dispersão',
    'histogram': 'Histograma',
    'box': 'Box Plot'
}

GRAFICO_CORES_PADRAO = [
    '#4CAF50', '#2196F3', '#9C27B0', '#FF9800', '#F44336',
    '#009688', '#795548', '#607D8B', '#E91E63', '#3F51B5'
]

# ====================== CONFIGURAÇÕES DE BACKUP ======================
BACKUP_CONFIG = {
    'max_backups': 10,
    'backup_interval_hours': 24,
    'compression': True,
    'include_logs': True,
    'include_config': True
}

# ====================== CONFIGURAÇÕES DE NOTIFICAÇÃO ======================
NOTIFICACAO_TIPOS = {
    'budget_alert': 'Alerta de Orçamento',
    'bill_reminder': 'Lembrete de Conta',
    'goal_achieved': 'Meta Alcançada',
    'anomaly_detected': 'Anomalia Detectada',
    'low_balance': 'Saldo Baixo',
    'report_ready': 'Relatório Pronto'
}

NOTIFICACAO_PRIORIDADES = {
    'high': 'Alta',
    'medium': 'Média',
    'low': 'Baixa'
}

# ====================== CONFIGURAÇÕES DE EXPORTAÇÃO ======================
EXPORT_CONFIG = {
    'csv_delimiter': ';',
    'csv_encoding': 'utf-8-sig',
    'excel_engine': 'openpyxl',
    'pdf_page_size': 'A4',
    'pdf_orientation': 'portrait'
}

# ====================== MENSAGENS DO SISTEMA ======================
MENSAGENS = {
    # Sucesso
    'save_success': 'Dados salvos com sucesso!',
    'delete_success': 'Registro removido com sucesso!',
    'update_success': 'Dados atualizados com sucesso!',
    'import_success': 'Importação realizada com sucesso!',
    'export_success': 'Exportação realizada com sucesso!',
    'backup_success': 'Backup criado com sucesso!',
    'restore_success': 'Dados restaurados com sucesso!',
    
    # Erro
    'save_error': 'Erro ao salvar dados.',
    'delete_error': 'Erro ao remover registro.',
    'update_error': 'Erro ao atualizar dados.',
    'import_error': 'Erro ao importar arquivo.',
    'export_error': 'Erro ao exportar dados.',
    'backup_error': 'Erro ao criar backup.',
    'restore_error': 'Erro ao restaurar backup.',
    
    # Validação
    'required_field': 'Campo obrigatório.',
    'invalid_value': 'Valor inválido.',
    'invalid_date': 'Data inválida.',
    'invalid_email': 'Email inválido.',
    'invalid_phone': 'Telefone inválido.',
    'value_too_high': 'Valor muito alto.',
    'value_too_low': 'Valor muito baixo.',
    
    # Confirmação
    'confirm_delete': 'Tem certeza que deseja excluir este registro?',
    'confirm_reset': 'Tem certeza que deseja resetar todos os dados? Esta ação não pode ser desfeita.',
    
    # Informação
    'no_data': 'Nenhum dado disponível.',
    'loading': 'Carregando...',
    'processing': 'Processando...',
    'wait': 'Aguarde...'
}

# ====================== CONFIGURAÇÕES DE API ======================
API_CONFIG = {
    'version': 'v1',
    'rate_limit': 100,  # Requisições por minuto
    'timeout': 30,  # Segundos
    'max_page_size': 100
}

# ====================== CONFIGURAÇÕES DE CACHE ======================
CACHE_CONFIG = {
    'memory_max_size': 100,
    'memory_ttl': 300,  # Segundos
    'disk_ttl': 3600,  # Segundos
    'disk_path': '.cache'
}

# ====================== CONFIGURAÇÕES DE LOG ======================
LOG_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'date_format': '%Y-%m-%d %H:%M:%S',
    'max_bytes': 10 * 1024 * 1024,  # 10MB
    'backup_count': 5,
    'log_dir': 'logs'
}

# ====================== CONFIGURAÇÕES DE SEGURANÇA ======================
SECURITY_CONFIG = {
    'min_password_length': 6,
    'session_timeout': 3600,  # Segundos
    'max_login_attempts': 5,
    'lockout_time': 300,  # Segundos
    'encryption_key_env': 'ADAPTFIN_KEY'
}

# ====================== CONFIGURAÇÕES DE UI ======================
UI_CONFIG = {
    'theme': 'light',
    'sidebar_state': 'expanded',
    'default_page_size': 25,
    'date_format': '%d/%m/%Y',
    'datetime_format': '%d/%m/%Y %H:%M:%S',
    'currency_symbol': 'R$',
    'decimal_places': 2,
    'thousand_separator': '.',
    'decimal_separator': ','
}

# ====================== FUNÇÕES AUXILIARES ======================
def get_categoria_por_valor(valor):
    """Retorna categoria baseada no valor (positivo=receita, negativo=despesa)"""
    return CATEGORIAS_RECEITA if valor >= 0 else CATEGORIAS_DESPESA

def get_cor_por_valor(valor):
    """Retorna cor baseada no valor"""
    return COLORS['positive'] if valor >= 0 else COLORS['negative']

def get_icone_por_categoria(categoria):
    """Retorna ícone baseado na categoria"""
    for cat in CATEGORIAS_DESPESA:
        if categoria in cat:
            return cat.split(' ')[0]
    for cat in CATEGORIAS_RECEITA:
        if categoria in cat:
            return cat.split(' ')[0]
    return ICONS.get('balance', '💰')

def get_nome_mes(mes_numero, abreviado=False):
    """Retorna nome do mês pelo número"""
    if 1 <= mes_numero <= 12:
        return MESES_ABREV[mes_numero - 1] if abreviado else MESES_NOMES[mes_numero - 1]
    return "Inválido"

def get_nome_dia(dia_numero, abreviado=False):
    """Retorna nome do dia da semana pelo número (0=segunda)"""
    if 0 <= dia_numero <= 6:
        return DIAS_SEMANA_ABREV[dia_numero] if abreviado else DIAS_SEMANA[dia_numero]
    return "Inválido"

def get_mes_atual():
    """Retorna mês atual (número e nome)"""
    from datetime import datetime
    mes_num = datetime.now().month
    return mes_num, MESES_NOMES[mes_num - 1]

def get_ano_atual():
    """Retorna ano atual"""
    from datetime import datetime
    return datetime.now().year