from django.conf import settings

def is_cache_enabled():
    return getattr(settings, 'CACHE_ENABLED', True)

def get_cache_timeout():
    return getattr(settings, 'CACHE_TTL', 60 * 15)