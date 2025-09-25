import threading
from datetime import datetime, timedelta
from typing import Optional, Callable

from ...infrastructure.github.github_client import GitHubClient
from ...application.services.pull_requests_service import PullRequestsService
from ...application.services.contributors_service import ContributorsService
from ...application.services.languages_service import LanguagesService
from ..service.report_generator import ReportGenerator
from ...infrastructure.error.error_handler import ErrorHandler


class ReportManager:
    def __init__(self, progress_manager):
        self.progress_manager = progress_manager
        self.report = None

    def generate_report(
        self,
        repo_name: str,
        days: int,
        token: Optional[str],
        on_complete: Callable,
        on_error: Optional[Callable] = None,
    ) -> None:
        def run_report():
            try:
                # Reset report
                self.report = None

                # Show progress
                self.progress_manager.update_status(
                    "Initializing...", show_progress=True
                )
                self.progress_manager.update_progress(0)

                # Initialize client
                client = GitHubClient(token=token)

                # Calculate date range
                self.progress_manager.update_status("Calculating date range...")
                self.progress_manager.update_progress(20)

                end_date = datetime.now()
                start_date = end_date - timedelta(days=days)

                # Initialize services
                prs_service = PullRequestsService(client)
                contrib_service = ContributorsService(client)
                lang_service = LanguagesService(client)

                # Get repository data
                self.progress_manager.update_status("Fetching pull requests...")
                self.progress_manager.update_progress(30)
                prs = prs_service.get_pull_requests(
                    repo_name, start_date=start_date, end_date=end_date
                )

                self.progress_manager.update_status("Fetching contributor stats...")
                self.progress_manager.update_progress(50)
                contributor_stats = contrib_service.get_contributor_stats(repo_name)

                self.progress_manager.update_status("Fetching repository languages...")
                self.progress_manager.update_progress(70)
                languages = lang_service.get_repository_languages(repo_name)

                # Generate report
                self.progress_manager.update_status("Generating report...")
                self.progress_manager.update_progress(80)

                report_gen = ReportGenerator()
                self.report = report_gen.generate_report(
                    repo_name=repo_name,
                    prs=prs,
                    period_start=start_date,
                    period_end=end_date,
                    contributor_stats=contributor_stats,
                    languages=languages,
                )

                # Complete
                self.progress_manager.update_status("Report generated successfully")
                self.progress_manager.update_progress(100)
                self.progress_manager.hide_progress()

                # Call completion callback
                on_complete()

            except Exception as e:
                captured_error = e
                ErrorHandler.handle_gui_error(
                    captured_error,
                    "report generation",
                    callback=lambda: [
                        self.progress_manager.hide_progress(),
                        on_error(captured_error) if on_error else None,
                    ],
                )

        # Run in background thread
        thread = threading.Thread(target=run_report)
        thread.start()

    def get_report(self):
        return self.report
