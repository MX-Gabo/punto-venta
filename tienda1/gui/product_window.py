import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog

class ProductWindow:
    def __init__(self, parent, db, on_close=None):
        self.db = db
        self.on_close = on_close
        self.win = tk.Toplevel(parent)
        self.win.title("Productos - CRUD")
        self.win.geometry("800x450")
        self.create_widgets()
        self.cargar()

    def create_widgets(self):
        frm = ttk.Frame(self.win, padding=8)
        frm.pack(fill='both', expand=True)
        # tree
        self.tree = ttk.Treeview(frm, columns=("id","nombre","tipo","cantidad","color","talla","precio"), show='headings')
        for col,h in [("id","ID"),("nombre","Nombre"),("tipo","Tipo"),("cantidad","Cantidad"),("color","Color"),("talla","Talla"),("precio","Precio")]:
            self.tree.heading(col, text=h)
            self.tree.column(col, anchor='center')
        self.tree.pack(side='left', fill='both', expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        # panel derecho
        panel = ttk.Frame(frm, padding=8)
        panel.pack(side='right', fill='y')
        labels = ["Nombre","Tipo","Cantidad","Color","Talla","Precio"]
        self.entries = {}
        for i,lab in enumerate(labels):
            ttk.Label(panel, text=lab).pack(anchor='w')
            ent = ttk.Entry(panel)
            ent.pack(fill='x', pady=2)
            self.entries[lab.lower()] = ent
        ttk.Button(panel, text="Agregar", command=self.agregar).pack(fill='x', pady=4)
        ttk.Button(panel, text="Editar", command=self.editar).pack(fill='x', pady=4)
        ttk.Button(panel, text="Eliminar", command=self.eliminar).pack(fill='x', pady=4)

    def cargar(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        for row in self.db.listar_productos():
            self.tree.insert("", "end", values=row)

    def on_select(self, event):
        sel = self.tree.selection()
        if sel:
            vals = self.tree.item(sel[0])['values']
            # mapear a entradas
            _,nombre,tipo,cantidad,color,talla,precio = vals
            self.entries['nombre'].delete(0,'end'); self.entries['nombre'].insert(0,nombre)
            self.entries['tipo'].delete(0,'end'); self.entries['tipo'].insert(0,tipo)
            self.entries['cantidad'].delete(0,'end'); self.entries['cantidad'].insert(0,cantidad)
            self.entries['color'].delete(0,'end'); self.entries['color'].insert(0,color)
            self.entries['talla'].delete(0,'end'); self.entries['talla'].insert(0,talla)
            self.entries['precio'].delete(0,'end'); self.entries['precio'].insert(0,precio)

    def agregar(self):
        try:
            nombre = self.entries['nombre'].get().strip()
            tipo = self.entries['tipo'].get().strip()
            cantidad = int(self.entries['cantidad'].get() or 0)
            color = self.entries['color'].get().strip()
            talla = self.entries['talla'].get().strip()
            precio = float(self.entries['precio'].get() or 0.0)
            if not nombre:
                raise ValueError("Nombre requerido")
        except Exception as e:
            messagebox.showerror("Error", f"Datos inválidos: {e}")
            return
        self.db.agregar_producto(nombre,tipo,cantidad,color,talla,precio)
        messagebox.showinfo("OK","Producto agregado")
        self.cargar()
        if self.on_close: self.on_close()

    def editar(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Seleccione", "Seleccione un producto")
            return
        id_ = self.tree.item(sel[0])['values'][0]
        try:
            nombre = self.entries['nombre'].get().strip()
            tipo = self.entries['tipo'].get().strip()
            cantidad = int(self.entries['cantidad'].get() or 0)
            color = self.entries['color'].get().strip()
            talla = self.entries['talla'].get().strip()
            precio = float(self.entries['precio'].get() or 0.0)
        except Exception as e:
            messagebox.showerror("Error", f"Datos inválidos: {e}")
            return
        self.db.actualizar_producto(id_,nombre,tipo,cantidad,color,talla,precio)
        messagebox.showinfo("OK","Producto actualizado")
        self.cargar()
        if self.on_close: self.on_close()

    def eliminar(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Seleccione", "Seleccione un producto")
            return
        id_ = self.tree.item(sel[0])['values'][0]
        if messagebox.askyesno("Confirmar", "¿Eliminar producto?"):
            self.db.eliminar_producto(id_)
            messagebox.showinfo("OK","Eliminado")
            self.cargar()
            if self.on_close: self.on_close()
