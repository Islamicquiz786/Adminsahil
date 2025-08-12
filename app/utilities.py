import time
from datetime import datetime

def timestamp():
    """Get formatted timestamp"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def rate_limited(max_calls, time_frame):
    """Simple rate limiter decorator"""
    def decorator(func):
        calls = []
        
        def wrapper(*args, **kwargs):
            now = time.time()
            calls.append(now)
            
            # Remove old calls
            calls[:] = [call for call in calls if now - call < time_frame]
            
            if len(calls) > max_calls:
                raise Exception("Rate limit exceeded")
            return func(*args, **kwargs)
        return wrapper
    return decorator