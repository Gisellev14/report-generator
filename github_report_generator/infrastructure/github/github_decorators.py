"""Decorators for GitHub API client."""

import functools
import time
from datetime import datetime
from typing import Callable

def cache_response(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        # Generate cache key
        cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
        
        # Initialize cache if needed
        if not hasattr(self, '_cache'):
            self._cache = {}
            
        # Return cached response if available
        if cache_key in self._cache:
            return self._cache[cache_key]
            
        # Get fresh response
        response = func(self, *args, **kwargs)
        self._cache[cache_key] = response
        return response
    return wrapper

def handle_github_request(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        max_retries = kwargs.pop('max_retries', 3)
        retry_count = 0
        
        while retry_count <= max_retries:
            try:
                response = func(self, *args, **kwargs)
                
                # Check rate limits from response headers
                remaining = int(getattr(response, 'headers', {}).get('X-RateLimit-Remaining', 0))
                reset_time = datetime.fromtimestamp(
                    int(getattr(response, 'headers', {}).get('X-RateLimit-Reset', 0))
                ).strftime('%Y-%m-%d %H:%M:%S')
                
                if remaining < 100:
                    print("\nWARNING: GitHub API rate limit is low!")
                    print(f"Remaining requests: {remaining}")
                    print(f"Rate limit resets at: {reset_time}")
                
                if getattr(response, 'status_code', 0) == 403 and 'rate limit exceeded' in str(response).lower():
                    reset_seconds = int(getattr(response, 'headers', {}).get('X-RateLimit-Reset', 0)) - int(time.time())
                    if reset_seconds > 0 and retry_count < max_retries:
                        wait_time = min(reset_seconds + 1, 2 ** retry_count * 5)
                        print(f"Rate limit exceeded. Waiting {wait_time} seconds...")
                        time.sleep(wait_time)
                        retry_count += 1
                        continue
                    raise Exception(f"GitHub API rate limit exceeded. Resets at {reset_time}")
                
                return response
                
            except Exception as e:
                if retry_count < max_retries:
                    retry_count += 1
                    time.sleep(2 ** retry_count)
                    continue
                raise Exception(f"GitHub API request failed: {str(e)}")
        
        raise Exception(f"Failed after {max_retries} retries")
    return wrapper
