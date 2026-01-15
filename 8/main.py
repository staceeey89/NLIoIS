import tkinter as tk
from gui_app import GermanTTSApp

if __name__ == "__main__":
    root = tk.Tk()
    # Настройка масштабирования для экранов с высоким разрешением (DPI Awareness)
    try:
        from ctypes import windll

        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass

    app = GermanTTSApp(root)
    root.mainloop()