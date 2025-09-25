import tkinter as tk
from typing import Optional

from ...domain.management.chart_manager import ChartManager
from ...domain.management.config_manager import ConfigManager
from ...infrastructure.error.error_handler import ErrorHandler
from ...domain.management.event_manager import EventManager
from ...domain.management.progress_manager import ProgressManager
from ...domain.management.report_manager import ReportManager
from .chart_updater import ChartUpdater
from .gui_utils import GUIUtils
from .input_validator import InputValidator
from .metrics_updater import MetricsUpdater
from .tab_manager import TabManager
from .window_manager import WindowManager


class ReportGeneratorGUI:
    def __init__(self):
        # Initialize core managers
        self.window_manager = WindowManager()
        self.config_manager = ConfigManager()
        self.event_manager = EventManager()

        # Initialize UI managers
        self.tab_manager = TabManager(self.window_manager.get_notebook())
        self.chart_manager = ChartManager()
        self.chart_updater = ChartUpdater(self.tab_manager, self.chart_manager)
        self.metrics_updater = MetricsUpdater(self.tab_manager)
        self.progress_manager = ProgressManager(
            self.window_manager.get_main_container()
        )

        # Initialize data managers
        self.report_manager = ReportManager(self.progress_manager)

        # Initialize state
        self.repo_entry: Optional[tk.Entry] = None
        self.token_entry: Optional[tk.Entry] = None
        self.days_entry: Optional[tk.Entry] = None
        self.input_validator: Optional[InputValidator] = None

        # Set up GUI
        self._setup_gui()

    def _setup_gui(self) -> None:
        # Create GUI elements
        self.tab_manager.create_tabs()
        self._create_input_frame()

        # Set up event handlers
        self._setup_event_handlers()

        # Load saved configuration
        self._load_config()

    def _setup_event_handlers(self) -> None:
        self.window_manager.set_close_handler(self._on_close)
        self.tab_manager.bind_tab_change(
            lambda e: self.event_manager.on_tab_change(
                self.tab_manager, self.chart_updater, self.report_manager
            )
        )

    def _create_input_frame(self) -> None:
        input_frame = tk.LabelFrame(
            self.window_manager.get_main_container(), text="Repository Configuration"
        )
        input_frame.pack(fill=tk.X, pady=(0, 10))
        self._create_input_fields(input_frame)
        self._create_options_frame(input_frame)

        self.input_validator = InputValidator(
            self.repo_entry, self.days_entry, self.token_entry
        )

    def _create_input_fields(self, parent: tk.Widget) -> None:
        # Repository input
        repo_frame, _, self.repo_entry = GUIUtils.create_labeled_entry(
            parent,
            "Repository:",
            "test-org/sample-project",
        )

        # Token input
        token_frame, _, self.token_entry = GUIUtils.create_labeled_entry(
            parent,
            "GitHub Token:",
            "",
            show="*",
        )

        # Days input
        days_frame, _, self.days_entry = GUIUtils.create_labeled_entry(
            parent, "Days to analyze:", "30"
        )

        # Add quick select buttons
        GUIUtils.create_quick_select_buttons(days_frame, self.days_entry, [7, 30, 90])

    def _create_options_frame(self, parent: tk.Widget) -> None:
        options_frame = tk.Frame(parent)
        options_frame.pack(fill=tk.X, padx=5, pady=5)

        # Generate button
        generate_btn = tk.Button(
            options_frame, text="Generate Report", command=self._generate_report
        )
        generate_btn.pack(side=tk.RIGHT)
        GUIUtils.create_tooltip(generate_btn, "Click to generate the repository report")

    def _generate_report(self) -> None:
        try:
            if not self.input_validator.validate_all():
                return

            repo_name = self.repo_entry.get().strip()
            token = self.token_entry.get() or None
            days = int(self.days_entry.get())
            # Generate report
            self.report_manager.generate_report(
                repo_name=repo_name,
                days=days,
                token=token,
                on_complete=lambda: self.event_manager.on_report_complete(
                    self.metrics_updater, self.chart_updater, self.report_manager
                ),
            )

        except Exception as e:
            ErrorHandler.handle_gui_error(e, "generating report")

    def _on_close(self) -> None:
        try:
            # Save configuration
            self.event_manager.on_config_change(
                self.config_manager,
                repo=self.repo_entry.get(),
                days=self.days_entry.get(),
            )

            # Clean up and close
            self.window_manager.cleanup()

        except Exception as e:
            ErrorHandler.handle_gui_error(
                e, "closing application", callback=lambda: self.window_manager.cleanup()
            )

    def _load_config(self) -> None:
        try:
            config = self.config_manager.load_config()

            # Update input fields
            self.repo_entry.delete(0, tk.END)
            self.repo_entry.insert(0, config.get("repo", "owner/repo"))

            self.days_entry.delete(0, tk.END)
            self.days_entry.insert(0, config.get("days", "30"))

        except Exception as e:
            ErrorHandler.handle_gui_error(e, "loading configuration")

    def run(self) -> None:
        try:
            self.window_manager.run()
        except Exception as e:
            ErrorHandler.handle_gui_error(e, "running application")


def main() -> None:
    app = ReportGeneratorGUI()
    app.run()


if __name__ == "__main__":
    main()
