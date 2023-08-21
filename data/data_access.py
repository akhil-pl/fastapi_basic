import redis
from functools import wraps
import json
from datetime import datetime

redis_host = "localhost"  # Replace with your Redis server host
redis_port = 6379  # Replace with your Redis server port

redis_conn = redis.StrictRedis(host=redis_host, port=redis_port)


def candidate_to_dict(candidate): # Because candidate object received from querry is not serialisable. This can be done using classmaper library also
    return {
        "id": candidate.id,
        "name": candidate.name,
        "dob": candidate.dob.strftime('%Y-%m-%d'),  # Convert datetime to string
        "sex":candidate.sex,
        "skills":candidate.skills
    }

def default_serializer(obj):
    if isinstance(obj, datetime):
        return obj.strftime('%Y-%m-%d')
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

def candidate_cache(ttl: int = 600):
    def decorator(func):
        @wraps(func)
        async def wrapper(candidate_id, *args, **kwargs):
            cache_key = f"candidate:{candidate_id}"
            cached_data = redis_conn.get(cache_key)
            if cached_data:
                return json.loads(cached_data.decode("utf-8"))
            else:
                result = await func(candidate_id, *args, **kwargs)
                candidate_dict = candidate_to_dict(result)
                redis_conn.set(cache_key, ttl, json.dumps(candidate_dict, default=default_serializer))
                return result
        return wrapper
    return decorator

# To remove the caching once the data is changed
def invalidate_candidate_cache(candidate_id):
    cache_key = f"candidate:{candidate_id}"
    redis_conn.delete(cache_key)




def all_candidates_cache():
    def decorator(func):
        @wraps(func)
        async def wrapper(pattern=None, limit=None, skip=None, *args, **kwargs):
            if pattern is None and limit is None and skip is None:
                cache_key = "all_candidates"
                cached_data = redis_conn.get(cache_key)
                if cached_data:
                    return json.loads(cached_data.decode("utf-8"))
                else:
                    result = await func(pattern, limit, skip, *args, **kwargs)
                    serialized_result = []
                    for candidate in result:
                        candidate_dict = candidate_to_dict(candidate)
                        serialized_result.append(candidate_dict)
                    redis_conn.setex(cache_key, json.dumps(serialized_result, default=default_serializer))
                    return result
            else:
                return func(pattern, limit, skip, *args, **kwargs)
        return wrapper
    return decorator

# For deleting cached once the data is changed
def invalidate_all_candidates_cache():
    cache_key = "all_candidates"
    redis_conn.delete(cache_key)
