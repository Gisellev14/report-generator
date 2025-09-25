from typing import Dict
from ...infrastructure.github.github_client import GitHubClient


class LanguagesService:
    def __init__(self, github_client: GitHubClient):
        self.github_client = github_client

    def get_repository_languages(self, repo_name: str) -> Dict[str, int]:
        try:
            return self.github_client.make_request(
                "GET", f"repos/{repo_name}/languages"
            )
        except Exception as e:
            print(f"Warning: Error fetching repository languages: {str(e)}")
            return {}
