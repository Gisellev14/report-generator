import tkinter as tk
from tkinter import ttk


class ProgressManager:
    def __init__(self, parent):
        self.frame = ttk.Frame(parent)
        self.frame.pack(fill=tk.X, padx=5, pady=5)

        # Status label
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(self.frame, textvariable=self.status_var)
        self.status_label.pack(side=tk.LEFT, padx=5)

        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(
            self.frame, variable=self.progress_var, maximum=100, length=200
        )
        self.progress.pack(side=tk.LEFT, padx=5)
        self.progress.pack_forget()

    def update_status(self, message: str, show_progress: bool = False):
        self.status_var.set(message)

        if show_progress:
            self.progress.pack(side=tk.LEFT, padx=5)
            self.progress_var.set(0)
        else:
            self.progress.pack_forget()

    def update_progress(self, value: float):
        self.progress_var.set(value)

    def hide_progress(self, delay_ms: int = 3000):
        self.frame.after(delay_ms, self.progress.pack_forget)
        self.frame.after(delay_ms, lambda: self.status_var.set("Ready"))

    def show_error(self, message: str):
        self.status_var.set(f"Error: {message}")
        self.progress.pack_forget()
