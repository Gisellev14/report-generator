from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...domain.model import RepositoryReport

SUPPORTED_FORMATS = ['json', 'html', 'console']

def format_report(report: "RepositoryReport", fmt: str) -> str:
        """Format the report in the specified format."""
        if fmt == 'json':
            return report.model_dump_json(indent=2)
        elif fmt == 'html':
            from ...infrastructure.visualization import generate_html_report
            return generate_html_report(report)
        else:
            from .format_console import format_console
            return format_console(report)