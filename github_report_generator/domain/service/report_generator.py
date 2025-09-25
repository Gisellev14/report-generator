import re
from datetime import datetime
from typing import Dict, List, Optional
import statistics

from ..model.models import (
    ContributorStats,
    InitiativeStats,
    PullRequest,
    PullRequestState,
    RepositoryReport,
)


class ReportGenerator:
    """Generates reports from GitHub repository data."""

    def __init__(self, initiative_patterns: Optional[Dict[str, str]] = None):
        """Initialize the report generator.

        Args:
            initiative_patterns: Dictionary mapping initiative names to regex patterns
                               for branch name matching. If None, loads from config file.
        """
        if initiative_patterns is not None:
            self.initiative_patterns = initiative_patterns
        else:
            self.initiative_patterns = self._load_initiative_patterns()

    def _load_initiative_patterns(self) -> Dict[str, str]:
        """Load initiative patterns from configuration file.

        Returns:
            Dictionary mapping initiative names to regex patterns.
            If config file is not found, returns default patterns.
        """
        try:
            import yaml
            from pathlib import Path

            config_path = Path(__file__).parent / "config" / "initiatives.yaml"
            if config_path.exists():
                with open(config_path, "r") as f:
                    return yaml.safe_load(f)
        except Exception as e:
            print(f"Warning: Could not load initiative patterns: {e}")

        # Default patterns if config file not found or invalid
        return {
            "Features": r"^feature/|^feat/",
            "Bug Fixes": r"^fix/|^bugfix/|^hotfix/",
            "Documentation": r"^docs/|^documentation/",
            "Testing": r"^test/|^testing/",
            "Refactoring": r"^refactor/",
            "Dependencies": r"^deps/|^dependencies/",
            "CI/CD": r"^ci/|^cd/",
            "Performance": r"^perf/",
            "Security": r"^security/",
            "UI/UX": r"^ui/|^ux/",
            "Analytics": r"^analytics/",
            "API": r"^api/",
            "Infrastructure": r"^infra/",
            "Configuration": r"^config/",
            "Tooling": r"^tools/|^tooling/",
            "Maintenance": r"^chore/|^maint/",
            "Experiments": r"^exp/|^experimental/",
        }

    def _categorize_pr_size(self, pr: PullRequest) -> str:
        """Categorize PR size based on total number of changes.

        Size categories:
        - xs: ≤ 10 changes
        - s:  11-50 changes
        - m:  51-250 changes
        - l:  251-1000 changes
        - xl: > 1000 changes
        """
        total_changes = pr.additions + pr.deletions
        if total_changes <= 10:
            return "xs"
        elif total_changes <= 50:
            return "s"
        elif total_changes <= 250:
            return "m"
        elif total_changes <= 1000:
            return "l"
        return "xl"

    def generate_report(
        self,
        repo_name: str,
        prs: List[PullRequest],
        period_start: datetime,
        period_end: datetime,
        contributor_stats: Optional[Dict[str, ContributorStats]] = None,
        languages: Optional[Dict[str, int]] = None,
    ) -> RepositoryReport:
        """Generate a repository report for the given time period.

        Args:
            repo_name: Name of the repository in 'owner/repo' format
            prs: List of pull requests in the period
            period_start: Start of the reporting period
            period_end: End of the reporting period
            contributor_stats: Optional pre-fetched contributor statistics
            languages: Optional pre-fetched language statistics

        Returns:
            RepositoryReport containing the analysis
        """
        # Initialize the report
        report = RepositoryReport(
            repo_name=repo_name, period_start=period_start, period_end=period_end
        )

        # Process PRs to extract metrics
        self._process_prs(report, prs)

        # Add contributor statistics if provided
        if contributor_stats:
            self._merge_contributor_stats(report, contributor_stats, prs)

        # Add language statistics if provided
        if languages:
            report.languages = languages

        # Calculate metrics
        self._calculate_metrics(report)

        # Generate highlights
        self._generate_highlights(report)

        return report

    def _process_prs(self, report: RepositoryReport, prs: List[PullRequest]) -> None:
        """Process pull requests to extract metrics."""
        # Initialize counters
        report.prs_merged = 0
        report.prs_open = 0
        report.prs_closed = 0

        # Lists for calculating medians
        time_to_first_reviews = []
        time_to_approvals = []
        total_reviews = 0
        total_review_comments = 0

        for pr in prs:
            # Categorize PR size
            pr.size_category = self._categorize_pr_size(pr)
            report.pr_size_distribution[pr.size_category] += 1

            # Calculate review metrics
            if pr.review_metrics:
                if pr.review_metrics.time_to_first_review is not None:
                    time_to_first_reviews.append(pr.review_metrics.time_to_first_review)
                if pr.review_metrics.time_to_approval is not None:
                    time_to_approvals.append(pr.review_metrics.time_to_approval)
                total_reviews += pr.review_metrics.number_of_reviewers
                total_review_comments += pr.review_metrics.number_of_comments

            # Categorize PR by state
            if pr.state == PullRequestState.MERGED:
                report.prs_merged += 1
            elif pr.state == PullRequestState.OPEN:
                report.prs_open += 1
            elif pr.state == PullRequestState.CLOSED:
                report.prs_closed += 1

            # Update contributor stats
            self._update_contributor_stats(report, pr)

            # Map initiatives from branch name
            self._map_initiatives(report, pr)

            # Update lead and cycle times for merged PRs
            if pr.state == PullRequestState.MERGED and pr.merged_at:
                lead_time = (
                    pr.merged_at - pr.created_at
                ).total_seconds() / 3600  # in hours
                cycle_time = (
                    pr.merged_at - pr.created_at
                ).total_seconds() / 3600  # in hours

                if pr.author in report.contributors:
                    report.contributors[pr.author].lead_times.append(lead_time)
                    report.contributors[pr.author].cycle_times.append(cycle_time)

    def _update_contributor_stats(
        self, report: RepositoryReport, pr: PullRequest
    ) -> None:
        """Update contributor statistics based on a PR."""
        # Initialize contributor if not exists
        if pr.author not in report.contributors:
            report.contributors[pr.author] = ContributorStats(login=pr.author)

        # Update PR authored count
        if pr.state == PullRequestState.MERGED:
            report.contributors[pr.author].prs_merged += 1

        report.contributors[pr.author].prs_authored += 1

        # Update reviews received
        for reviewer in pr.reviewers:
            if reviewer not in report.contributors:
                report.contributors[reviewer] = ContributorStats(login=reviewer)
            report.contributors[reviewer].reviews_given += 1

            # Count reviews received by the PR author
            report.contributors[pr.author].reviews_received += 1

    def _map_initiatives(self, report: RepositoryReport, pr: PullRequest) -> None:
        """Map PRs to initiatives based on branch name patterns."""
        if not self.initiative_patterns:
            return

        branch = pr.branch.lower()
        matched_initiatives = []

        # Check branch name against each pattern
        for initiative, pattern in self.initiative_patterns.items():
            if re.match(pattern, branch, re.IGNORECASE):
                matched_initiatives.append(initiative)

                # Initialize initiative stats if not exists
                if initiative not in report.initiatives:
                    report.initiatives[initiative] = InitiativeStats(name=initiative)

                # Update initiative stats
                stats = report.initiatives[initiative]
                stats.pr_count += 1
                stats.contributors[pr.author] = stats.contributors.get(pr.author, 0) + 1

                # Update timing metrics for merged PRs
                if (
                    pr.state == PullRequestState.MERGED
                    and pr.merged_at
                    and pr.created_at
                ):
                    lead_time = (pr.merged_at - pr.created_at).total_seconds() / 3600
                    cycle_time = lead_time  # Simplified for now

                    # Update averages using exponential moving average
                    alpha = 0.3  # Smoothing factor
                    if stats.avg_lead_time is None:
                        stats.avg_lead_time = lead_time
                    else:
                        stats.avg_lead_time = (
                            alpha * lead_time + (1 - alpha) * stats.avg_lead_time
                        )

                    if stats.avg_cycle_time is None:
                        stats.avg_cycle_time = cycle_time
                    else:
                        stats.avg_cycle_time = (
                            alpha * cycle_time + (1 - alpha) * stats.avg_cycle_time
                        )

        # Store matched initiatives in the PR
        pr.initiatives = matched_initiatives

    def _merge_contributor_stats(
        self,
        report: RepositoryReport,
        contributor_stats: Dict[str, ContributorStats],
        prs: List[PullRequest],
    ) -> None:
        """Merge pre-fetched contributor statistics into the report."""
        for login, stats in contributor_stats.items():
            if login not in report.contributors:
                report.contributors[login] = stats
            else:
                # Merge the stats
                existing = report.contributors[login]
                existing.commits = stats.commits
                existing.additions = stats.additions
                existing.deletions = stats.deletions

    def _calculate_metrics(self, report: RepositoryReport) -> None:
        """Calculate metrics for the report."""
        # Calculate total PRs
        report.total_prs = report.prs_merged + report.prs_open + report.prs_closed

        # Calculate lead and cycle times
        all_lead_times = []
        all_cycle_times = []
        time_to_first_reviews = []
        time_to_approvals = []
        total_reviews = 0
        total_review_comments = 0

        for pr in report.prs:
            if pr.review_metrics:
                if pr.review_metrics.time_to_first_review is not None:
                    time_to_first_reviews.append(pr.review_metrics.time_to_first_review)
                if pr.review_metrics.time_to_approval is not None:
                    time_to_approvals.append(pr.review_metrics.time_to_approval)
                total_reviews += pr.review_metrics.number_of_reviewers
                total_review_comments += pr.review_metrics.number_of_comments

        for contributor in report.contributors.values():
            if contributor.lead_times:
                all_lead_times.extend(contributor.lead_times)
            if contributor.cycle_times:
                all_cycle_times.extend(contributor.cycle_times)

        # Calculate medians
        if all_lead_times:
            report.median_lead_time = statistics.median(all_lead_times)
        if all_cycle_times:
            report.median_cycle_time = statistics.median(all_cycle_times)
        if time_to_first_reviews:
            report.median_time_to_first_review = statistics.median(
                time_to_first_reviews
            )
        if time_to_approvals:
            report.median_time_to_approval = statistics.median(time_to_approvals)

        # Calculate averages
        if report.total_prs > 0:
            report.avg_reviews_per_pr = total_reviews / report.total_prs
            report.avg_review_comments_per_pr = total_review_comments / report.total_prs

        # Calculate initiative metrics
        for initiative in report.initiatives.values():
            # Calculate average lead and cycle times for the initiative
            lead_times = []
            cycle_times = []

            for pr in report.prs:
                if (
                    initiative.name in pr.initiatives
                    and pr.state == PullRequestState.MERGED
                ):
                    if pr.merged_at:
                        lead_times.append(
                            (pr.merged_at - pr.created_at).total_seconds() / 3600
                        )
                        cycle_times.append(
                            (pr.merged_at - pr.created_at).total_seconds() / 3600
                        )

            if lead_times:
                initiative.avg_lead_time = statistics.mean(lead_times)
            if cycle_times:
                initiative.avg_cycle_time = statistics.mean(cycle_times)

    def _generate_highlights(self, report: RepositoryReport) -> None:
        """Generate highlight points for the report."""
        highlights = []

        # Total contributions
        highlights.append(
            f"Total of {report.total_prs} PRs were created in this period, "
            f"with {report.prs_merged} merged, {report.prs_open} still open, "
            f"and {report.prs_closed} closed without merging."
        )

        # PR size distribution
        size_dist = report.pr_size_distribution
        total_prs = sum(size_dist.values())
        if total_prs > 0:
            size_percentages = {
                size: (count / total_prs) * 100
                for size, count in size_dist.items()
                if count > 0
            }
            size_str = ", ".join(
                f"{size.upper()}: {pct:.1f}%"
                for size, pct in sorted(size_percentages.items())
            )
            highlights.append(f"PR size distribution: {size_str}")

        # Review metrics
        if report.median_time_to_first_review is not None:
            highlights.append(
                f"Median time to first review: {report.median_time_to_first_review:.1f} hours"
            )
        if report.avg_reviews_per_pr > 0:
            highlights.append(
                f"Average reviews per PR: {report.avg_reviews_per_pr:.1f}, "
                f"with {report.avg_review_comments_per_pr:.1f} comments on average"
            )

        # Top contributors
        if report.contributors:
            top_contributors = sorted(
                report.contributors.values(),
                key=lambda x: x.prs_authored
                + x.reviews_given,  # Consider both PRs and reviews
                reverse=True,
            )[:3]

            if top_contributors:
                contribs = ", ".join(
                    f"{c.login} ({c.prs_authored} PRs, {c.reviews_given} reviews)"
                    for c in top_contributors
                )
                highlights.append(f"Top contributors: {contribs}")

        # Lead and cycle times
        if report.median_lead_time is not None:
            highlights.append(
                f"Median lead time (first commit to merge): {report.median_lead_time:.1f} hours"
            )

        if report.median_cycle_time is not None:
            highlights.append(
                f"Median cycle time (PR open to merge): {report.median_cycle_time:.1f} hours"
            )

        # Top initiatives
        if report.initiatives:
            # Sort by both PR count and average cycle time
            def initiative_score(i: InitiativeStats) -> float:
                pr_score = i.pr_count
                time_score = 0
                if i.avg_cycle_time is not None:
                    # Lower cycle time is better
                    time_score = 100 / (
                        i.avg_cycle_time + 1
                    )  # Add 1 to avoid division by zero
                return pr_score + time_score

            top_initiatives = sorted(
                report.initiatives.values(), key=initiative_score, reverse=True
            )[:3]

            if top_initiatives:
                init_str = ", ".join(
                    f"{i.name} ({i.pr_count} PRs, {i.avg_cycle_time:.1f}h avg cycle)"
                    for i in top_initiatives
                    if i.avg_cycle_time is not None
                )
                highlights.append(f"Top initiatives: {init_str}")

        # Add insights about initiatives
        if report.initiatives:
            # Find fastest and slowest initiatives
            initiatives_with_times = [
                i
                for i in report.initiatives.values()
                if i.avg_cycle_time is not None and i.pr_count >= 3  # At least 3 PRs
            ]

            if initiatives_with_times:
                fastest = min(initiatives_with_times, key=lambda i: i.avg_cycle_time)
                slowest = max(initiatives_with_times, key=lambda i: i.avg_cycle_time)

                if (
                    fastest.avg_cycle_time < slowest.avg_cycle_time * 0.5
                ):  # At least 2x faster
                    highlights.append(
                        f"The {fastest.name} initiative has notably faster cycle times "
                        f"({fastest.avg_cycle_time:.1f}h vs {slowest.avg_cycle_time:.1f}h "
                        f"for {slowest.name})"
                    )

        report.highlights = highlights
