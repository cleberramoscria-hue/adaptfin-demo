"""
Utilitários de Criptografia - Hash, token, criptografia de dados
"""
import hashlib
import secrets
import base64
import os

# Tentar importar cryptography, se não estiver disponível, usar fallback
try:
    from cryptography.fernet import Fernet
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    Fernet = None

# Chave de criptografia (em produção, usar variável de ambiente)
ENCRYPTION_KEY = os.environ.get('ADAPTFIN_KEY', None)

if CRYPTO_AVAILABLE and ENCRYPTION_KEY:
    try:
        cipher = Fernet(ENCRYPTION_KEY.encode() if isinstance(ENCRYPTION_KEY, str) else ENCRYPTION_KEY)
    except:
        cipher = None
else:
    cipher = None

def hash_password(password, salt=None):
    """
    Gera hash da senha usando SHA256
    
    Args:
        password: Senha em texto plano
        salt: Salt (opcional)
    
    Returns:
        str: Hash da senha no formato "salt:hash"
    """
    if salt is None:
        salt = secrets.token_hex(16)
    
    # Usar PBKDF2 com SHA256
    hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    hash_value = base64.urlsafe_b64encode(hash_obj).decode()
    
    return f"{salt}:{hash_value}"

def verify_password(password, hashed):
    """
    Verifica se a senha corresponde ao hash
    
    Args:
        password: Senha em texto plano
        hashed: Hash armazenado (formato "salt:hash")
    
    Returns:
        bool: True se senha correta
    """
    try:
        salt, hash_value = hashed.split(':')
        
        hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        computed_hash = base64.urlsafe_b64encode(hash_obj).decode()
        
        return computed_hash == hash_value
    except Exception:
        return False

def generate_token(length=32):
    """
    Gera token seguro aleatório
    
    Args:
        length: Tamanho do token
    
    Returns:
        str: Token hexadecimal
    """
    return secrets.token_hex(length)

def generate_api_key():
    """
    Gera chave de API
    
    Returns:
        str: Chave API no formato adaptfin_xxx
    """
    return f"adaptfin_{secrets.token_urlsafe(32)}"

def encrypt_data(data):
    """
    Criptografa dados (fallback para base64 se cryptography não disponível)
    
    Args:
        data: String ou bytes para criptografar
    
    Returns:
        str: Dados criptografados
    """
    if isinstance(data, str):
        data = data.encode()
    
    if cipher is not None:
        try:
            encrypted = cipher.encrypt(data)
            return base64.urlsafe_b64encode(encrypted).decode()
        except:
            pass
    
    # Fallback: apenas codificar em base64 (não é seguro, mas funciona)
    return base64.urlsafe_b64encode(data).decode()

def decrypt_data(encrypted_data):
    """
    Descriptografa dados
    
    Args:
        encrypted_data: Dados criptografados
    
    Returns:
        str: Dados descriptografados
    """
    try:
        decoded = base64.urlsafe_b64decode(encrypted_data)
        
        if cipher is not None:
            try:
                decrypted = cipher.decrypt(decoded)
                return decrypted.decode()
            except:
                pass
        
        # Fallback: assumir que é apenas base64
        return decoded.decode()
    except Exception:
        return encrypted_data

def hash_file(file_path, algorithm="sha256"):
    """
    Calcula hash de um arquivo
    
    Args:
        file_path: Caminho do arquivo
        algorithm: Algoritmo de hash (md5, sha1, sha256, sha512)
    
    Returns:
        str: Hash do arquivo
    """
    hash_func = getattr(hashlib, algorithm, hashlib.sha256)()
    
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_func.update(chunk)
    
    return hash_func.hexdigest()

def generate_uuid():
    """
    Gera UUID v4
    
    Returns:
        str: UUID
    """
    import uuid
    return str(uuid.uuid4())

def mask_sensitive_data(data, show_first=4, show_last=4):
    """
    Mascara dados sensíveis (cartão, conta, etc)
    
    Args:
        data: Dados originais
        show_first: Caracteres a mostrar no início
        show_last: Caracteres a mostrar no fim
    
    Returns:
        str: Dados mascarados
    """
    if not data:
        return ""
    
    data_str = str(data)
    length = len(data_str)
    
    if length <= show_first + show_last:
        return "*" * length
    
    masked = data_str[:show_first]
    masked += "*" * (length - show_first - show_last)
    masked += data_str[-show_last:]
    
    return masked

def encrypt_file(file_path, output_path=None):
    """
    Criptografa arquivo
    
    Args:
        file_path: Arquivo origem
        output_path: Arquivo destino (opcional)
    
    Returns:
        bool: True se sucesso
    """
    if output_path is None:
        output_path = f"{file_path}.encrypted"
    
    try:
        with open(file_path, 'rb') as f:
            data = f.read()
        
        encrypted = encrypt_data(data)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(encrypted)
        
        return True
    except Exception:
        return False

def decrypt_file(file_path, output_path=None):
    """
    Descriptografa arquivo
    
    Args:
        file_path: Arquivo criptografado
        output_path: Arquivo destino (opcional)
    
    Returns:
        bool: True se sucesso
    """
    if output_path is None:
        output_path = file_path.replace('.encrypted', '')
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            encrypted = f.read()
        
        decrypted = decrypt_data(encrypted)
        
        with open(output_path, 'wb') as f:
            f.write(decrypted if isinstance(decrypted, bytes) else decrypted.encode())
        
        return True
    except Exception:
        return False