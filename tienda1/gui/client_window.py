import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
class ClientWindow:
    def __init__(self, parent, db):
        self.db = db
        self.win = tk.Toplevel(parent)
        self.win.title("Clientes - CRUD")
        self.win.geometry("700x400")
        self.create_widgets()
        self.load()

    def create_widgets(self):
        frm = ttk.Frame(self.win, padding=8)
        frm.pack(fill='both', expand=True)
        self.tree = ttk.Treeview(frm, columns=("id","nombre","telefono","direccion","correo"), show='headings')
        for col,h in [("id","ID"),("nombre","Nombre"),("telefono","Tel"),("direccion","Dirección"),("correo","Correo")]:
            self.tree.heading(col, text=h)
            self.tree.column(col, anchor='center')
        self.tree.pack(side='left', fill='both', expand=True)
        panel = ttk.Frame(frm, padding=8)
        panel.pack(side='right', fill='y')
        self.en_nombre = ttk.Entry(panel); ttk.Label(panel,text="Nombre").pack(anchor='w'); self.en_nombre.pack(fill='x')
        self.en_tel = ttk.Entry(panel); ttk.Label(panel,text="Teléfono").pack(anchor='w'); self.en_tel.pack(fill='x')
        self.en_dir = ttk.Entry(panel); ttk.Label(panel,text="Dirección").pack(anchor='w'); self.en_dir.pack(fill='x')
        self.en_mail = ttk.Entry(panel); ttk.Label(panel,text="Correo").pack(anchor='w'); self.en_mail.pack(fill='x')
        ttk.Button(panel, text="Agregar", command=self.agregar).pack(fill='x', pady=4)
        ttk.Button(panel, text="Editar", command=self.editar).pack(fill='x', pady=4)
        ttk.Button(panel, text="Eliminar", command=self.eliminar).pack(fill='x', pady=4)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    def load(self):
        for r in self.tree.get_children(): self.tree.delete(r)
        for row in self.db.listar_clientes():
            self.tree.insert("", "end", values=row)

    def on_select(self, event):
        sel = self.tree.selection()
        if sel:
            id_,nombre,tel,dir_,mail = self.tree.item(sel[0])['values']
            self.en_nombre.delete(0,'end'); self.en_nombre.insert(0,nombre)
            self.en_tel.delete(0,'end'); self.en_tel.insert(0,tel)
            self.en_dir.delete(0,'end'); self.en_dir.insert(0,dir_)
            self.en_mail.delete(0,'end'); self.en_mail.insert(0,mail)

    def agregar(self):
        nombre = self.en_nombre.get().strip()
        if not nombre:
            messagebox.showwarning("Nombre", "Nombre requerido")
            return
        self.db.agregar_cliente(nombre, self.en_tel.get(), self.en_dir.get(), self.en_mail.get())
        messagebox.showinfo("OK","Cliente agregado")
        self.load()

    def editar(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Seleccione", "Seleccione un cliente")
            return
        id_ = self.tree.item(sel[0])['values'][0]
        self.db.actualizar_cliente(id_, self.en_nombre.get(), self.en_tel.get(), self.en_dir.get(), self.en_mail.get())
        messagebox.showinfo("OK","Cliente actualizado")
        self.load()

    def eliminar(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Seleccione", "Seleccione un cliente")
            return
        id_ = self.tree.item(sel[0])['values'][0]
        if messagebox.askyesno("Confirmar","¿Eliminar cliente?"):
            self.db.eliminar_cliente(id_)
            messagebox.showinfo("OK","Eliminado")
            self.load()
