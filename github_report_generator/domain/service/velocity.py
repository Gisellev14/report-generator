from datetime import timedelta
from typing import List, Tuple

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from ..model.models import PullRequest, RepositoryReport, WeeklyMetrics


def calculate_weekly_metrics(prs: List[PullRequest]) -> List[WeeklyMetrics]:
    # Group PRs by week
    weekly_data = {}

    for pr in prs:
        # Use merged_at for completed work
        if pr.merged_at:
            week_key = pr.merged_at.isocalendar()[:2]  # (year, week)
            week_start = pr.merged_at - timedelta(days=pr.merged_at.weekday())

            if week_key not in weekly_data:
                weekly_data[week_key] = {
                    "week_start": week_start,
                    "completed_prs": 0,
                    "completed_changes": 0,
                    "review_times": [],
                    "cycle_times": [],
                    "contributors": set(),
                    "total_reviews": 0,
                    "total_comments": 0,
                }

            data = weekly_data[week_key]
            data["completed_prs"] += 1
            data["completed_changes"] += pr.additions + pr.deletions
            data["contributors"].add(pr.author)
            data["total_reviews"] += len(pr.reviewers)

            if pr.review_metrics:
                data["total_comments"] += pr.review_metrics.number_of_comments
                if pr.review_metrics.time_to_approval is not None:
                    data["review_times"].append(pr.review_metrics.time_to_approval)

            if pr.created_at:
                cycle_time = (pr.merged_at - pr.created_at).total_seconds() / 3600
                data["cycle_times"].append(cycle_time)

    # Convert to WeeklyMetrics objects
    result = []
    prev_metrics = None

    for week_key, data in sorted(weekly_data.items()):
        avg_review_time = (
            sum(data["review_times"]) / len(data["review_times"])
            if data["review_times"]
            else None
        )
        avg_cycle_time = (
            sum(data["cycle_times"]) / len(data["cycle_times"])
            if data["cycle_times"]
            else None
        )

        # Calculate trends
        throughput_trend = None
        cycle_time_trend = None

        if prev_metrics:
            # Throughput trend (percentage change)
            throughput_trend = (
                (data["completed_prs"] - prev_metrics.completed_prs)
                / prev_metrics.completed_prs
                * 100
                if prev_metrics.completed_prs > 0
                else 0
            )

            # Cycle time trend (percentage change, negative = improving)
            if avg_cycle_time is not None and prev_metrics.avg_cycle_time is not None:
                cycle_time_trend = (
                    (avg_cycle_time - prev_metrics.avg_cycle_time)
                    / prev_metrics.avg_cycle_time
                    * 100
                )

        metrics = WeeklyMetrics(
            week_start=data["week_start"],
            completed_prs=data["completed_prs"],
            completed_changes=data["completed_changes"],
            avg_review_time=avg_review_time,
            avg_cycle_time=avg_cycle_time,
            active_contributors=len(data["contributors"]),
            total_reviews=data["total_reviews"],
            total_comments=data["total_comments"],
            throughput_trend=throughput_trend,
            cycle_time_trend=cycle_time_trend,
        )

        result.append(metrics)
        prev_metrics = metrics

    return result


def create_velocity_charts(report: RepositoryReport) -> Tuple[go.Figure, go.Figure]:
    # Calculate metrics if not already present
    if not report.weekly_metrics:
        report.weekly_metrics = calculate_weekly_metrics(report.prs)

    # Throughput chart
    throughput_fig = make_subplots(
        rows=2,
        cols=1,
        subplot_titles=("Weekly Completed PRs", "Weekly Code Changes"),
        vertical_spacing=0.15,
    )

    # Add weekly PR completions with trend indicators
    weeks = [m.week_start for m in report.weekly_metrics]
    completed_prs = [m.completed_prs for m in report.weekly_metrics]
    completed_changes = [m.completed_changes for m in report.weekly_metrics]
    throughput_trends = [m.throughput_trend for m in report.weekly_metrics]

    # PR completions with trend colors
    colors = [
        "#3498db"
        if trend is None
        else "#2ecc71"
        if trend > 0
        else "#e74c3c"
        if trend < 0
        else "#3498db"
        for trend in throughput_trends
    ]

    throughput_fig.add_trace(
        go.Bar(
            x=weeks,
            y=completed_prs,
            name="Completed PRs",
            marker_color=colors,
            text=[
                f"{prs} PRs<br>{'+' if trend > 0 else ''}{trend:.1f}%"
                if trend is not None
                else f"{prs} PRs"
                for prs, trend in zip(completed_prs, throughput_trends)
            ],
            textposition="auto",
        ),
        row=1,
        col=1,
    )

    # Code changes
    throughput_fig.add_trace(
        go.Bar(
            x=weeks, y=completed_changes, name="Code Changes", marker_color="#2ecc71"
        ),
        row=2,
        col=1,
    )

    throughput_fig.update_layout(
        title="Team Throughput Metrics", showlegend=True, height=600, width=800
    )

    # Cycle time chart
    cycle_fig = make_subplots(
        rows=2,
        cols=1,
        subplot_titles=("Average Review Time", "Average Cycle Time"),
        vertical_spacing=0.15,
    )

    # Add review time trend
    review_times = [m.avg_review_time for m in report.weekly_metrics]
    cycle_times = [m.avg_cycle_time for m in report.weekly_metrics]
    cycle_trends = [m.cycle_time_trend for m in report.weekly_metrics]

    # Review time line with trend colors
    cycle_fig.add_trace(
        go.Scatter(
            x=weeks,
            y=review_times,
            name="Review Time",
            mode="lines+markers",
            line=dict(color="#e74c3c"),
            text=[f"{time:.1f}h" for time in review_times],
            textposition="top center",
        ),
        row=1,
        col=1,
    )

    # Cycle time line with trend indicators
    cycle_fig.add_trace(
        go.Scatter(
            x=weeks,
            y=cycle_times,
            name="Cycle Time",
            mode="lines+markers",
            line=dict(color="#9b59b6"),
            text=[
                f"{time:.1f}h<br>{'+' if trend < 0 else ''}{abs(trend):.1f}%"
                if trend is not None
                else f"{time:.1f}h"
                for time, trend in zip(cycle_times, cycle_trends)
            ],
            textposition="top center",
        ),
        row=2,
        col=1,
    )

    # Add trend arrows
    for i, trend in enumerate(cycle_trends):
        if trend is not None and i < len(cycle_times) - 1:
            cycle_fig.add_annotation(
                x=weeks[i],
                y=cycle_times[i],
                text="⬆" if trend < 0 else "⬇",
                showarrow=False,
                yshift=10,
                font=dict(size=16, color="#2ecc71" if trend < 0 else "#e74c3c"),
            )

    cycle_fig.update_layout(
        title="Time Metrics Trends",
        showlegend=True,
        height=600,
        width=800,
        yaxis_title="Hours",
        yaxis2_title="Hours",
    )

    return throughput_fig, cycle_fig
