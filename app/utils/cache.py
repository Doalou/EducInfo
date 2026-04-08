from app.extensions import cache

def get_cached(key):
    """Récupère une valeur du cache."""
    return cache.get(key)

def set_cached(key, value, timeout=None):
    """Définit une valeur dans le cache."""
    return cache.set(key, value, timeout=timeout)
