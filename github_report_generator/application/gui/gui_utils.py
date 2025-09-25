import tkinter as tk
from tkinter import ttk


class GUIUtils:
    @staticmethod
    def create_labeled_entry(parent, label_text, default_value="", show=None):
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, padx=5, pady=5)

        label = ttk.Label(frame, text=label_text)
        label.pack(side=tk.LEFT)

        entry = ttk.Entry(frame, show=show)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))

        if default_value:
            entry.insert(0, default_value)

        return frame, label, entry

    @staticmethod
    def create_quick_select_buttons(parent, entry, values):
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, padx=5)

        for value in values:
            ttk.Button(
                frame,
                text=f"{value}d",
                width=3,
                command=lambda v=value: (
                    entry.delete(0, tk.END),
                    entry.insert(0, str(v)),
                ),
            ).pack(side=tk.LEFT, padx=2)

        return frame

    @staticmethod
    def create_progress_section(parent):
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, padx=5, pady=5)

        status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(frame, textvariable=status_var)
        status_label.pack(side=tk.LEFT, padx=5)

        progress_var = tk.DoubleVar()
        progress = ttk.Progressbar(
            frame, variable=progress_var, maximum=100, length=200
        )
        progress.pack(side=tk.LEFT, padx=5)
        progress.pack_forget()

        return frame, status_var, progress_var, progress

    @staticmethod
    def create_tooltip(widget, text: str, delay_ms: int = 500):
        Tooltip(widget, text, delay=delay_ms)


class Tooltip:
    def __init__(self, widget, text: str, delay: int = 500):
        self.widget = widget
        self.text = text
        self.delay = delay
        self._id = None
        self._tipwindow = None

        self.widget.bind("<Enter>", self._schedule)
        self.widget.bind("<Leave>", self._hide)
        self.widget.bind("<ButtonPress>", self._hide)

    def _schedule(self, _event=None):
        self._unschedule()
        self._id = self.widget.after(self.delay, self._show)

    def _unschedule(self):
        if self._id is not None:
            self.widget.after_cancel(self._id)
            self._id = None

    def _show(self):
        if self._tipwindow or not self.text:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 10
        self._tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = ttk.Label(
            tw, text=self.text, relief=tk.SOLID, borderwidth=1, padding=(5, 3)
        )
        label.pack()

    def _hide(self, _event=None):
        self._unschedule()
        tw = self._tipwindow
        if tw is not None:
            tw.destroy()
            self._tipwindow = None
