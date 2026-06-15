"""
Utilitários de Cache - Sistema de cache para melhor performance
"""
import functools
import time
import json
import os
import hashlib
from collections import OrderedDict

class CacheManager:
    """Gerenciador de cache em memória"""
    
    def __init__(self, max_size=100, ttl=300):
        """
        Args:
            max_size: Número máximo de itens no cache
            ttl: Tempo de vida em segundos
        """
        self.cache = OrderedDict()
        self.max_size = max_size
        self.ttl = ttl
        self.hits = 0
        self.misses = 0
    
    def get(self, key):
        """
        Obtém item do cache
        
        Args:
            key: Chave do cache
        
        Returns:
            Valor ou None se não existir
        """
        if key in self.cache:
            value, timestamp = self.cache[key]
            
            # Verificar expiração
            if time.time() - timestamp < self.ttl:
                # Mover para o fim (LRU)
                self.cache.move_to_end(key)
                self.hits += 1
                return value
            else:
                del self.cache[key]
        
        self.misses += 1
        return None
    
    def set(self, key, value):
        """
        Adiciona item ao cache
        
        Args:
            key: Chave do cache
            value: Valor a armazenar
        """
        if key in self.cache:
            del self.cache[key]
        
        # Limitar tamanho
        while len(self.cache) >= self.max_size:
            self.cache.popitem(last=False)
        
        self.cache[key] = (value, time.time())
    
    def delete(self, key):
        """Remove item do cache"""
        if key in self.cache:
            del self.cache[key]
            return True
        return False
    
    def clear(self):
        """Limpa todo o cache"""
        self.cache.clear()
        self.hits = 0
        self.misses = 0
    
    def get_stats(self):
        """Retorna estatísticas do cache"""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        
        return {
            'size': len(self.cache),
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': f"{hit_rate:.1f}%",
            'max_size': self.max_size,
            'ttl': self.ttl
        }
    
    def __contains__(self, key):
        return key in self.cache
    
    def __len__(self):
        return len(self.cache)

class DiskCache:
    """Cache persistente em disco"""
    
    def __init__(self, cache_dir=".cache", ttl=3600):
        """
        Args:
            cache_dir: Diretório de cache
            ttl: Tempo de vida em segundos
        """
        self.cache_dir = cache_dir
        self.ttl = ttl
        os.makedirs(cache_dir, exist_ok=True)
    
    def _get_key_hash(self, key):
        """Gera hash da chave"""
        key_str = json.dumps(key, sort_keys=True) if not isinstance(key, str) else key
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def _get_cache_path(self, key):
        """Retorna caminho do arquivo de cache"""
        key_hash = self._get_key_hash(key)
        return os.path.join(self.cache_dir, f"{key_hash}.json")
    
    def get(self, key):
        """Obtém item do cache"""
        cache_path = self._get_cache_path(key)
        
        if not os.path.exists(cache_path):
            return None
        
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Verificar expiração
            if time.time() - data['timestamp'] < self.ttl:
                return data['value']
            else:
                os.remove(cache_path)
                return None
        except:
            return None
    
    def set(self, key, value):
        """Adiciona item ao cache"""
        cache_path = self._get_cache_path(key)
        
        try:
            data = {
                'key': self._get_key_hash(key),
                'value': value,
                'timestamp': time.time()
            }
            
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)
            
            return True
        except:
            return False
    
    def delete(self, key):
        """Remove item do cache"""
        cache_path = self._get_cache_path(key)
        
        if os.path.exists(cache_path):
            os.remove(cache_path)
            return True
        return False
    
    def clear(self, older_than=None):
        """
        Limpa cache
        
        Args:
            older_than: Limpar itens mais antigos que X segundos
        """
        removed = 0
        
        for filename in os.listdir(self.cache_dir):
            if not filename.endswith('.json'):
                continue
            
            file_path = os.path.join(self.cache_dir, filename)
            
            try:
                if older_than:
                    mtime = os.path.getmtime(file_path)
                    if time.time() - mtime < older_than:
                        continue
                
                os.remove(file_path)
                removed += 1
            except:
                pass
        
        return removed
    
    def size(self):
        """Retorna número de itens no cache"""
        return sum(1 for f in os.listdir(self.cache_dir) if f.endswith('.json'))

# Cache global
_memory_cache = CacheManager()
_disk_cache = DiskCache()

def cached(ttl=300, memory_only=False):
    """
    Decorator para cache de funções
    
    Args:
        ttl: Tempo de vida em segundos
        memory_only: Usar apenas cache em memória
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Criar chave baseada nos argumentos
            key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Tentar cache em memória
            result = _memory_cache.get(key)
            if result is not None:
                return result
            
            # Tentar cache em disco
            if not memory_only:
                result = _disk_cache.get(key)
                if result is not None:
                    # Salvar no cache em memória
                    _memory_cache.set(key, result)
                    return result
            
            # Executar função
            result = func(*args, **kwargs)
            
            # Salvar nos caches
            _memory_cache.set(key, result)
            if not memory_only:
                _disk_cache.set(key, result)
            
            return result
        
        return wrapper
    return decorator

def invalidate_cache(func_name=None):
    """
    Invalida cache
    
    Args:
        func_name: Nome da função para invalidar (opcional)
    """
    if func_name:
        # Invalida apenas funções com o nome específico
        keys_to_delete = []
        for key in _memory_cache.cache.keys():
            if key.startswith(f"{func_name}:"):
                keys_to_delete.append(key)
        
        for key in keys_to_delete:
            _memory_cache.delete(key)
    else:
        # Invalida todo o cache
        _memory_cache.clear()
        _disk_cache.clear()

def get_cache_stats():
    """Retorna estatísticas do cache"""
    return {
        'memory': _memory_cache.get_stats(),
        'disk_size': _disk_cache.size()
    }

def memory_cache(func):
    """Decorator para cache em memória apenas"""
    return cached(ttl=300, memory_only=True)(func)

def disk_cache(func):
    """Decorator para cache em disco"""
    return cached(ttl=3600, memory_only=False)(func)

# Funções auxiliares para acesso direto ao cache
def get_from_cache(key):
    """Obtém valor do cache de memória"""
    return _memory_cache.get(key)

def set_in_cache(key, value):
    """Define valor no cache de memória"""
    _memory_cache.set(key, value)

def clear_cache():
    """Limpa todo o cache"""
    _memory_cache.clear()
    _disk_cache.clear()