import argparse
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

import yaml
from dotenv import load_dotenv

from .services import pull_requests_service, contributors_service, languages_service
from ..infrastructure.github import GitHubClient
from ..domain import ReportGenerator
from ..domain import PullRequestState
from ..application.utils import calculate_date_range
from ..application.formatters import SUPPORTED_FORMATS, format_report
from ..application.gui import ReportGeneratorGUI


class ReportCLI:
    def __init__(self):
        self.parser = self._create_parser()
        self.args = None
        self.config = {}

    def _create_parser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(
            description="Generate GitHub repository contribution reports."
        )

        # Required arguments
        parser.add_argument(
            "repo",
            help='GitHub repository in format "owner/repo"',
        )

        # (Mock data option removed)

        # Date range options
        date_group = parser.add_argument_group("Date range options")
        date_group.add_argument(
            "--month",
            type=int,
            help="Month to generate report for (1-12, defaults to current month)",
            choices=range(1, 13),
            default=datetime.now().month,
        )
        date_group.add_argument(
            "--year",
            type=int,
            help="Year to generate report for (defaults to current year)",
            default=datetime.now().year,
        )
        date_group.add_argument(
            "--days",
            type=int,
            help="Number of days to look back (alternative to --month/--year)",
        )

        # Output options
        output_group = parser.add_argument_group("Output options")
        output_group.add_argument(
            "--output",
            help="Output file path (default: report_<repo>_<date>.json)",
        )
        parser.add_argument(
            "--format",
            choices=SUPPORTED_FORMATS,
            default="json",
            help="Output format (default: json)",
        )

        # Configuration
        config_group = parser.add_argument_group("Configuration")
        config_group.add_argument(
            "--config",
            help="Path to configuration file",
            default=".github_report_config.yaml",
        )

        # Debugging
        debug_group = parser.add_argument_group("Debugging")
        debug_group.add_argument(
            "--debug",
            action="store_true",
            help="Enable debug output",
        )

        return parser

    def load_config(self, config_path: str) -> Dict[str, Any]:
        config = {}

        # Default initiative patterns (can be overridden in config)
        config["initiative_patterns"] = {
            "feature": r"^feature/.*",
            "bugfix": r"^bug(fix)?/.*",
            "hotfix": r"^hotfix/.*",
            "docs": r"^docs?/.*",
            "refactor": r"^refactor/.*",
            "test": r"^test/.*",
        }

        # Try to load from file if it exists
        if os.path.exists(config_path):
            try:
                with open(config_path, "r") as f:
                    file_config = yaml.safe_load(f) or {}
                    config.update(file_config)
                if self.args and self.args.debug:
                    print(f"Loaded configuration from {config_path}")
            except Exception as e:
                print(f"Warning: Failed to load config from {config_path}: {e}")

        return config

    def run(self, args=None) -> int:
        # Parse command-line arguments
        self.args = self.parser.parse_args(args)

        # Load configuration
        self.config = self.load_config(self.args.config)

        # Check GitHub token
        token = os.getenv("GITHUB_TOKEN")
        if not token:
            print(
                "\nWARNING: GITHUB_TOKEN not provided. Proceeding with unauthenticated requests."
                "\nYou can provide a token by setting the GITHUB_TOKEN environment variable."
                "\nThis is required for authenticated requests and higher rate limits."
            )

        github = GitHubClient(token=token)

        prs_service = pull_requests_service.PullRequestsService(github)
        contrib_service = contributors_service.ContributorsService(github)
        language_service = languages_service.LanguagesService(github)

        try:
            # Calculate date range
            start_date, end_date = calculate_date_range(self.args)

            # Initialize report generator with initiative patterns
            report_gen = ReportGenerator(
                initiative_patterns=self.config.get("initiative_patterns")
            )

            if self.args.debug:
                print(f"Fetching data for {self.args.repo}...")
                print(f"Auth mode: {'token' if token else 'unauthenticated'}")

            # Fetch pull requests
            prs = prs_service.get_pull_requests(
                repo_name=self.args.repo,
                state=PullRequestState.ALL,
                start_date=start_date,
                end_date=end_date,
                show_progress=True,
            )

            # Fetch additional data if needed
            contributor_stats = contrib_service.get_contributor_stats(self.args.repo)
            languages = language_service.get_repository_languages(self.args.repo)

            # Generate the report
            report = report_gen.generate_report(
                repo_name=self.args.repo,
                prs=prs,
                period_start=start_date,
                period_end=end_date,
                contributor_stats=contributor_stats,
                languages=languages,
            )

            # Format and output the report
            output = format_report(report, self.args.format)

            # Write to file or print to console
            if self.args.output:
                output_path = Path(self.args.output)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, "w") as f:
                    f.write(output)
                print(f"Report written to {output_path}")
            else:
                print(output)

            return 0

        except Exception as e:
            print(f"Error: {str(e)}", file=sys.stderr)
            if self.args and self.args.debug:
                import traceback

                traceback.print_exc()
            return 1
        finally:
            github.close()


def main():
    load_dotenv()
    if len(sys.argv) > 1:
        cli = ReportCLI()
        exit_code = cli.run()
        sys.exit(exit_code)
    else:
        app = ReportGeneratorGUI()
    app.run()


if __name__ == "__main__":
    main()
