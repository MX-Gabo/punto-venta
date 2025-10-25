
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from tienda1.gui.main_window import MainWindow
class LoginWindow:
    def __init__(self, root, db):
        self.root = root
        self.db = db
        self.root.title("Iniciar Sesión - Tienda")
        self.root.geometry("320x160")
        ttk.Label(root, text="Usuario:").pack(pady=5)
        self.ent_user = ttk.Entry(root)
        self.ent_user.pack()
        ttk.Label(root, text="Contraseña:").pack(pady=5)
        self.ent_pass = ttk.Entry(root, show="*")
        self.ent_pass.pack()
        ttk.Button(root, text="Iniciar sesión", command=self.login).pack(pady=10)

    def login(self):
        u = self.ent_user.get().strip()
        p = self.ent_pass.get().strip()
        if not u or not p:
            messagebox.showwarning("Validación", "Ingrese usuario y contraseña")
            return
        res = self.db.verificar_usuario(u,p)
        if res:
            user_id, rol = res
            messagebox.showinfo("OK", f"Bienvenido {u} ({rol})")
            self.root.destroy()
            main = tk.Tk()
            MainWindow(main, self.db, usuario=u, rol=rol)
            main.mainloop()
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos")
