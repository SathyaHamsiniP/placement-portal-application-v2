import json
import redis
from functools import wraps
from flask import request, jsonify

# Connect to Redis DB 3 for caching 
redis_client = redis.Redis(host='localhost', port=6379, db=3, decode_responses=True)

def cache_response(timeout=300, key_prefix="api_cache"):
    """
    Decorator to cache a view output in Redis.
    Incorporate user context if current_user is present, and query params.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Access kwargs.get('current_user') if passed by token_required
            current_user = kwargs.get('current_user')
            user_part = f":user_{current_user.id}" if current_user else ""
            
            # Incorporate query parameters
            query_part = f":args_{hash(frozenset(request.args.items()))}" if request.args else ""
            
            cache_key = f"{key_prefix}:{request.path}{user_part}{query_part}"
            
            try:
                cached_data = redis_client.get(cache_key)
                if cached_data:
                    return jsonify(json.loads(cached_data))
            except Exception:
                pass  # Fallback to database on Redis connection issues
            
            # Run the actual view function
            response = f(*args, **kwargs)
            
            try:
                # Extract JSON payload and status code
                if isinstance(response, tuple):
                    res_obj, status_code = response
                else:
                    res_obj = response
                    status_code = 200
                
                if status_code == 200:
                    if hasattr(res_obj, 'get_json'):
                        data = res_obj.get_json()
                    elif isinstance(res_obj, dict) or isinstance(res_obj, list):
                        data = res_obj
                    else:
                        data = None
                    
                    if data is not None:
                        redis_client.setex(cache_key, timeout, json.dumps(data))
            except Exception:
                pass
                
            return response
        return decorated_function
    return decorator

def invalidate_cache(pattern="*"):
    """
    Invalidate Redis cache keys matching the given pattern wildcard.
    """
    try:
        keys = redis_client.keys(pattern)
        if keys:
            redis_client.delete(*keys)
    except Exception:
        pass
