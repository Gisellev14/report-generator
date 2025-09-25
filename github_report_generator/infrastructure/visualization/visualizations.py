import plotly.graph_objects as go
from plotly.subplots import make_subplots

from ...domain.model.models import RepositoryReport


class BaseChart:
    def __init__(self):
        self.default_colors = {
            "primary": "#3498db",
            "success": "#2ecc71",
            "warning": "#f1c40f",
            "danger": "#e74c3c",
            "info": "#9b59b6",
        }
        self.default_layout = {
            "showlegend": True,
            "margin": dict(l=40, r=40, t=40, b=40),
        }

    def apply_common_styling(self, fig: go.Figure) -> None:
        fig.update_layout(**self.default_layout)

    def create_figure(self, **kwargs) -> go.Figure:
        raise NotImplementedError


class PRSizeChart(BaseChart):
    def create_figure(self, report: RepositoryReport) -> go.Figure:
        sizes = []
        counts = []

        for size, count in report.pr_size_distribution.items():
            if count > 0:
                sizes.append(size.upper())
                counts.append(count)

        fig = go.Figure(
            data=[
                go.Pie(
                    labels=sizes,
                    values=counts,
                    hole=0.4,
                    textinfo="label+percent",
                    marker=dict(colors=list(self.default_colors.values())),
                )
            ]
        )

        fig.update_layout(title="Pull Request Size Distribution")
        self.apply_common_styling(fig)
        return fig


class ReviewTimeChart(BaseChart):
    def create_figure(self, report: RepositoryReport) -> go.Figure:
        first_review_times = []
        approval_times = []

        for pr in report.prs:
            if pr.review_metrics.time_to_first_review is not None:
                first_review_times.append(pr.review_metrics.time_to_first_review)
            if pr.review_metrics.time_to_approval is not None:
                approval_times.append(pr.review_metrics.time_to_approval)

        fig = go.Figure()

        fig.add_trace(
            go.Box(
                y=first_review_times,
                name="Time to First Review",
                marker_color=self.default_colors["primary"],
            )
        )

        fig.add_trace(
            go.Box(
                y=approval_times,
                name="Time to Approval",
                marker_color=self.default_colors["success"],
            )
        )

        fig.update_layout(title="Review Time Distribution (hours)")
        self.apply_common_styling(fig)
        return fig


class VelocityChart(BaseChart):
    def create_figure(self, report: RepositoryReport) -> tuple[go.Figure, go.Figure]:
        from .velocity import calculate_weekly_metrics

        if not report.weekly_metrics:
            report.weekly_metrics = calculate_weekly_metrics(report.prs)

        throughput_fig = self._create_throughput_chart(report)
        cycle_fig = self._create_cycle_time_chart(report)

        return throughput_fig, cycle_fig

    def _create_throughput_chart(self, report: RepositoryReport) -> go.Figure:
        fig = make_subplots(
            rows=2,
            cols=1,
            subplot_titles=("Weekly Completed PRs", "Weekly Code Changes"),
        )

        weeks = [m.week_start for m in report.weekly_metrics]
        completed_prs = [m.completed_prs for m in report.weekly_metrics]
        completed_changes = [m.completed_changes for m in report.weekly_metrics]

        fig.add_trace(
            go.Bar(
                x=weeks,
                y=completed_prs,
                name="Completed PRs",
                marker_color=self.default_colors["primary"],
            ),
            row=1,
            col=1,
        )

        fig.add_trace(
            go.Bar(
                x=weeks,
                y=completed_changes,
                name="Code Changes",
                marker_color=self.default_colors["success"],
            ),
            row=2,
            col=1,
        )

        fig.update_layout(title="Team Throughput Metrics")
        self.apply_common_styling(fig)
        return fig

    def _create_cycle_time_chart(self, report: RepositoryReport) -> go.Figure:
        fig = make_subplots(
            rows=2, cols=1, subplot_titles=("Average Review Time", "Average Cycle Time")
        )

        weeks = [m.week_start for m in report.weekly_metrics]
        review_times = [m.avg_review_time for m in report.weekly_metrics]
        cycle_times = [m.avg_cycle_time for m in report.weekly_metrics]

        fig.add_trace(
            go.Scatter(
                x=weeks,
                y=review_times,
                name="Review Time",
                mode="lines+markers",
                line=dict(color=self.default_colors["danger"]),
            ),
            row=1,
            col=1,
        )

        fig.add_trace(
            go.Scatter(
                x=weeks,
                y=cycle_times,
                name="Cycle Time",
                mode="lines+markers",
                line=dict(color=self.default_colors["info"]),
            ),
            row=2,
            col=1,
        )

        fig.update_layout(title="Time Metrics Trends")
        self.apply_common_styling(fig)
        return fig


def create_pr_size_chart(report: RepositoryReport) -> go.Figure:
    sizes = []
    counts = []

    for size, count in report.pr_size_distribution.items():
        if count > 0:
            sizes.append(size.upper())
            counts.append(count)

    fig = go.Figure(
        data=[
            go.Pie(
                labels=sizes,
                values=counts,
                hole=0.4,
                textinfo="label+percent",
                marker=dict(
                    colors=["#2ecc71", "#3498db", "#9b59b6", "#e74c3c", "#f1c40f"]
                ),
            )
        ]
    )

    fig.update_layout(
        title="Pull Request Size Distribution", showlegend=True, width=600, height=400
    )

    return fig


def create_review_time_chart(report: RepositoryReport) -> go.Figure:
    first_review_times = []
    approval_times = []

    for pr in report.prs:
        if pr.review_metrics.time_to_first_review is not None:
            first_review_times.append(pr.review_metrics.time_to_first_review)
        if pr.review_metrics.time_to_approval is not None:
            approval_times.append(pr.review_metrics.time_to_approval)

    fig = go.Figure()

    fig.add_trace(
        go.Box(
            y=first_review_times,
            name="Time to First Review",
            boxpoints="all",
            marker_color="#3498db",
        )
    )

    fig.add_trace(
        go.Box(
            y=approval_times,
            name="Time to Approval",
            boxpoints="all",
            marker_color="#2ecc71",
        )
    )

    fig.update_layout(
        title="Review Time Distribution (hours)",
        yaxis_title="Hours",
        showlegend=True,
        width=800,
        height=400,
    )

    return fig


def create_contributor_heatmap(report: RepositoryReport) -> go.Figure:
    contributors = list(report.contributors.keys())
    metrics = ["PRs Authored", "PRs Merged", "Reviews Given", "Reviews Received"]

    data = []
    for contributor in contributors:
        stats = report.contributors[contributor]
        data.append(
            [
                stats.prs_authored,
                stats.prs_merged,
                stats.reviews_given,
                stats.reviews_received,
            ]
        )

    fig = go.Figure(
        data=go.Heatmap(
            z=data, x=metrics, y=contributors, colorscale="Viridis", showscale=True
        )
    )

    fig.update_layout(
        title="Contributor Activity Heatmap",
        width=800,
        height=400 + (len(contributors) * 30),
    )

    return fig


def create_velocity_charts(report: RepositoryReport) -> tuple[go.Figure, go.Figure]:
    chart = VelocityChart()
    return chart.create_figure(report)


def generate_html_report(report: RepositoryReport) -> str:
    # Create figures
    size_chart = create_pr_size_chart(report)
    review_chart = create_review_time_chart(report)
    activity_chart = create_contributor_heatmap(report)
    throughput_chart, cycle_chart = create_velocity_charts(report)

    # Create HTML template
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>GitHub Repository Report - {report.repo_name}</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
            body {{
                font-family: Arial, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }}
            .header {{
                text-align: center;
                margin-bottom: 30px;
            }}
            .chart-container {{
                margin-bottom: 40px;
            }}
            .metrics {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-bottom: 40px;
            }}
            .metric-card {{
                background: #f8f9fa;
                padding: 20px;
                border-radius: 8px;
                text-align: center;
            }}
            .metric-value {{
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
            }}
            .metric-label {{
                color: #7f8c8d;
                margin-top: 5px;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>GitHub Repository Report</h1>
            <h2>{report.repo_name}</h2>
            <p>Period: {report.period_start.strftime("%Y-%m-%d")} to {report.period_end.strftime("%Y-%m-%d")}</p>
        </div>
        
        <div class="metrics">
            <div class="metric-card">
                <div class="metric-value">{report.total_prs}</div>
                <div class="metric-label">Total PRs</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{report.prs_merged}</div>
                <div class="metric-label">Merged PRs</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{len(report.contributors)}</div>
                <div class="metric-label">Contributors</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{f"{report.median_cycle_time:.1f}h" if report.median_cycle_time is not None else "N/A"}</div>
                <div class="metric-label">Median Cycle Time</div>
            </div>
        </div>
        
        <div class="chart-container">
            <div id="size-chart"></div>
        </div>
        
        <div class="chart-container">
            <div id="review-chart"></div>
        </div>
        
        <div class="chart-container">
            <div id="activity-chart"></div>
        </div>

        <div class="chart-container">
            <div id="throughput-chart"></div>
        </div>

        <div class="chart-container">
            <div id="cycle-chart"></div>
        </div>
        
        <script>
            {size_chart.to_json()}
            Plotly.newPlot('size-chart', size_chart.data, size_chart.layout);
            
            {review_chart.to_json()}
            Plotly.newPlot('review-chart', review_chart.data, review_chart.layout);
            
            {activity_chart.to_json()}
            Plotly.newPlot('activity-chart', activity_chart.data, activity_chart.layout);
            
            {throughput_chart.to_json()}
            Plotly.newPlot('throughput-chart', throughput_chart.data, throughput_chart.layout);
            
            {cycle_chart.to_json()}
            Plotly.newPlot('cycle-chart', cycle_chart.data, cycle_chart.layout);
        </script>
    </body>
    </html>
    """

    return html
