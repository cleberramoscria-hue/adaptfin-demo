"""
Serviço de Autenticação e Segurança
"""
import hashlib
import json
import os
from datetime import datetime, timedelta
import secrets

class AuthService:
    """Gerencia autenticação e segurança do usuário"""
    
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.auth_file = os.path.join(data_dir, "users.json")
        self.session_file = os.path.join(data_dir, "session.json")
        self._init_storage()
    
    def _init_storage(self):
        """Inicializa arquivos de armazenamento"""
        os.makedirs(self.data_dir, exist_ok=True)
        
        if not os.path.exists(self.auth_file):
            with open(self.auth_file, 'w') as f:
                json.dump({}, f)
        
        if not os.path.exists(self.session_file):
            with open(self.session_file, 'w') as f:
                json.dump({}, f)
    
    def _hash_password(self, password):
        """Criptografa a senha"""
        salt = secrets.token_hex(16)
        hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return f"{salt}:{hash_obj.hex()}"
    
    def _verify_password(self, password, hashed):
        """Verifica se a senha está correta"""
        salt, hash_value = hashed.split(':')
        hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return hash_obj.hex() == hash_value
    
    def register_user(self, username, password, email):
        """Registra novo usuário"""
        with open(self.auth_file, 'r') as f:
            users = json.load(f)
        
        if username in users:
            return False, "Usuário já existe"
        
        users[username] = {
            'password': self._hash_password(password),
            'email': email,
            'created_at': datetime.now().isoformat(),
            'last_login': None
        }
        
        with open(self.auth_file, 'w') as f:
            json.dump(users, f, indent=2)
        
        return True, "Usuário criado com sucesso"
    
    def login(self, username, password):
        """Realiza login do usuário"""
        with open(self.auth_file, 'r') as f:
            users = json.load(f)
        
        if username not in users:
            return False, "Usuário não encontrado"
        
        if not self._verify_password(password, users[username]['password']):
            return False, "Senha incorreta"
        
        # Atualizar último login
        users[username]['last_login'] = datetime.now().isoformat()
        with open(self.auth_file, 'w') as f:
            json.dump(users, f, indent=2)
        
        # Criar sessão
        session_token = secrets.token_hex(32)
        with open(self.session_file, 'r') as f:
            sessions = json.load(f)
        
        sessions[session_token] = {
            'username': username,
            'created_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(days=7)).isoformat()
        }
        
        with open(self.session_file, 'w') as f:
            json.dump(sessions, f, indent=2)
        
        return True, session_token
    
    def logout(self, session_token):
        """Realiza logout"""
        with open(self.session_file, 'r') as f:
            sessions = json.load(f)
        
        if session_token in sessions:
            del sessions[session_token]
            
            with open(self.session_file, 'w') as f:
                json.dump(sessions, f, indent=2)
        
        return True
    
    def verify_session(self, session_token):
        """Verifica se a sessão é válida"""
        with open(self.session_file, 'r') as f:
            sessions = json.load(f)
        
        if session_token not in sessions:
            return None
        
        session = sessions[session_token]
        expires_at = datetime.fromisoformat(session['expires_at'])
        
        if expires_at < datetime.now():
            del sessions[session_token]
            with open(self.session_file, 'w') as f:
                json.dump(sessions, f, indent=2)
            return None
        
        return session['username']
    
    def change_password(self, username, old_password, new_password):
        """Altera a senha do usuário"""
        with open(self.auth_file, 'r') as f:
            users = json.load(f)
        
        if username not in users:
            return False, "Usuário não encontrado"
        
        if not self._verify_password(old_password, users[username]['password']):
            return False, "Senha atual incorreta"
        
        users[username]['password'] = self._hash_password(new_password)
        
        with open(self.auth_file, 'w') as f:
            json.dump(users, f, indent=2)
        
        return True, "Senha alterada com sucesso"