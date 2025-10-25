import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from tienda1.gui.product_window import ProductWindow
from tienda1.gui.client_window import ClientWindow
from tienda1.gui.sales_window import SalesWindow

class MainWindow:
    def __init__(self, root, db, usuario, rol):
        self.root = root
        self.db = db
        self.usuario = usuario
        self.rol = rol
        self.root.title("Tienda - Principal")
        self.root.geometry("700x450")

        # cabecera
        header = ttk.Frame(root, padding=10)
        header.pack(fill='x')
        ttk.Label(header, text=f"Usuario: {usuario} - Rol: {rol}").pack(side='left')
        ttk.Button(header, text="Productos", command=self.open_productos).pack(side='left', padx=5)
        ttk.Button(header, text="Clientes", command=self.open_clientes).pack(side='left', padx=5)
        ttk.Button(header, text="Ventas", command=self.open_ventas).pack(side='left', padx=5)
        ttk.Button(header, text="Salir", command=root.quit).pack(side='right')

        # info / lista de productos
        self.tree = ttk.Treeview(root, columns=("id","nombre","tipo","cantidad","color","talla","precio"), show='headings')
        for col,h in [("id","ID"),("nombre","Nombre"),("tipo","Tipo"),("cantidad","Cantidad"),("color","Color"),("talla","Talla"),("precio","Precio")]:
            self.tree.heading(col, text=h)
            self.tree.column(col, anchor='center')
        self.tree.pack(expand=True, fill='both', padx=10, pady=10)
        ttk.Button(root, text="Refrescar lista", command=self.cargar_productos).pack()
        self.cargar_productos()

    def cargar_productos(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        for row in self.db.listar_productos():
            self.tree.insert("", "end", values=row)

    def open_productos(self):
        ProductWindow(self.root, self.db, on_close=self.cargar_productos)

    def open_clientes(self):
        ClientWindow(self.root, self.db)

    def open_ventas(self):
        SalesWindow(self.root, self.db, usuario=self.usuario)
