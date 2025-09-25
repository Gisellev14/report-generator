from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...domain.model import RepositoryReport

def format_console(report: "RepositoryReport") -> str:
        lines = [
            f"GitHub Repository Report: {report.repo_name}",
            f"Period: {report.period_start.date()} to {report.period_end.date()}",
            "=" * 80,
            "\nHighlights:",
        ]
        
        # Add highlights
        for highlight in report.highlights:
            lines.append(f"- {highlight}")
        
        # Add contributor stats
        lines.extend(["", "Contributors:", "-" * 40])
        for login, stats in sorted(
            report.contributors.items(),
            key=lambda x: x[1].prs_authored,
            reverse=True
        ):
            lines.append(
                f"{login}: {stats.prs_authored} PRs authored, "
                f"{stats.prs_merged} merged, "
                f"{stats.reviews_given} reviews given"
            )
        
        # Add initiative stats
        if report.initiatives:
            lines.extend(["", "Initiatives:", "-" * 40])
            for name, stats in sorted(
                report.initiatives.items(),
                key=lambda x: x[1].pr_count,
                reverse=True
            ):
                lines.append(
                    f"{name}: {stats.pr_count} PRs, "
                    f"{len(stats.contributors)} contributors, "
                    f"avg lead time: {stats.avg_lead_time or 'N/A'} hours"
                )
        
        # Add language stats
        if report.languages:
            lines.extend(["", "Languages:", "-" * 40])
            total_bytes = sum(report.languages.values())
            if total_bytes > 0:
                for lang, bytes_count in sorted(
                    report.languages.items(),
                    key=lambda x: x[1],
                    reverse=True
                ):
                    percentage = (bytes_count / total_bytes) * 100
                    lines.append(f"{lang}: {percentage:.1f}%")
            else:
                lines.append("No data available")
        
        return "\n".join(lines)