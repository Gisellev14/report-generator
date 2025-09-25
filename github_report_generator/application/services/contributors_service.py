import time
from typing import Dict

from ...infrastructure.github.github_client import GitHubClient
from ...domain.model import ContributorStats


class ContributorsService:
    def __init__(self, github_client: GitHubClient):
        self.github_client = github_client

    def get_contributor_stats(self, repo_name: str) -> Dict[str, ContributorStats]:
        stats = {}

        try:
            # Get contributor statistics
            contributors = self.github_client.make_request(
                "GET", f"repos/{repo_name}/stats/contributors"
            )

            # If we get a 202, the stats are being generated, wait and retry
            retries = 3
            while retries > 0 and not contributors:
                time.sleep(2)
                contributors = self.github_client.make_request(
                    "GET", f"repos/{repo_name}/stats/contributors"
                )
                retries -= 1
            
            contributors = contributors or []

            for contributor in contributors:
                if not contributor.get("author"):
                    continue

                login = contributor["author"]["login"]
                weeks = contributor["weeks"]

                # Calculate totals
                total_commits = contributor["total"]
                total_additions = sum(week["a"] for week in weeks)
                total_deletions = sum(week["d"] for week in weeks)

                stats[login] = ContributorStats(
                    login=login,
                    commits=total_commits,
                    additions=total_additions,
                    deletions=total_deletions,
                )

        except Exception as e:
            print(f"Warning: Error fetching contributor stats: {str(e)}")
            # Return empty stats rather than failing
            pass

        return stats
