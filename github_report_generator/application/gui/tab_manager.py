import tkinter as tk
from tkinter import ttk


class TabConfig:

    TABS = {
        "overview": {
            "title": "Overview",
            "frames": [
                {"type": "summary", "title": "Summary"},
                {"type": "chart", "title": "Key Metrics"},
            ],
        },
        "pr_metrics": {
            "title": "PR Metrics",
            "frames": [{"type": "chart", "title": "PR Size Distribution"}],
        },
        "review_metrics": {
            "title": "Review Metrics",
            "frames": [{"type": "chart", "title": "Review Times"}],
        },
        "contributors": {
            "title": "Contributors",
            "frames": [{"type": "chart", "title": "Contributor Activity"}],
        },
        "velocity": {
            "title": "Velocity",
            "frames": [
                {"type": "metrics", "title": "Current Metrics"},
                {"type": "chart", "title": "Team Throughput"},
                {"type": "chart", "title": "Cycle Time"},
            ],
        },
    }


class TabManager:
    def __init__(self, notebook):
        self.notebook = notebook
        self.tabs = {}
        self.frames = {}
        self.summary_text = None
        self.metrics_grid = None
        self.metrics_labels = {}
        self.trend_labels = {}
        self.sparklines = {}

    def create_tabs(self):
        for tab_id, config in TabConfig.TABS.items():
            tab = ttk.Frame(self.notebook)
            self.notebook.add(tab, text=config["title"])
            self.tabs[tab_id] = tab
            self.frames[tab_id] = {}

            for frame_config in config["frames"]:
                if frame_config["type"] == "summary":
                    self._create_summary_frame(tab_id, tab)
                elif frame_config["type"] == "metrics":
                    self._create_metrics_frame(tab_id, tab)
                elif frame_config["type"] == "chart":
                    self._create_chart_frame(tab_id, tab, frame_config["title"])

    def _create_summary_frame(self, tab_id: str, tab: ttk.Frame):
        frame = ttk.LabelFrame(tab, text="Summary")
        frame.pack(fill=tk.X, padx=5, pady=5)

        text = tk.Text(frame, height=10)
        text.pack(fill=tk.X, padx=5, pady=5)

        self.frames[tab_id]["summary"] = frame
        self.summary_text = text

    def _create_metrics_frame(self, tab_id: str, tab: ttk.Frame):
        frame = ttk.LabelFrame(tab, text="Current Metrics")
        frame.pack(fill=tk.X, padx=5, pady=5)

        grid = ttk.Frame(frame)
        grid.pack(fill=tk.X, padx=5, pady=5)

        metrics = [
            ("total_prs", "Total PRs"),
            ("merge_rate", "Merge Rate"),
            ("cycle_time", "Cycle Time"),
            ("review_time", "Review Time"),
            ("contributors", "Contributors"),
        ]

        for row, (metric_id, label) in enumerate(metrics):
            ttk.Label(grid, text=f"{label}:").grid(
                row=row, column=0, sticky="e", padx=5
            )

            # Value label
            value_label = ttk.Label(grid, text="-")
            value_label.grid(row=row, column=1, sticky="w", padx=5)
            self.metrics_labels[metric_id] = value_label

            # Trend label
            trend_label = ttk.Label(grid, text="")
            trend_label.grid(row=row, column=2, sticky="w")
            self.trend_labels[metric_id] = trend_label

            # Sparkline
            sparkline = tk.Canvas(grid, width=50, height=20)
            sparkline.grid(row=row, column=3, sticky="w", padx=5)
            self.sparklines[metric_id] = sparkline

        self.frames[tab_id]["metrics"] = frame
        self.metrics_grid = grid

    def _create_chart_frame(self, tab_id: str, tab: ttk.Frame, title: str):
        frame = ttk.LabelFrame(tab, text=title)
        frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        if tab_id == "velocity":
            # Velocity tab has multiple chart frames
            frame_id = title.lower().replace(" ", "_")
            self.frames[tab_id][frame_id] = frame
        else:
            self.frames[tab_id]["chart"] = frame

    def get_tab(self, tab_id):
        return self.tabs.get(tab_id)

    def get_chart_frame(self, tab_id):
        if tab_id == "velocity":
            raise ValueError("Velocity tab has multiple chart frames. Use get_velocity_chart_frames() instead.")
        frames_for_tab = self.frames.get(tab_id, {})
        frame = frames_for_tab.get("chart")
        if frame is None:
            raise KeyError(f"Chart frame not found for tab: {tab_id}")
        return frame

    def get_velocity_chart_frames(self, frame_id: str):
        frames_for_velocity = self.frames.get("velocity", {})
        frame = frames_for_velocity.get(frame_id)
        if frame is None:
            raise KeyError(f"Velocity chart frame not found for ID: {frame_id}")
        return frame
        
    def get_current_tab(self):
        current = self.notebook.select()
        return self.notebook.tab(current, "text")

    def bind_tab_change(self, callback):
        self.notebook.bind("<<NotebookTabChanged>>", callback)
