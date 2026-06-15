"""
Database Manager - SQLite (Local) + Supabase (Cloud)
"""
import pandas as pd
import sqlite3
import os
from datetime import datetime
from dotenv import load_dotenv
import uuid

# Carregar variáveis de ambiente
load_dotenv()

class DatabaseManager:
    """Gerencia conexões com banco de dados local e cloud"""
    
    def __init__(self, db_path="data/adaptfin.db"):
        self.db_path = db_path
        self.cloud_enabled = False
        self.supabase_client = None
        
        # Criar diretório se não existir
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Tentar conectar ao Supabase (cloud)
        try:
            from supabase import create_client
            supabase_url = os.getenv("SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_KEY")
            
            if supabase_url and supabase_key:
                self.supabase_client = create_client(supabase_url, supabase_key)
                self.cloud_enabled = True
                print("✅ Conexão com Supabase estabelecida!")
        except Exception as e:
            print(f"⚠️ Cloud não disponível: {e}")
        
        # Criar banco local
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
    
    # ====================== OPERAÇÕES LOCAIS (SQLite) ======================
    
    def salvar_transacao_local(self, transacao_dict):
        """Salva uma transação no banco local (recebe dicionário)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Garantir valores padrão
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
            # Atualizar
            cursor.execute("""
                UPDATE transacoes 
                SET descricao = ?, valor = ?, categoria = ?, data = ?, 
                    status = ?, tipo = ?, recorrente = ?, grupo_recorrente = ?,
                    updated_at = datetime('now')
                WHERE id = ?
            """, (descricao, valor, categoria, data, status, tipo, recorrente, grupo_recorrente, transacao_id))
        else:
            # Inserir
            cursor.execute("""
                INSERT INTO transacoes 
                (id, descricao, valor, categoria, data, status, tipo, recorrente, grupo_recorrente, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
            """, (transacao_id, descricao, valor, categoria, data, status, tipo, recorrente, grupo_recorrente))
        
        conn.commit()
        conn.close()
        return True
    
    def salvar_transacao_dataframe(self, df):
        """Salva transações a partir de um DataFrame"""
        conn = sqlite3.connect(self.db_path)
        
        # Preparar dados
        df_copy = df.copy()
        
        # Garantir colunas necessárias
        if 'id' not in df_copy.columns:
            df_copy['id'] = [str(uuid.uuid4())[:8] for _ in range(len(df_copy))]
        if 'status' not in df_copy.columns:
            df_copy['status'] = 'Pendente'
        if 'tipo' not in df_copy.columns:
            df_copy['tipo'] = df_copy['valor'].apply(lambda x: 'receita' if x > 0 else 'despesa')
        if 'recorrente' not in df_copy.columns:
            df_copy['recorrente'] = 0
        
        # Selecionar apenas colunas que existem na tabela
        colunas_tabela = ['id', 'descricao', 'valor', 'categoria', 'data', 'status', 'tipo', 'recorrente', 'grupo_recorrente']
        colunas_existentes = [col for col in colunas_tabela if col in df_copy.columns]
        
        # Salvar
        df_copy[colunas_existentes].to_sql('transacoes', conn, if_exists='append', index=False)
        conn.close()
    
    def carregar_transacoes_local(self, filtros=None):
        """Carrega transações do banco local"""
        conn = sqlite3.connect(self.db_path)
        
        query = "SELECT * FROM transacoes"
        
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
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        # Renomear colunas para o padrão do app (se necessário)
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
    
    def carregar_configuracoes(self):
        """Carrega configurações do banco"""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query("SELECT chave, valor FROM configuracoes", conn)
        conn.close()
        
        if not df.empty:
            config = {}
            for _, row in df.iterrows():
                val = row['valor']
                if val == 'True':
                    val = True
                elif val == 'False':
                    val = False
                elif val.isdigit():
                    val = int(val)
                elif val.replace('.', '').isdigit():
                    try:
                        val = float(val)
                    except:
                        pass
                config[row['chave']] = val
            return pd.DataFrame([config])
        return pd.DataFrame()
    
    def salvar_configuracoes(self, config_dict):
        """Salva configurações no banco"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for chave, valor in config_dict.items():
            cursor.execute("""
                INSERT OR REPLACE INTO configuracoes (chave, valor, updated_at)
                VALUES (?, ?, datetime('now'))
            """, (chave, str(valor)))
        
        conn.commit()
        conn.close()
    
    def excluir_transacao_local(self, id_transacao):
        """Exclui transação do banco local"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM transacoes WHERE id = ?", (id_transacao,))
        conn.commit()
        conn.close()
    
    def excluir_todas_transacoes(self):
        """Exclui todas as transações do banco"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM transacoes")
        conn.commit()
        conn.close()
    
    # ====================== OPERAÇÕES NA NUVEM (Supabase) ======================
    
    def salvar_transacao_cloud(self, transacao):
        """Salva transação na nuvem (Supabase)"""
        if not self.cloud_enabled:
            return False
        
        try:
            data = transacao.to_dict(orient='records')[0]
            self.supabase_client.table('transacoes').insert(data).execute()
            return True
        except Exception as e:
            print(f"Erro ao salvar na nuvem: {e}")
            return False
    
    def carregar_transacoes_cloud(self):
        """Carrega transações da nuvem"""
        if not self.cloud_enabled:
            return pd.DataFrame()
        
        try:
            response = self.supabase_client.table('transacoes').select('*').execute()
            return pd.DataFrame(response.data)
        except Exception as e:
            print(f"Erro ao carregar da nuvem: {e}")
            return pd.DataFrame()
    
    def sincronizar_cloud(self):
        """Sincroniza dados locais com a nuvem"""
        if not self.cloud_enabled:
            return "Cloud não configurada"
        
        try:
            dados_locais = self.carregar_transacoes_local()
            
            for _, row in dados_locais.iterrows():
                self.salvar_transacao_cloud(pd.DataFrame([row]))
            
            return "✅ Sincronização concluída!"
        except Exception as e:
            return f"❌ Erro na sincronização: {e}"
    
    # ====================== OPERAÇÕES COMBINADAS ======================
    
    def salvar_transacao(self, transacao, sincronizar=True):
        """Salva transação localmente e opcionalmente na nuvem"""
        if isinstance(transacao, pd.DataFrame):
            self.salvar_transacao_dataframe(transacao)
        else:
            self.salvar_transacao_local(transacao)
        
        if sincronizar and self.cloud_enabled:
            self.salvar_transacao_cloud(transacao)
    
    def carregar_todas_transacoes(self, origem="local"):
        """Carrega transações da origem especificada"""
        if origem == "cloud" and self.cloud_enabled:
            return self.carregar_transacoes_cloud()
        return self.carregar_transacoes_local()
    
    def fazer_backup(self):
        """Faz backup do banco local"""
        backup_path = f"data/backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        import shutil
        shutil.copy2(self.db_path, backup_path)
        return backup_path
    
    def estatisticas(self):
        """Retorna estatísticas do banco"""
        conn = sqlite3.connect(self.db_path)
        
        stats = {}
        
        # Total de transações
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM transacoes")
        stats['total_transacoes'] = cursor.fetchone()[0]
        
        # Total de receitas
        cursor.execute("SELECT SUM(valor) FROM transacoes WHERE valor > 0")
        stats['total_receitas'] = cursor.fetchone()[0] or 0
        
        # Total de despesas
        cursor.execute("SELECT SUM(valor) FROM transacoes WHERE valor < 0")
        stats['total_despesas'] = abs(cursor.fetchone()[0] or 0)
        
        conn.close()
        
        return stats