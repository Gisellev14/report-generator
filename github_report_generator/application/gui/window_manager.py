import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt

class WindowManager:
    def __init__(self, title: str = "GitHub Report Generator", geometry: str = "1200x800"):
        self.root = tk.Tk()
        self.root.title(title)
        self.root.geometry(geometry)
        
        # Create main container
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create notebook
        self.notebook = ttk.Notebook(self.main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
    def get_root(self) -> tk.Tk:
        return self.root
        
    def get_main_container(self) -> ttk.Frame:
        return self.main_container
        
    def get_notebook(self) -> ttk.Notebook:
        return self.notebook
        
    def set_close_handler(self, handler) -> None:
        self.root.protocol("WM_DELETE_WINDOW", handler)
        
    def cleanup(self) -> None:
        try:
            # Clean up matplotlib
            plt.close('all')
        except Exception as e:
            print(f"Error cleaning up matplotlib: {e}")
            
        # Destroy window
        try:
            self.root.destroy()
        except Exception as e:
            print(f"Error destroying window: {e}")
            
    def run(self) -> None:
        self.root.mainloop()
