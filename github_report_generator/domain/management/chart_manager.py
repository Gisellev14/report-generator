import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.pyplot as plt

from ...infrastructure.visualization.visualizations import (
    PRSizeChart,
    ReviewTimeChart,
    VelocityChart,
)


class ChartManager:
    def __init__(self):
        self.default_figsize = (8, 6)
        self.dpi = 100
        self.charts = {
            "pr_size": PRSizeChart(),
            "review_time": ReviewTimeChart(),
            "velocity": VelocityChart(),
        }
        self.canvases = {}

    def create_chart(self, frame, chart_type=None, report=None):
        # Clear existing widgets
        for widget in frame.winfo_children():
            widget.destroy()

        # Default: create an empty figure to return (fig, canvas)
        fig = None

        if chart_type == "velocity" and report:
            throughput_fig, cycle_fig = self.charts["velocity"].create_figure(report)
            self._setup_canvas(frame, throughput_fig, "throughput")
            self._setup_canvas(frame, cycle_fig, "cycle")
            return
        elif chart_type == "pr_size" and report:
            fig = self.charts["pr_size"].create_figure(report)
        elif chart_type == "review_time" and report:
            fig = self.charts["review_time"].create_figure(report)
        else:
            # Generic empty figure if no report or unknown chart type
            fig = plt.Figure(figsize=self.default_figsize, dpi=self.dpi)

        canvas = self._setup_canvas(frame, fig, chart_type or "generic")
        return fig, canvas

    def _setup_canvas(self, frame, fig, name):
        canvas = FigureCanvasTkAgg(fig, master=frame)

        # Create toolbar
        toolbar_frame = ttk.Frame(frame)
        toolbar_frame.pack(side=tk.BOTTOM, fill=tk.X)
        toolbar = NavigationToolbar2Tk(canvas, toolbar_frame)
        toolbar.update()

        # Pack canvas
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        canvas.draw()

        self.canvases[name] = canvas
        return canvas

    def update_sparkline(self, canvas, values, color):
        canvas.delete("all")

        if not values:
            return

        # Normalize values to canvas size
        width = 50
        height = 20
        padding = 2

        min_val = min(values)
        max_val = max(values)
        if min_val == max_val:
            max_val = min_val + 1

        # Scale points to fit canvas
        points = []
        for i, val in enumerate(values):
            x = padding + (width - 2 * padding) * i / (len(values) - 1)
            normalized_val = (val - min_val) / (max_val - min_val)
            y = padding + (height - 2 * padding) * (1 - normalized_val)
            points.append(x)
            points.append(y)

        if len(points) >= 4:
            canvas.create_line(points, fill=color, smooth=True, tags="line")
            x = points[-2]
            y = points[-1]
            canvas.create_oval(
                x - 2, y - 2, x + 2, y + 2, fill=color, outline=color, tags="dot"
            )
        elif len(points) == 2:
            x = points[0]
            y = points[1]
            canvas.create_oval(
                x - 2, y - 2, x + 2, y + 2, fill=color, outline=color, tags="dot"
            )

    def clear_all(self):
        for canvas in self.canvases.values():
            for widget in canvas.get_tk_widget().master.winfo_children():
                widget.destroy()
        self.canvases.clear()

    def update_chart(self, frame, chart_type, data, title=None):
        fig, canvas = self.create_chart(frame)
        ax = fig.add_subplot(111)

        if chart_type == "pie":
            ax.pie(data["values"], labels=data["labels"], autopct="%1.1f%%")
        elif chart_type == "bar":
            ax.bar(data["x"], data["y"], color=data.get("colors"))
        elif chart_type == "line":
            ax.plot(data["x"], data["y"], marker="o")

        if title:
            ax.set_title(title)

        fig.tight_layout()
        canvas.draw()
        return fig, canvas

    def create_sparkline(self, canvas, values, color):
        canvas.delete("all")

        if not values:
            return

        # Normalize values to canvas size
        width = 50
        height = 20
        padding = 2

        min_val = min(values)
        max_val = max(values)
        if min_val == max_val:
            max_val = min_val + 1

        points = []
        for i, val in enumerate(values):
            x = padding + (width - 2 * padding) * i / (len(values) - 1)
            normalized_val = (val - min_val) / (max_val - min_val)
            y = padding + (height - 2 * padding) * (1 - normalized_val)
            points.append(x)
            points.append(y)

        if len(points) >= 4:
            canvas.create_line(points, fill=color, smooth=True, tags="line")
            x = points[-2]
            y = points[-1]
            canvas.create_oval(
                x - 2, y - 2, x + 2, y + 2, fill=color, outline=color, tags="dot"
            )
        elif len(points) == 2:
            x = points[0]
            y = points[1]
            canvas.create_oval(
                x - 2, y - 2, x + 2, y + 2, fill=color, outline=color, tags="dot"
            )
