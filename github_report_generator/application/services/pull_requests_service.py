from datetime import datetime
from typing import List, Optional
from tqdm import tqdm

from ...domain.model import PullRequest, PullRequestState
from ...infrastructure.github.github_client import GitHubClient

class PullRequestsService:
    def __init__(self, github_client: GitHubClient):
        self.github_client = github_client
    
    def get_pull_requests(
        self,
        repo_name: str,
        state: PullRequestState = PullRequestState.ALL,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        show_progress: bool = True,
    ) -> List[PullRequest]:
        prs = []
        page = 1
        per_page = 30
        
        github_state = state.value if state != PullRequestState.MERGED else "closed"

        while True:
            params = {
                "state": github_state,
                "sort": "updated",
                "direction": "desc",
                "per_page": per_page,
                "page": page,
            }

            try:
                pr_data = self.github_client.make_request("GET", f"repos/{repo_name}/pulls", params)

                if not pr_data:
                    break

                for pr in tqdm(pr_data, desc=f"Fetching PRs (page {page})") if show_progress else pr_data:
                    if state == PullRequestState.MERGED and not pr.get("merged_at"):
                        continue

                    updated_at = datetime.strptime(
                        pr["updated_at"], "%Y-%m-%dT%H:%M:%SZ"
                    )
                    if start_date and updated_at < start_date:
                        continue
                    if end_date and updated_at > end_date:
                        continue

                    batch_urls = [pr["url"], f"{pr['url']}/reviews"]
                    batch_results = self.github_client.batch_request(batch_urls)

                    pr_details = batch_results[pr["url"]] or {}
                    reviews = batch_results[f"{pr['url']}/reviews"] or []
                    reviewers = list(
                        set(r["user"]["login"] for r in reviews if r["user"])
                    )

                    prs.append(
                        PullRequest(
                            number=pr["number"],
                            title=pr["title"],
                            state=PullRequestState(pr["state"].lower()),
                            author=pr["user"]["login"] if pr["user"] else "unknown",
                            created_at=datetime.strptime(
                                pr["created_at"], "%Y-%m-%dT%H:%M:%SZ"
                            ),
                            updated_at=updated_at,
                            closed_at=datetime.strptime(
                                pr["closed_at"], "%Y-%m-%dT%H:%M:%SZ"
                            )
                            if pr["closed_at"]
                            else None,
                            merged_at=datetime.strptime(
                                pr["merged_at"], "%Y-%m-%dT%H:%M:%SZ"
                            )
                            if pr["merged_at"]
                            else None,
                            additions=pr_details.get("additions", 0),
                            deletions=pr_details.get("deletions", 0),
                            changed_files=pr_details.get("changed_files", 0),
                            comments=pr_details.get("comments", 0),
                            review_comments=pr_details.get("review_comments", 0),
                            commits=pr_details.get("commits", 0),
                            branch=pr["head"]["ref"],
                            labels=[label["name"] for label in pr.get("labels", [])],
                            reviewers=reviewers,
                        )
                    )

                if len(pr_data) < per_page:
                    break

                page += 1

            except Exception as e:
                raise Exception(f"Error fetching pull requests: {str(e)}")

        return prs