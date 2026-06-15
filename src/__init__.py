"""
Src Module - Core modules for AdaptFin
"""
from .data_manager import DataManager
from .analyzer import process_data, categorize_transactions
from .recommendations import generate_recommendation
from .ml_engine import MLFinanceEngine

__all__ = [
    'DataManager',
    'process_data',
    'categorize_transactions', 
    'generate_recommendation',
    'MLFinanceEngine'
]