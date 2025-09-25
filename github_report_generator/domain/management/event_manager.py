from typing import Callable, Dict, List


class EventManager:
    def __init__(self):
        self.handlers: Dict[str, List[Callable]] = {
            "tab_change": [],
            "report_complete": [],
            "report_error": [],
            "config_change": [],
        }

    def on_tab_change(self, tab_manager, chart_updater, report_manager):
        report = report_manager.get_report()

        if report:
            chart_updater.update_charts(report)

    def on_report_complete(self, metrics_updater, chart_updater, report_manager):
        report = report_manager.get_report()
        if report:
            metrics_updater.update_metrics(report)
            chart_updater.update_charts(report)

    def on_config_change(self, config_manager, **kwargs):
        config_manager.update_config(**kwargs)
        config_manager.save_config(config_manager.config)

    def register_handler(self, event_type: str, handler: Callable) -> None:
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)

    def trigger_event(self, event_type: str, *args, **kwargs) -> None:
        if event_type in self.handlers:
            for handler in self.handlers[event_type]:
                handler(*args, **kwargs)
