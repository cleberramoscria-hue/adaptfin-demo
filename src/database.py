"""
Database Manager - SQLite Local (Simplificado)
"""
import pandas as pd
import sqlite3
import os
from datetime import datetime
import uuid

class DatabaseManager:
    """Gerencia banco de dados SQLite local"""
    
    def __init__(self, db_path="data/adaptfin.db"):
        self.db_path = db_path
        # Criar diretório se não existir
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_local_db()
    
    def _init_local_db(self):
        """Inicializa banco de dados SQLite local"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabela de transações
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transacoes (
                id TEXT PRIMARY KEY,
                descricao TEXT NOT NULL,
                valor REAL NOT NULL,
                categoria TEXT,
                data TEXT NOT NULL,
                status TEXT DEFAULT 'Pendente',
                tipo TEXT,
                recorrente INTEGER DEFAULT 0,
                grupo_recorrente TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabela de configurações
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS configuracoes (
                chave TEXT PRIMARY KEY,
                valor TEXT,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabela de metas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS metas (
                id TEXT PRIMARY KEY,
                nome TEXT NOT NULL,
                valor_alvo REAL NOT NULL,
                valor_atual REAL DEFAULT 0,
                prazo TEXT,
                aporte_mensal REAL DEFAULT 0,
                status TEXT DEFAULT 'Ativa',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def salvar_transacao_local(self, transacao_dict):
        """Salva uma transação no banco local"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        transacao_id = transacao_dict.get('id', str(uuid.uuid4())[:8])
        descricao = transacao_dict.get('descricao', '')
        valor = float(transacao_dict.get('valor', 0))
        categoria = transacao_dict.get('categoria', 'Outros')
        data = transacao_dict.get('data', datetime.now().strftime('%Y-%m-%d'))
        status = transacao_dict.get('status', 'Pendente')
        tipo = transacao_dict.get('tipo', 'receita' if valor > 0 else 'despesa')
        recorrente = int(transacao_dict.get('recorrente', 0))
        grupo_recorrente = transacao_dict.get('grupo_recorrente', None)
        
        # Verificar se já existe
        cursor.execute("SELECT id FROM transacoes WHERE id = ?", (transacao_id,))
        existe = cursor.fetchone()
        
        if existe:
            cursor.execute("""
                UPDATE transacoes 
                SET descricao = ?, valor = ?, categoria = ?, data = ?, 
                    status = ?, tipo = ?, recorrente = ?, grupo_recorrente = ?,
                    updated_at = datetime('now')
                WHERE id = ?
            """, (descricao, valor, categoria, data, status, tipo, recorrente, grupo_recorrente, transacao_id))
        else:
            cursor.execute("""
                INSERT INTO transacoes 
                (id, descricao, valor, categoria, data, status, tipo, recorrente, grupo_recorrente, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
            """, (transacao_id, descricao, valor, categoria, data, status, tipo, recorrente, grupo_recorrente))
        
        conn.commit()
        conn.close()
        return True
    
    def carregar_transacoes_local(self, filtros=None):
        """Carrega transações do banco local"""
        conn = sqlite3.connect(self.db_path)
        
        query = "SELECT * FROM transacoes ORDER BY data DESC"
        
        if filtros:
            conditions = []
            if filtros.get('data_inicio'):
                conditions.append(f"data >= '{filtros['data_inicio']}'")
            if filtros.get('data_fim'):
                conditions.append(f"data <= '{filtros['data_fim']}'")
            if filtros.get('categoria'):
                conditions.append(f"categoria = '{filtros['categoria']}'")
            if filtros.get('status'):
                conditions.append(f"status = '{filtros['status']}'")
            if filtros.get('tipo'):
                conditions.append(f"tipo = '{filtros['tipo']}'")
            
            if conditions:
                query = query.replace("ORDER BY data DESC", "")
                query += " WHERE " + " AND ".join(conditions) + " ORDER BY data DESC"
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        # Renomear colunas para o padrão do app
        if not df.empty:
            mapeamento = {
                'descricao': 'Descrição',
                'valor': 'Valor',
                'categoria': 'Categoria',
                'data': 'Data',
                'status': 'Status',
                'id': 'id',
                'tipo': 'Tipo',
                'recorrente': 'Recorrente'
            }
            for col_orig, col_dest in mapeamento.items():
                if col_orig in df.columns:
                    df = df.rename(columns={col_orig: col_dest})
        
        return df
    
    def estatisticas(self):
        """Retorna estatísticas do banco"""
        conn = sqlite3.connect(self.db_path)
        
        stats = {}
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM transacoes")
        stats['total_transacoes'] = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT SUM(valor) FROM transacoes WHERE valor > 0")
        stats['total_receitas'] = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT SUM(valor) FROM transacoes WHERE valor < 0")
        stats['total_despesas'] = abs(cursor.fetchone()[0] or 0)
        
        conn.close()
        return stats
    
    def fazer_backup(self):
        """Faz backup do banco local"""
        import shutil
        backup_dir = "data/backups"
        os.makedirs(backup_dir, exist_ok=True)
        
        backup_path = os.path.join(backup_dir, f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")
        shutil.copy2(self.db_path, backup_path)
        
        # Limpar backups antigos (manter últimos 10)
        backups = sorted([f for f in os.listdir(backup_dir) if f.endswith('.db')])
        for old_backup in backups[:-10]:
            try:
                os.remove(os.path.join(backup_dir, old_backup))
            except:
                pass
        
        return backup_path