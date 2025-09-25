from typing import List, Optional, Tuple

from ...domain.model.models import RepositoryReport, WeeklyMetrics
from ...domain.service.velocity import calculate_weekly_metrics


class MetricsUpdater:
    def __init__(self, tab_manager):
        self.tab_manager = tab_manager

    def update_metrics(self, report: RepositoryReport):
        if not report:
            return

        weekly_metrics = calculate_weekly_metrics(report.prs)
        if not weekly_metrics:
            return

        latest = weekly_metrics[-1]
        prev = weekly_metrics[-2] if len(weekly_metrics) > 1 else None

        # Update total PRs
        self._update_pr_metrics(report, latest, prev, weekly_metrics)

        # Update merge rate
        self._update_merge_rate(report, latest, prev, weekly_metrics)

        # Update cycle time
        self._update_cycle_time(latest, prev, weekly_metrics)

        # Update review time
        self._update_review_time(latest, prev, weekly_metrics)

        # Update contributors
        self._update_contributor_metrics(report, latest, prev, weekly_metrics)

    def _calculate_trend(
        self, current: float, previous: float, inverse: bool = False
    ) -> Tuple[float, str, str]:
        if previous == 0:
            return 0, "#3498db", "="

        trend = (current - previous) / previous * 100
        is_positive = trend > 0

        if inverse:
            is_positive = not is_positive

        color = "#2ecc71" if is_positive else "#e74c3c"
        symbol = "↑" if is_positive else "↓"

        return trend, color, symbol

    def _update_pr_metrics(
        self,
        report: RepositoryReport,
        latest: WeeklyMetrics,
        prev: Optional[WeeklyMetrics],
        weekly_metrics: List[WeeklyMetrics],
    ):
        # Update total PRs value
        self.tab_manager.metrics_labels["total_prs"].config(text=str(report.total_prs))

        if prev:
            # Calculate trend
            trend, color, symbol = self._calculate_trend(
                latest.completed_prs, prev.completed_prs
            )

            # Update trend label
            self.tab_manager.trend_labels["total_prs"].config(
                text=f"{symbol} {abs(trend):.1f}%", foreground=color
            )

            # Update sparkline
            pr_values = [m.completed_prs for m in weekly_metrics[-4:]]
            self.tab_manager.chart_manager.update_sparkline(
                self.tab_manager.sparklines["total_prs"], pr_values, color
            )

    def _update_merge_rate(
        self,
        report: RepositoryReport,
        latest: WeeklyMetrics,
        prev: Optional[WeeklyMetrics],
        weekly_metrics: List[WeeklyMetrics],
    ):
        merge_rate = report.prs_merged / report.total_prs * 100
        self.tab_manager.metrics_labels["merge_rate"].config(text=f"{merge_rate:.1f}%")

        if prev:
            # Calculate previous merge rate
            prev_merged = len(
                [
                    p
                    for p in report.prs
                    if p.merged_at and p.merged_at < latest.week_start
                ]
            )
            prev_total = len(
                [p for p in report.prs if p.created_at < latest.week_start]
            )
            prev_rate = (prev_merged / prev_total * 100) if prev_total > 0 else 0

            # Calculate trend
            trend, color, symbol = self._calculate_trend(merge_rate, prev_rate)

            # Update trend label
            self.tab_manager.trend_labels["merge_rate"].config(
                text=f"{symbol} {abs(trend):.1f}%", foreground=color
            )

            # Update sparkline
            merge_rates = []
            for m in weekly_metrics[-4:]:
                merged = len(
                    [
                        p
                        for p in report.prs
                        if p.merged_at and p.merged_at <= m.week_start
                    ]
                )
                total = len([p for p in report.prs if p.created_at <= m.week_start])
                rate = (merged / total * 100) if total > 0 else 0
                merge_rates.append(rate)

            self.tab_manager.chart_manager.update_sparkline(
                self.tab_manager.sparklines["merge_rate"], merge_rates, color
            )

    def _update_cycle_time(
        self,
        latest: WeeklyMetrics,
        prev: Optional[WeeklyMetrics],
        weekly_metrics: List[WeeklyMetrics],
    ):
        if latest.avg_cycle_time is not None:
            self.tab_manager.metrics_labels["cycle_time"].config(
                text=f"{latest.avg_cycle_time:.1f} hours"
            )

            if prev and prev.avg_cycle_time is not None:
                # Calculate trend (inverse because lower is better)
                trend, color, symbol = self._calculate_trend(
                    latest.avg_cycle_time, prev.avg_cycle_time, inverse=True
                )

                # Update trend label
                self.tab_manager.trend_labels["cycle_time"].config(
                    text=f"{symbol} {abs(trend):.1f}%", foreground=color
                )

                # Update sparkline
                cycle_times = [
                    m.avg_cycle_time
                    for m in weekly_metrics[-4:]
                    if m.avg_cycle_time is not None
                ]
                self.tab_manager.chart_manager.update_sparkline(
                    self.tab_manager.sparklines["cycle_time"], cycle_times, color
                )

    def _update_review_time(
        self,
        latest: WeeklyMetrics,
        prev: Optional[WeeklyMetrics],
        weekly_metrics: List[WeeklyMetrics],
    ):
        if latest.avg_review_time is not None:
            self.tab_manager.metrics_labels["review_time"].config(
                text=f"{latest.avg_review_time:.1f} hours"
            )

            if prev and prev.avg_review_time is not None:
                # Calculate trend (inverse because lower is better)
                trend, color, symbol = self._calculate_trend(
                    latest.avg_review_time, prev.avg_review_time, inverse=True
                )

                # Update trend label
                self.tab_manager.trend_labels["review_time"].config(
                    text=f"{symbol} {abs(trend):.1f}%", foreground=color
                )

                # Update sparkline
                review_times = [
                    m.avg_review_time
                    for m in weekly_metrics[-4:]
                    if m.avg_review_time is not None
                ]
                self.tab_manager.chart_manager.update_sparkline(
                    self.tab_manager.sparklines["review_time"], review_times, color
                )

    def _update_contributor_metrics(
        self,
        report: RepositoryReport,
        latest: WeeklyMetrics,
        prev: Optional[WeeklyMetrics],
        weekly_metrics: List[WeeklyMetrics],
    ):
        self.tab_manager.metrics_labels["contributors"].config(
            text=str(len(report.contributors))
        )

        if prev:
            # Calculate trend
            trend, color, symbol = self._calculate_trend(
                latest.active_contributors, prev.active_contributors
            )

            # Update trend label
            self.tab_manager.trend_labels["contributors"].config(
                text=f"{symbol} {abs(trend):.1f}%", foreground=color
            )

            # Update sparkline
            contributor_counts = [m.active_contributors for m in weekly_metrics[-4:]]
            self.tab_manager.chart_manager.update_sparkline(
                self.tab_manager.sparklines["contributors"], contributor_counts, color
            )
