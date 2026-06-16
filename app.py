"""
AdaptFin - Assistente Financeiro Adaptativo
Versão 2.0.0
"""
import streamlit as st
import pandas as pd
import sys
import os
import uuid
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database import DatabaseManager
from src.shared import formatar_moeda, carregar_todas_transacoes
from utils.theme_utils import aplicar_tema_global

# ====================== CONFIGURAÇÃO ======================
st.set_page_config(
    page_title="AdaptFin",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ====================== DADOS DE DEMONSTRAÇÃO (Junho 2025 - Junho 2026) ======================
def carregar_dados_completos():
    """Carrega dados de Junho 2025 a Junho 2026 com cenários variados"""
    
    dados = []
    
    # ==================== JUNHO 2025 (Mês Normal) ====================
    dados.extend([
        {"Data": "2025-06-05", "Descricao": "Salário Junho", "Valor": 5500.00, "Categoria": "Renda"},
        {"Data": "2025-06-10", "Descricao": "Aluguel", "Valor": -1850.00, "Categoria": "Moradia"},
        {"Data": "2025-06-12", "Descricao": "Supermercado", "Valor": -650.00, "Categoria": "Alimentacao"},
        {"Data": "2025-06-14", "Descricao": "Netflix", "Valor": -45.90, "Categoria": "Servicos"},
        {"Data": "2025-06-14", "Descricao": "Internet", "Valor": -120.00, "Categoria": "Servicos"},
        {"Data": "2025-06-14", "Descricao": "Energia", "Valor": -160.00, "Categoria": "Moradia"},
        {"Data": "2025-06-15", "Descricao": "Agua", "Valor": -80.00, "Categoria": "Moradia"},
        {"Data": "2025-06-18", "Descricao": "Consulta Médica", "Valor": -250.00, "Categoria": "Saude"},
        {"Data": "2025-06-20", "Descricao": "Ifood", "Valor": -140.00, "Categoria": "Alimentacao"},
        {"Data": "2025-06-22", "Descricao": "Uber", "Valor": -90.00, "Categoria": "Transporte"},
        {"Data": "2025-06-25", "Descricao": "Academia", "Valor": -110.00, "Categoria": "Saude"},
        {"Data": "2025-06-28", "Descricao": "Farmácia", "Valor": -65.00, "Categoria": "Saude"},
        {"Data": "2025-06-30", "Descricao": "Cinema", "Valor": -70.00, "Categoria": "Lazer"},
    ])
    
    # ==================== JULHO 2025 (Festas e Gastos Sociais) ====================
    dados.extend([
        {"Data": "2025-07-05", "Descricao": "Salário Julho", "Valor": 5500.00, "Categoria": "Renda"},
        {"Data": "2025-07-10", "Descricao": "Aluguel", "Valor": -1850.00, "Categoria": "Moradia"},
        {"Data": "2025-07-12", "Descricao": "Supermercado", "Valor": -750.00, "Categoria": "Alimentacao"},
        {"Data": "2025-07-14", "Descricao": "Netflix", "Valor": -45.90, "Categoria": "Servicos"},
        {"Data": "2025-07-14", "Descricao": "Internet", "Valor": -120.00, "Categoria": "Servicos"},
        {"Data": "2025-07-14", "Descricao": "Energia", "Valor": -210.00, "Categoria": "Moradia"},
        {"Data": "2025-07-15", "Descricao": "Agua", "Valor": -80.00, "Categoria": "Moradia"},
        {"Data": "2025-07-18", "Descricao": "Festa Julina", "Valor": -500.00, "Categoria": "Lazer"},
        {"Data": "2025-07-18", "Descricao": "Presente Amigo", "Valor": -150.00, "Categoria": "Outros"},
        {"Data": "2025-07-20", "Descricao": "Ifood", "Valor": -220.00, "Categoria": "Alimentacao"},
        {"Data": "2025-07-22", "Descricao": "Uber", "Valor": -120.00, "Categoria": "Transporte"},
        {"Data": "2025-07-25", "Descricao": "Academia", "Valor": -110.00, "Categoria": "Saude"},
        {"Data": "2025-07-28", "Descricao": "Farmácia", "Valor": -45.00, "Categoria": "Saude"},
        {"Data": "2025-07-30", "Descricao": "Restaurante", "Valor": -180.00, "Categoria": "Alimentacao"},
    ])
    
    # ==================== AGOSTO 2025 (Compras e Economia) ====================
    dados.extend([
        {"Data": "2025-08-05", "Descricao": "Salário Agosto", "Valor": 5500.00, "Categoria": "Renda"},
        {"Data": "2025-08-10", "Descricao": "Aluguel", "Valor": -1850.00, "Categoria": "Moradia"},
        {"Data": "2025-08-12", "Descricao": "Supermercado", "Valor": -620.00, "Categoria": "Alimentacao"},
        {"Data": "2025-08-14", "Descricao": "Netflix", "Valor": -45.90, "Categoria": "Servicos"},
        {"Data": "2025-08-14", "Descricao": "Internet", "Valor": -120.00, "Categoria": "Servicos"},
        {"Data": "2025-08-14", "Descricao": "Energia", "Valor": -155.00, "Categoria": "Moradia"},
        {"Data": "2025-08-15", "Descricao": "Agua", "Valor": -80.00, "Categoria": "Moradia"},
        {"Data": "2025-08-18", "Descricao": "Compras Roupa", "Valor": -350.00, "Categoria": "Outros"},
        {"Data": "2025-08-20", "Descricao": "Ifood", "Valor": -130.00, "Categoria": "Alimentacao"},
        {"Data": "2025-08-22", "Descricao": "Uber", "Valor": -85.00, "Categoria": "Transporte"},
        {"Data": "2025-08-25", "Descricao": "Academia", "Valor": -110.00, "Categoria": "Saude"},
        {"Data": "2025-08-28", "Descricao": "Farmácia", "Valor": -50.00, "Categoria": "Saude"},
        {"Data": "2025-08-30", "Descricao": "Show", "Valor": -200.00, "Categoria": "Lazer"},
    ])
    
    # ==================== SETEMBRO 2025 (Educação) ====================
    dados.extend([
        {"Data": "2025-09-05", "Descricao": "Salário Setembro", "Valor": 5500.00, "Categoria": "Renda"},
        {"Data": "2025-09-10", "Descricao": "Aluguel", "Valor": -1850.00, "Categoria": "Moradia"},
        {"Data": "2025-09-12", "Descricao": "Supermercado", "Valor": -680.00, "Categoria": "Alimentacao"},
        {"Data": "2025-09-14", "Descricao": "Netflix", "Valor": -45.90, "Categoria": "Servicos"},
        {"Data": "2025-09-14", "Descricao": "Internet", "Valor": -120.00, "Categoria": "Servicos"},
        {"Data": "2025-09-14", "Descricao": "Energia", "Valor": -175.00, "Categoria": "Moradia"},
        {"Data": "2025-09-15", "Descricao": "Agua", "Valor": -80.00, "Categoria": "Moradia"},
        {"Data": "2025-09-18", "Descricao": "Curso Online", "Valor": -350.00, "Categoria": "Educacao"},
        {"Data": "2025-09-18", "Descricao": "Livros", "Valor": -150.00, "Categoria": "Educacao"},
        {"Data": "2025-09-20", "Descricao": "Ifood", "Valor": -150.00, "Categoria": "Alimentacao"},
        {"Data": "2025-09-22", "Descricao": "Uber", "Valor": -95.00, "Categoria": "Transporte"},
        {"Data": "2025-09-25", "Descricao": "Academia", "Valor": -110.00, "Categoria": "Saude"},
        {"Data": "2025-09-28", "Descricao": "Farmácia", "Valor": -55.00, "Categoria": "Saude"},
    ])
    
    # ==================== OUTUBRO 2025 (Aniversário) ====================
    dados.extend([
        {"Data": "2025-10-05", "Descricao": "Salário Outubro", "Valor": 5500.00, "Categoria": "Renda"},
        {"Data": "2025-10-10", "Descricao": "Aluguel", "Valor": -1850.00, "Categoria": "Moradia"},
        {"Data": "2025-10-12", "Descricao": "Supermercado", "Valor": -750.00, "Categoria": "Alimentacao"},
        {"Data": "2025-10-14", "Descricao": "Netflix", "Valor": -45.90, "Categoria": "Servicos"},
        {"Data": "2025-10-14", "Descricao": "Internet", "Valor": -120.00, "Categoria": "Servicos"},
        {"Data": "2025-10-14", "Descricao": "Energia", "Valor": -190.00, "Categoria": "Moradia"},
        {"Data": "2025-10-15", "Descricao": "Agua", "Valor": -80.00, "Categoria": "Moradia"},
        {"Data": "2025-10-18", "Descricao": "Festa Aniversário", "Valor": -600.00, "Categoria": "Lazer"},
        {"Data": "2025-10-18", "Descricao": "Presentes", "Valor": -250.00, "Categoria": "Outros"},
        {"Data": "2025-10-20", "Descricao": "Ifood", "Valor": -200.00, "Categoria": "Alimentacao"},
        {"Data": "2025-10-22", "Descricao": "Uber", "Valor": -110.00, "Categoria": "Transporte"},
        {"Data": "2025-10-25", "Descricao": "Academia", "Valor": -110.00, "Categoria": "Saude"},
        {"Data": "2025-10-28", "Descricao": "Farmácia", "Valor": -70.00, "Categoria": "Saude"},
    ])
    
    # ==================== NOVEMBRO 2025 (Black Friday) ====================
    dados.extend([
        {"Data": "2025-11-05", "Descricao": "Salário Novembro", "Valor": 5500.00, "Categoria": "Renda"},
        {"Data": "2025-11-10", "Descricao": "Aluguel", "Valor": -1850.00, "Categoria": "Moradia"},
        {"Data": "2025-11-12", "Descricao": "Supermercado", "Valor": -800.00, "Categoria": "Alimentacao"},
        {"Data": "2025-11-14", "Descricao": "Netflix", "Valor": -45.90, "Categoria": "Servicos"},
        {"Data": "2025-11-14", "Descricao": "Internet", "Valor": -120.00, "Categoria": "Servicos"},
        {"Data": "2025-11-14", "Descricao": "Energia", "Valor": -200.00, "Categoria": "Moradia"},
        {"Data": "2025-11-15", "Descricao": "Agua", "Valor": -80.00, "Categoria": "Moradia"},
        {"Data": "2025-11-18", "Descricao": "Black Friday - TV", "Valor": -1200.00, "Categoria": "Outros"},
        {"Data": "2025-11-18", "Descricao": "Black Friday - Roupas", "Valor": -600.00, "Categoria": "Outros"},
        {"Data": "2025-11-20", "Descricao": "Ifood", "Valor": -250.00, "Categoria": "Alimentacao"},
        {"Data": "2025-11-22", "Descricao": "Uber", "Valor": -150.00, "Categoria": "Transporte"},
        {"Data": "2025-11-25", "Descricao": "Academia", "Valor": -110.00, "Categoria": "Saude"},
        {"Data": "2025-11-28", "Descricao": "Farmácia", "Valor": -75.00, "Categoria": "Saude"},
    ])
    
    # ==================== DEZEMBRO 2025 (Natal) ====================
    dados.extend([
        {"Data": "2025-12-05", "Descricao": "Salário Dezembro", "Valor": 5500.00, "Categoria": "Renda"},
        {"Data": "2025-12-05", "Descricao": "13º Salário", "Valor": 5500.00, "Categoria": "Renda"},
        {"Data": "2025-12-10", "Descricao": "Aluguel", "Valor": -1850.00, "Categoria": "Moradia"},
        {"Data": "2025-12-12", "Descricao": "Supermercado", "Valor": -900.00, "Categoria": "Alimentacao"},
        {"Data": "2025-12-14", "Descricao": "Netflix", "Valor": -45.90, "Categoria": "Servicos"},
        {"Data": "2025-12-14", "Descricao": "Internet", "Valor": -120.00, "Categoria": "Servicos"},
        {"Data": "2025-12-14", "Descricao": "Energia", "Valor": -230.00, "Categoria": "Moradia"},
        {"Data": "2025-12-15", "Descricao": "Agua", "Valor": -80.00, "Categoria": "Moradia"},
        {"Data": "2025-12-18", "Descricao": "Ceia Natal", "Valor": -800.00, "Categoria": "Alimentacao"},
        {"Data": "2025-12-18", "Descricao": "Presentes Natal", "Valor": -1200.00, "Categoria": "Outros"},
        {"Data": "2025-12-20", "Descricao": "Viagem Reveillon", "Valor": -2000.00, "Categoria": "Lazer"},
        {"Data": "2025-12-22", "Descricao": "Uber", "Valor": -200.00, "Categoria": "Transporte"},
        {"Data": "2025-12-25", "Descricao": "Academia", "Valor": -110.00, "Categoria": "Saude"},
        {"Data": "2025-12-28", "Descricao": "Farmácia", "Valor": -85.00, "Categoria": "Saude"},
    ])
    
    # ==================== JANEIRO 2026 (Início do ano) ====================
    dados.extend([
        {"Data": "2026-01-05", "Descricao": "Salário Janeiro", "Valor": 5800.00, "Categoria": "Renda"},
        {"Data": "2026-01-08", "Descricao": "Bônus Ano Novo", "Valor": 1500.00, "Categoria": "Renda"},
        {"Data": "2026-01-10", "Descricao": "Aluguel", "Valor": -1900.00, "Categoria": "Moradia"},
        {"Data": "2026-01-12", "Descricao": "Supermercado", "Valor": -780.00, "Categoria": "Alimentacao"},
        {"Data": "2026-01-14", "Descricao": "Netflix", "Valor": -49.90, "Categoria": "Servicos"},
        {"Data": "2026-01-14", "Descricao": "Internet", "Valor": -130.00, "Categoria": "Servicos"},
        {"Data": "2026-01-14", "Descricao": "Energia", "Valor": -210.00, "Categoria": "Moradia"},
        {"Data": "2026-01-15", "Descricao": "Agua", "Valor": -85.00, "Categoria": "Moradia"},
        {"Data": "2026-01-18", "Descricao": "Uber", "Valor": -100.00, "Categoria": "Transporte"},
        {"Data": "2026-01-20", "Descricao": "Ifood", "Valor": -190.00, "Categoria": "Alimentacao"},
        {"Data": "2026-01-22", "Descricao": "Cinema", "Valor": -80.00, "Categoria": "Lazer"},
        {"Data": "2026-01-25", "Descricao": "Academia", "Valor": -120.00, "Categoria": "Saude"},
        {"Data": "2026-01-28", "Descricao": "Farmácia", "Valor": -60.00, "Categoria": "Saude"},
        {"Data": "2026-01-30", "Descricao": "Restaurante", "Valor": -160.00, "Categoria": "Alimentacao"},
        {"Data": "2026-01-31", "Descricao": "Presente", "Valor": -200.00, "Categoria": "Outros"},
    ])
    
    # ==================== FEVEREIRO 2026 (Carnaval) ====================
    dados.extend([
        {"Data": "2026-02-05", "Descricao": "Salário Fevereiro", "Valor": 5800.00, "Categoria": "Renda"},
        {"Data": "2026-02-10", "Descricao": "Aluguel", "Valor": -1900.00, "Categoria": "Moradia"},
        {"Data": "2026-02-12", "Descricao": "Supermercado", "Valor": -720.00, "Categoria": "Alimentacao"},
        {"Data": "2026-02-14", "Descricao": "Netflix", "Valor": -49.90, "Categoria": "Servicos"},
        {"Data": "2026-02-14", "Descricao": "Internet", "Valor": -130.00, "Categoria": "Servicos"},
        {"Data": "2026-02-14", "Descricao": "Energia", "Valor": -185.00, "Categoria": "Moradia"},
        {"Data": "2026-02-15", "Descricao": "Agua", "Valor": -85.00, "Categoria": "Moradia"},
        {"Data": "2026-02-18", "Descricao": "Carnaval Viagem", "Valor": -1500.00, "Categoria": "Lazer"},
        {"Data": "2026-02-18", "Descricao": "Hospedagem", "Valor": -800.00, "Categoria": "Lazer"},
        {"Data": "2026-02-20", "Descricao": "Ifood", "Valor": -230.00, "Categoria": "Alimentacao"},
        {"Data": "2026-02-22", "Descricao": "Uber", "Valor": -130.00, "Categoria": "Transporte"},
        {"Data": "2026-02-25", "Descricao": "Academia", "Valor": -120.00, "Categoria": "Saude"},
        {"Data": "2026-02-27", "Descricao": "Farmácia", "Valor": -50.00, "Categoria": "Saude"},
    ])
    
    # ==================== MARÇO 2026 (Manutenção Carro) ====================
    dados.extend([
        {"Data": "2026-03-05", "Descricao": "Salário Março", "Valor": 5800.00, "Categoria": "Renda"},
        {"Data": "2026-03-10", "Descricao": "Aluguel", "Valor": -1900.00, "Categoria": "Moradia"},
        {"Data": "2026-03-12", "Descricao": "Supermercado", "Valor": -800.00, "Categoria": "Alimentacao"},
        {"Data": "2026-03-14", "Descricao": "Netflix", "Valor": -49.90, "Categoria": "Servicos"},
        {"Data": "2026-03-14", "Descricao": "Internet", "Valor": -130.00, "Categoria": "Servicos"},
        {"Data": "2026-03-14", "Descricao": "Energia", "Valor": -220.00, "Categoria": "Moradia"},
        {"Data": "2026-03-15", "Descricao": "Agua", "Valor": -85.00, "Categoria": "Moradia"},
        {"Data": "2026-03-18", "Descricao": "Manutenção Carro", "Valor": -700.00, "Categoria": "Transporte"},
        {"Data": "2026-03-18", "Descricao": "Óleo e Filtros", "Valor": -250.00, "Categoria": "Transporte"},
        {"Data": "2026-03-20", "Descricao": "Ifood", "Valor": -160.00, "Categoria": "Alimentacao"},
        {"Data": "2026-03-22", "Descricao": "Teatro", "Valor": -200.00, "Categoria": "Lazer"},
        {"Data": "2026-03-25", "Descricao": "Academia", "Valor": -120.00, "Categoria": "Saude"},
        {"Data": "2026-03-28", "Descricao": "Farmácia", "Valor": -75.00, "Categoria": "Saude"},
    ])
    
    # ==================== ABRIL 2026 (Viagem Curta) ====================
    dados.extend([
        {"Data": "2026-04-05", "Descricao": "Salário Abril", "Valor": 5800.00, "Categoria": "Renda"},
        {"Data": "2026-04-10", "Descricao": "Aluguel", "Valor": -1900.00, "Categoria": "Moradia"},
        {"Data": "2026-04-12", "Descricao": "Supermercado", "Valor": -650.00, "Categoria": "Alimentacao"},
        {"Data": "2026-04-14", "Descricao": "Netflix", "Valor": -49.90, "Categoria": "Servicos"},
        {"Data": "2026-04-14", "Descricao": "Internet", "Valor": -130.00, "Categoria": "Servicos"},
        {"Data": "2026-04-14", "Descricao": "Energia", "Valor": -170.00, "Categoria": "Moradia"},
        {"Data": "2026-04-15", "Descricao": "Agua", "Valor": -85.00, "Categoria": "Moradia"},
        {"Data": "2026-04-18", "Descricao": "Passagem Aérea", "Valor": -600.00, "Categoria": "Transporte"},
        {"Data": "2026-04-18", "Descricao": "Hotel", "Valor": -450.00, "Categoria": "Lazer"},
        {"Data": "2026-04-20", "Descricao": "Ifood", "Valor": -130.00, "Categoria": "Alimentacao"},
        {"Data": "2026-04-22", "Descricao": "Uber", "Valor": -95.00, "Categoria": "Transporte"},
        {"Data": "2026-04-25", "Descricao": "Academia", "Valor": -120.00, "Categoria": "Saude"},
        {"Data": "2026-04-28", "Descricao": "Farmácia", "Valor": -55.00, "Categoria": "Saude"},
    ])
    
    # ==================== MAIO 2026 (Férias) ====================
    dados.extend([
        {"Data": "2026-05-05", "Descricao": "Salário Maio", "Valor": 5800.00, "Categoria": "Renda"},
        {"Data": "2026-05-10", "Descricao": "Aluguel", "Valor": -1900.00, "Categoria": "Moradia"},
        {"Data": "2026-05-12", "Descricao": "Supermercado", "Valor": -820.00, "Categoria": "Alimentacao"},
        {"Data": "2026-05-14", "Descricao": "Netflix", "Valor": -49.90, "Categoria": "Servicos"},
        {"Data": "2026-05-14", "Descricao": "Internet", "Valor": -130.00, "Categoria": "Servicos"},
        {"Data": "2026-05-14", "Descricao": "Energia", "Valor": -200.00, "Categoria": "Moradia"},
        {"Data": "2026-05-15", "Descricao": "Agua", "Valor": -85.00, "Categoria": "Moradia"},
        {"Data": "2026-05-18", "Descricao": "Viagem Internacional", "Valor": -2500.00, "Categoria": "Lazer"},
        {"Data": "2026-05-18", "Descricao": "Passagens", "Valor": -1200.00, "Categoria": "Transporte"},
        {"Data": "2026-05-20", "Descricao": "Ifood", "Valor": -300.00, "Categoria": "Alimentacao"},
        {"Data": "2026-05-22", "Descricao": "Uber", "Valor": -150.00, "Categoria": "Transporte"},
        {"Data": "2026-05-25", "Descricao": "Academia", "Valor": -120.00, "Categoria": "Saude"},
        {"Data": "2026-05-28", "Descricao": "Farmácia", "Valor": -70.00, "Categoria": "Saude"},
    ])
    
    # ==================== JUNHO 2026 (Mês de Recuperação) ====================
    dados.extend([
        {"Data": "2026-06-05", "Descricao": "Salário Junho", "Valor": 5800.00, "Categoria": "Renda"},
        {"Data": "2026-06-05", "Descricao": "Freelance Extra", "Valor": 800.00, "Categoria": "Renda"},
        {"Data": "2026-06-10", "Descricao": "Aluguel", "Valor": -1900.00, "Categoria": "Moradia"},
        {"Data": "2026-06-12", "Descricao": "Supermercado", "Valor": -680.00, "Categoria": "Alimentacao"},
        {"Data": "2026-06-14", "Descricao": "Netflix", "Valor": -49.90, "Categoria": "Servicos"},
        {"Data": "2026-06-14", "Descricao": "Internet", "Valor": -130.00, "Categoria": "Servicos"},
        {"Data": "2026-06-14", "Descricao": "Energia", "Valor": -175.00, "Categoria": "Moradia"},
        {"Data": "2026-06-15", "Descricao": "Agua", "Valor": -85.00, "Categoria": "Moradia"},
        {"Data": "2026-06-18", "Descricao": "Consulta Médica", "Valor": -350.00, "Categoria": "Saude"},
        {"Data": "2026-06-20", "Descricao": "Ifood", "Valor": -140.00, "Categoria": "Alimentacao"},
        {"Data": "2026-06-22", "Descricao": "Uber", "Valor": -100.00, "Categoria": "Transporte"},
        {"Data": "2026-06-25", "Descricao": "Academia", "Valor": -120.00, "Categoria": "Saude"},
        {"Data": "2026-06-28", "Descricao": "Farmácia", "Valor": -65.00, "Categoria": "Saude"},
        {"Data": "2026-06-30", "Descricao": "Cinema", "Valor": -80.00, "Categoria": "Lazer"},
        {"Data": "2026-06-30", "Descricao": "Investimento", "Valor": -500.00, "Categoria": "Investimento"},
    ])
    
    return pd.DataFrame(dados)

# ====================== INICIALIZAÇÃO ======================
db = DatabaseManager()

if "despesas_fixas" not in st.session_state:
    st.session_state.despesas_fixas = pd.DataFrame()
if "receitas" not in st.session_state:
    st.session_state.receitas = pd.DataFrame()
if "gastos_variaveis" not in st.session_state:
    st.session_state.gastos_variaveis = pd.DataFrame()
if "configuracoes" not in st.session_state:
    st.session_state.configuracoes = {
        "salario_mensal": 0.0,
        "limite_gastos": 0.0,
        "alertas_ativos": True,
        "ml_ativado": True,
        "tema": "Claro"
    }
if "dados_demo_carregados" not in st.session_state:
    st.session_state.dados_demo_carregados = False

# Carregar dados de demonstração se não houver dados
if st.session_state.receitas.empty and st.session_state.gastos_variaveis.empty and not st.session_state.dados_demo_carregados:
    df_completo = carregar_dados_completos()
    st.session_state.receitas = df_completo[df_completo["Valor"] > 0].copy()
    st.session_state.gastos_variaveis = df_completo[df_completo["Valor"] < 0].copy()
    # Adicionar IDs únicos
    st.session_state.receitas["id"] = [str(uuid.uuid4())[:8] for _ in range(len(st.session_state.receitas))]
    st.session_state.gastos_variaveis["id"] = [str(uuid.uuid4())[:8] for _ in range(len(st.session_state.gastos_variaveis))]
    st.session_state.dados_demo_carregados = True

# Aplicar tema GLOBALMENTE (em todas as páginas)
aplicar_tema_global()

# ====================== SIDEBAR ======================
with st.sidebar:
    st.markdown("# 🧠 AdaptFin")
    st.caption("Seu assistente financeiro")
    st.markdown("---")
    
    # Menu
    st.page_link("pages/1_🏠_Dashboard.py", label="📊 Dashboard")
    st.page_link("pages/2_💰_Transacoes.py", label="💰 Transações")
    st.page_link("pages/3_📊_Relatorios.py", label="📈 Relatórios")
    st.page_link("pages/4_🤖_Insights_ML.py", label="🤖 Insights ML")
    st.page_link("pages/5_🎯_Metas.py", label="🎯 Metas")
    st.page_link("pages/6_💬_Chat_Financeiro.py", label="💬 Chat")
    st.page_link("pages/7_⚙️_Configuracoes.py", label="⚙️ Configurações")
    