import tkinter as tk
from tkinter import ttk


class MetricsManager:
    def __init__(self):
        self.metrics = {}
        self.trends = {}
        self.sparklines = {}

    def create_metrics_section(self, parent):
        metrics_frame = ttk.LabelFrame(parent, text="Current Metrics")
        metrics_frame.pack(fill=tk.X, padx=5, pady=5)

        metrics_grid = ttk.Frame(metrics_frame)
        metrics_grid.pack(fill=tk.X, padx=5, pady=5)

        metrics = [
            ("total_prs", "Total PRs"),
            ("merge_rate", "Merge Rate"),
            ("cycle_time", "Cycle Time"),
            ("review_time", "Review Time"),
            ("contributors", "Contributors"),
        ]

        for row, (metric_id, label) in enumerate(metrics):
            # Label
            ttk.Label(metrics_grid, text=f"{label}:").grid(
                row=row, column=0, sticky="e", padx=5
            )

            # Value
            value_label = ttk.Label(metrics_grid, text="-")
            value_label.grid(row=row, column=1, sticky="w", padx=5)
            self.metrics[metric_id] = value_label

            # Trend
            trend_label = ttk.Label(metrics_grid, text="")
            trend_label.grid(row=row, column=2, sticky="w")
            self.trends[metric_id] = trend_label

            # Sparkline
            sparkline = tk.Canvas(metrics_grid, width=50, height=20)
            sparkline.grid(row=row, column=3, sticky="w", padx=5)
            self.sparklines[metric_id] = sparkline

        return metrics_frame

    def update_metric(
        self, metric_id, value, trend=None, sparkline_data=None, chart_manager=None
    ):
        if metric_id not in self.metrics:
            return

        # Update value
        self.metrics[metric_id].config(text=str(value))

        # Update trend if provided
        if trend is not None:
            color = "#2ecc71" if trend > 0 else "#e74c3c"
            symbol = "↑" if trend > 0 else "↓"
            self.trends[metric_id].config(
                text=f"{symbol} {abs(trend):.1f}%", foreground=color
            )

        # Update sparkline if provided
        if sparkline_data and chart_manager:
            chart_manager.update_sparkline(
                self.sparklines[metric_id], sparkline_data, color
            )

    def clear_all(self):
        for metric in self.metrics.values():
            metric.config(text="-")
        for trend in self.trends.values():
            trend.config(text="")
        for sparkline in self.sparklines.values():
            sparkline.delete("all")
