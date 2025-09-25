from ...domain.model.models import RepositoryReport
from ...domain.service.velocity import calculate_weekly_metrics
from typing import Optional


class ChartUpdater:
    def __init__(self, tab_manager, chart_manager):
        self.tab_manager = tab_manager
        self.chart_manager = chart_manager

    def update_charts(self, report: Optional[RepositoryReport] = None) -> None:
        if not report:
            return

        self.update_overview_charts(report)
        self.update_pr_charts(report)
        self.update_review_charts(report)
        self.update_contributor_charts(report)
        self.update_velocity_charts(report)

    def update_overview_charts(self, report: RepositoryReport):
        frame = self.tab_manager.frames["overview"]["chart"]
        fig, canvas = self.chart_manager.create_chart(frame, "pie")

        try:
            # PR status pie chart
            ax1 = fig.add_subplot(121)
            status_data = [report.prs_merged, report.prs_open, report.prs_closed]
            status_labels = ["Merged", "Open", "Closed"]
            total_status = sum(d for d in status_data if d is not None)
            if total_status and total_status > 0:
                ax1.pie(status_data, labels=status_labels, autopct="%1.1f%%")
                ax1.set_title("PR Status Distribution")
            else:
                ax1.text(0.5, 0.5, "No PR status data", ha="center", va="center")
                ax1.set_title("PR Status Distribution")

            # Language distribution
            ax2 = fig.add_subplot(122)
            languages = getattr(report, "languages", {})
            if languages:
                total = sum(languages.values())
                if total and total > 0:
                    lang_data = [
                        (lang, count / total * 100) for lang, count in languages.items()
                    ]
                    lang_data.sort(key=lambda x: x[1], reverse=True)

                    langs = [x[0] for x in lang_data]
                    percentages = [x[1] for x in lang_data]

                    ax2.pie(percentages, labels=langs, autopct="%1.1f%%")
                    ax2.set_title("Language Distribution")
                    ax2.tick_params(axis="x", rotation=45)
                else:
                    ax2.text(0.5, 0.5, "No language data", ha="center", va="center")
                    ax2.set_title("Language Distribution")
            else:
                ax2.text(0.5, 0.5, "No language data", ha="center", va="center")
                ax2.set_title("Language Distribution")

            fig.tight_layout()
            canvas.draw()

        except Exception as e:
            self._handle_chart_error("overview", e)

    def update_pr_charts(self, report: RepositoryReport):
        frame = self.tab_manager.frames["pr_metrics"]["chart"]
        fig, canvas = self.chart_manager.create_chart(frame)

        try:
            ax = fig.add_subplot(111)

            # PR size distribution
            pr_dist = getattr(report, "pr_size_distribution", {})
            if pr_dist:
                sizes = []
                counts = []
                for size, count in pr_dist.items():
                    if count > 0:
                        sizes.append(size.upper())
                        counts.append(count)

                if sizes and counts:
                    ax.pie(counts, labels=sizes, autopct="%1.1f%%")
                    ax.set_title("PR Size Distribution")

            fig.tight_layout()
            canvas.draw()

        except Exception as e:
            self._handle_chart_error("PR metrics", e)

    def update_review_charts(self, report: RepositoryReport):
        frame = self.tab_manager.frames["review_metrics"]["chart"]
        fig, canvas = self.chart_manager.create_chart(frame)

        try:
            ax1 = fig.add_subplot(121)
            ax2 = fig.add_subplot(122)

            # Review time distribution
            review_times = []
            approval_times = []

            for pr in report.prs:
                if hasattr(pr, "review_metrics"):
                    if hasattr(pr.review_metrics, "time_to_first_review"):
                        if pr.review_metrics.time_to_first_review is not None:
                            review_times.append(pr.review_metrics.time_to_first_review)
                    if hasattr(pr.review_metrics, "time_to_approval"):
                        if pr.review_metrics.time_to_approval is not None:
                            approval_times.append(pr.review_metrics.time_to_approval)

            if review_times or approval_times:
                ax1.boxplot(
                    [review_times, approval_times], labels=["First Review", "Approval"]
                )
                ax1.set_title("Review Time Distribution")
                ax1.set_ylabel("Hours")

            # Review comments per PR
            pr_comments = []
            for pr in report.prs:
                if hasattr(pr, "review_metrics"):
                    if hasattr(pr.review_metrics, "number_of_comments"):
                        pr_comments.append(pr.review_metrics.number_of_comments)

            if pr_comments:
                ax2.hist(pr_comments, bins=min(10, len(pr_comments)))
                ax2.set_title("Comments per PR")
                ax2.set_xlabel("Number of Comments")

            fig.tight_layout()
            canvas.draw()

        except Exception as e:
            self._handle_chart_error("review metrics", e)

    def update_contributor_charts(self, report: RepositoryReport):
        frame = self.tab_manager.frames["contributors"]["chart"]
        fig, canvas = self.chart_manager.create_chart(frame)

        try:
            ax = fig.add_subplot(111)

            # Contributor activity
            contributors = list(report.contributors.keys())
            prs_authored = [report.contributors[c].prs_authored for c in contributors]
            reviews_given = [report.contributors[c].reviews_given for c in contributors]

            x = range(len(contributors))
            width = 0.35

            ax.bar(
                [i - width / 2 for i in x], prs_authored, width, label="PRs Authored"
            )
            ax.bar(
                [i + width / 2 for i in x], reviews_given, width, label="Reviews Given"
            )

            ax.set_ylabel("Count")
            ax.set_title("Contributor Activity")
            ax.set_xticks(x)
            ax.set_xticklabels(contributors, rotation=45)
            ax.legend()

            fig.tight_layout()
            canvas.draw()

        except Exception as e:
            self._handle_chart_error("contributor", e)

    def update_velocity_charts(self, report: RepositoryReport):
        weekly_metrics = calculate_weekly_metrics(report.prs)
        if not weekly_metrics:
            return

        # Update throughput chart
        throughput_frame = self.tab_manager.frames["velocity"]["team_throughput"]
        throughput_fig, throughput_canvas = self.chart_manager.create_chart(
            throughput_frame
        )

        try:
            ax1 = throughput_fig.add_subplot(211)
            ax2 = throughput_fig.add_subplot(212)

            # Plot weekly PR completions
            weeks = [m.week_start for m in weekly_metrics]
            completed_prs = [m.completed_prs for m in weekly_metrics]
            completed_changes = [m.completed_changes for m in weekly_metrics]

            ax1.bar(weeks, completed_prs, color="#3498db")
            ax1.set_title("Weekly Completed PRs")
            ax1.tick_params(axis="x", rotation=45)

            ax2.bar(weeks, completed_changes, color="#2ecc71")
            ax2.set_title("Weekly Code Changes")
            ax2.tick_params(axis="x", rotation=45)

            throughput_fig.tight_layout()
            throughput_canvas.draw()

        except Exception as e:
            self._handle_chart_error("throughput", e)

        # Update cycle time chart
        cycle_frame = self.tab_manager.frames["velocity"]["cycle_time"]
        cycle_fig, cycle_canvas = self.chart_manager.create_chart(cycle_frame)

        try:
            ax3 = cycle_fig.add_subplot(211)
            ax4 = cycle_fig.add_subplot(212)

            # Plot time metrics
            review_times = [m.avg_review_time for m in weekly_metrics]
            cycle_times = [m.avg_cycle_time for m in weekly_metrics]

            ax3.plot(weeks, review_times, marker="o", color="#e74c3c")
            ax3.set_title("Average Review Time")
            ax3.set_ylabel("Hours")
            ax3.tick_params(axis="x", rotation=45)
            ax3.grid(True, alpha=0.3)

            ax4.plot(weeks, cycle_times, marker="o", color="#9b59b6")
            ax4.set_title("Average Cycle Time")
            ax4.set_ylabel("Hours")
            ax4.tick_params(axis="x", rotation=45)
            ax4.grid(True, alpha=0.3)

            cycle_fig.tight_layout()
            cycle_canvas.draw()

        except Exception as e:
            self._handle_chart_error("cycle time", e)

    def _handle_chart_error(self, chart_type: str, error: Exception):
        print(f"Error updating {chart_type} charts: {error}")
        import traceback

        traceback.print_exc()
