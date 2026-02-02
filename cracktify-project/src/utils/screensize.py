import tkinter as tk

root = tk.Tk()
root.withdraw()  # Hide the root window

width = root.winfo_screenwidth()
height = root.winfo_screenheight()

root.destroy()

def get_screen_size() -> tuple[int, int]:
    """Get the screen size (width, height) in pixels."""
    return width, height
