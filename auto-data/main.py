import tkinter as tk
import ttkbootstrap as ttk
from app import TkinterApp

def main():
    # Create the root window with ttkbootstrap theme
    root = ttk.Window(themename="darkly")
    root.title("Gestión de Datos")
    root.geometry("1200x800")
    
    # Set window icon if available
    try:
        root.iconbitmap('icon.ico')  # Make sure to have an icon.ico file in the same directory
    except:
        pass  # Continue without icon if not available
    
    # Initialize the application
    app = TkinterApp(root)
    
    # Start the main loop
    root.mainloop()

if __name__ == "__main__":
    main()