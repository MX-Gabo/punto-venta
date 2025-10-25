import tkinter as tk
from tienda1.db_manager import Database
from gui.login_window import LoginWindow

# ---------- Inicio ----------
def main():
    db = Database()
    root = tk.Tk()
    LoginWindow(root, db)
    root.mainloop()

if __name__ == "__main__":
    main()