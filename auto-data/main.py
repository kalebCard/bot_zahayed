import tkinter as tk
from app import TkinterApp

def main():
    root = tk.Tk()
    app = TkinterApp(root)
    root.mainloop()

if __name__ == "__main__":
    main() 