import time
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
import requests
from email.utils import parsedate_to_datetime

limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])

# def retry_call(url, method="GET", **kwargs):
#     response = requests.request(method, url, **kwargs)
#     if response.status_code == 429:
#         # В секундах
#         retry_after = response.headers.get("Retry-After")
#         if retry_after:
#             delay = int(retry_after)
#             time.sleep(max(0, int(delay)))
            
#             return retry_call(url, method, **kwargs)
#     return response