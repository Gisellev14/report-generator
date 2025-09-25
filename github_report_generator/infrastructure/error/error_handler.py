import traceback
from tkinter import messagebox
from typing import Callable, Optional


class ErrorHandler:
    @staticmethod
    def handle_gui_error(
        error: Exception,
        context: str,
        show_message: bool = True,
        callback: Optional[Callable] = None,
    ):
        error_msg = f"Error in {context}: {str(error)}"
        print(error_msg)
        traceback.print_exc()

        if show_message:
            messagebox.showerror("Error", error_msg)

        if callback:
            try:
                callback()
            except Exception as e:
                print(f"Error in error handler callback: {e}")
                traceback.print_exc()

    @staticmethod
    def handle_chart_error(error: Exception, chart_type: str, summary_text=None):
        error_msg = f"Error updating {chart_type} chart: {str(error)}"
        print(error_msg)
        traceback.print_exc()

        if summary_text:
            try:
                summary_text.insert("end", f"\n\n{error_msg}")
            except Exception as e:
                print(f"Error updating summary text: {e}")
                traceback.print_exc()

    @staticmethod
    def handle_api_error(
        error: Exception,
        operation: str,
    ) -> bool:
        error_msg = f"Error during {operation}: {str(error)}"
        print(error_msg)
        traceback.print_exc()
        messagebox.showerror("API Error", error_msg)
        return False
