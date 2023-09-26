import redis
from functools import wraps
import json
from datetime import datetime
import logging

redis_host = "localhost"  # Replace with your Redis server host
redis_port = 6379  # Replace with your Redis server port

redis_conn = redis.StrictRedis(host=redis_host, port=redis_port)


def candidate_to_dict(candidate): # Because candidate object received from querry is not serialisable.
    try:
        return {
            "id": candidate.id,
            "name": candidate.name,
            "dob": candidate.dob.strftime('%Y-%m-%d %H:%M:%S'),  # Convert datetime to string
            "sex":candidate.sex,
            "skills":candidate.skills
        }
    except Exception as e:
        logging.debug(f"ERROR while serializing candidate: {e}")

def employee_to_dict(employee):
    print("Employee Object: ",employee)
    return {
        "id": employee.id,
        "designation": employee.designation,
        "start": employee.start.strftime('%Y-%m-%d %H:%M:%S'),
        "end": employee.end.strftime('%Y-%m-%d %H:%M:%S'),
        "candidate_id": employee.cid,
        "department_id": employee.did
        # "candidate": candidate_to_dict(employee.candidate),  # Nested serialization
        # "department": {
        #     "id": employee.department.id,
        #     "name": employee.department.name
        # }
    }

def department_to_dict(department):
    return {
        "id":department.id,
        "name":department.name
    }

def default_serializer(obj):
    if isinstance(obj, datetime):
        return obj.strftime('%Y-%m-%d %H:%M:%S')
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

def candidate_cache(ttl: int = 600):
    def decorator(func):
        @wraps(func)
        async def wrapper(candidate_id, *args, **kwargs):
            cache_key = f"candidate:{candidate_id}"
            cached_data = redis_conn.get(cache_key)
            if cached_data:
                # logging.debug(f"No ERROR, Just checking logging:") # Just checking loging
                return json.loads(cached_data.decode("utf-8"))
            else:
                result = await func(candidate_id, *args, **kwargs)
                candidate_dict = candidate_to_dict(result)
                redis_conn.setex(cache_key, ttl, json.dumps(candidate_dict, default=default_serializer))
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
                    redis_conn.set(cache_key, json.dumps(serialized_result, default=default_serializer))
                    return result
            else:
                return func(pattern, limit, skip, *args, **kwargs)
        return wrapper
    return decorator

# For deleting cached once the data is changed
def invalidate_all_candidates_cache():
    cache_key = "all_candidates"
    redis_conn.delete(cache_key)






def employee_cache(ttl: int = 600):
    def decorator(func):
        @wraps(func)
        async def wrapper(employee_id, *args, **kwargs):
            cache_key = f"employee:{employee_id}"
            cached_data = redis_conn.get(cache_key)
            if cached_data:
                return json.loads(cached_data.decode("utf-8"))
            else:
                result = await func(employee_id, *args, **kwargs)
                # employee_dict = employee_to_dict(result)
                redis_conn.setex(cache_key, ttl, json.dumps(result, default=default_serializer))
                return result
        return wrapper
    return decorator

# To remove the caching once the data is changed
def invalidate_employee_cache(employee_id):
    cache_key = f"employee:{employee_id}"
    redis_conn.delete(cache_key)



def all_employees_cache():
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = "all_employees"
            cached_data = redis_conn.get(cache_key)
            if cached_data:
                return json.loads(cached_data.decode("utf-8"))
            else:
                result = await func(*args, **kwargs)
                serialized_result = []
                for employee in result:
                    employee_dict = employee_to_dict(employee)
                    serialized_result.append(employee_dict)
                redis_conn.set(cache_key, json.dumps(serialized_result, default=default_serializer))
                return result
        return wrapper
    return decorator

# For deleting cached once the data is changed
def invalidate_all_employees_cache():
    cache_key = "all_employees"
    redis_conn.delete(cache_key)




# OTP caching
def set_otpkey_cache(email:str, key:str, ttl:int=600):
    cache_key = f"{email}:otpkey"
    redis_conn.setex(cache_key, ttl, key)

def get_otpkey_cache(email:str):
    cache_key = f"{email}:otpkey"
    return redis_conn.get(cache_key)

def invalidate_otpkey_cache(email:str):
    cache_key = f"{email}:otpkey"
    redis_conn.delete(cache_key)




# For clearing all cache
def flush_all():
    try:
        redis_conn.flushall()  # Clear all cached data
        return {"Cache cleared successfully"}
    except Exception as e:
        return {f"An error occurred: {str(e)}"}
