# Trying to implement circuit_breaker
from fastapi import APIRouter
import logging
import requests
import circuitbreaker

router = APIRouter()

# Get the logger for the specific module or component
logger = logging.getLogger(__name__)

class MyCircuitBreaker(circuitbreaker.CircuitBreaker):
    FAILURE_THRESHOLD = 5
    RECOVERY_TIMEOUT = 60
    EXPECTED_EXCEPTION = requests.RequestException
    
@MyCircuitBreaker()    
def call_external():
  BASE_URL = "https://swap1.dev"
  END_POINT = "api/planets/1/"
  resp = requests.get(f"{BASE_URL}/{END_POINT}")
  data = []
  if resp.status_code == 200:
    data = resp.json()
  return data

@router.get("/circuitbreaker/", tags=["circuitbreaker"])
def implement_circuit_breaker():
  '''Calling a fake url for testing'''
  try:
    data = call_external()
    return {
      "status_code": 200,
      "success": True,
      "message": "Success get starwars data", 
      "data": data
    }
  except circuitbreaker.CircuitBreakerError as e:
    logger.error(f"Circuit breaker active: {e}")
    return {
      "status_code": 503,
      "success": False,
      "message": f"Circuit breaker active: {e}"
    }
  except requests.exceptions.ConnectionError as e:
    return {
      "status_code": 500,
      "success": False,
      "message": f"Failed get starwars data: {e}"
    }