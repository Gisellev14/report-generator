import os
from datetime import datetime
from typing import Dict, List, Optional, Any

import requests
import time

from .github_decorators import cache_response, handle_github_request


class GitHubClient:
    BASE_URL = "https://api.github.com"

    def __init__(self, token: Optional[str] = None):
        self.token = token or os.getenv("GITHUB_TOKEN")
        self.session = requests.Session()
        if self.token:
            self.session.headers.update(
                {
                    "Authorization": f"token {self.token}",
                    "Accept": "application/vnd.github.v3+json",
                }
            )
        self.session.headers.update({"User-Agent": "GitHub-Report-Generator"})
        self._cache: Dict[str, Any] = {}

    @handle_github_request
    @cache_response
    def make_request(self, method: str, url: str, params: Optional[Dict] = None) -> Any:
        cache_key = f"{method}:{url}:{str(params)}"

        # Check cache
        if hasattr(self, "_cache") and cache_key in self._cache:
            return self._cache[cache_key]

        if not hasattr(self, "_cache"):
            self._cache = {}
        if not url.startswith("http"):
            url = f"{self.BASE_URL}/{url.lstrip('/')}"

        retry_count = 0
        max_retries = 3
        response = None
        while retry_count <= max_retries:
            try:
                response = self.session.request(method, url, params=params)

                # Check rate limits
                remaining = int(response.headers.get("X-RateLimit-Remaining", 0))
                reset_time = datetime.fromtimestamp(
                    int(response.headers.get("X-RateLimit-Reset", 0))
                ).strftime("%Y-%m-%d %H:%M:%S")

                if remaining < 100:
                    print("\nWARNING: GitHub API rate limit is low!")
                    print(f"Remaining requests: {remaining}")
                    print(f"Rate limit resets at: {reset_time}")

                if (
                    response.status_code == 403
                    and "rate limit exceeded" in response.text.lower()
                ):
                    reset_seconds = int(
                        response.headers.get("X-RateLimit-Reset", 0)
                    ) - int(time.time())
                    if reset_seconds > 0 and retry_count < max_retries:
                        wait_time = min(reset_seconds + 1, 2**retry_count * 5)
                        print(f"Rate limit exceeded. Waiting {wait_time} seconds...")
                        time.sleep(wait_time)
                        retry_count += 1
                        continue
                    raise Exception(
                        f"GitHub API rate limit exceeded. Resets at {reset_time}"
                    )

                response.raise_for_status()
                data = response.json()

                # Cache the response if successful
                self._cache[cache_key] = data

                return data

            except requests.exceptions.RequestException as e:
                if retry_count < max_retries:
                    retry_count += 1
                    time.sleep(2**retry_count)
                    continue
                if response and response.status_code == 404:
                    raise ValueError(f"Resource not found: {url}")
                raise Exception(f"GitHub API request failed: {str(e)}")

        raise Exception(f"Failed after {max_retries} retries")

    def batch_request(
        self, urls: List[str], method: str = "GET", params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        # Make multiple requests in parallel to save on rate limits
        results = {}
        for url in urls:
            try:
                results[url] = self.make_request(method, url, params)
            except Exception as e:
                print(f"Warning: Failed to fetch {url}: {str(e)}")
                results[url] = None
        return results

    def close(self):
        if hasattr(self, "session"):
            self.session.close()
