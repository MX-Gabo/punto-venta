import tkinter as tk
from datetime import datetime
from tkinter import ttk, messagebox, simpledialog
from tienda1.config import IVA_RATE
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

class SalesWindow:
    def __init__(self, parent, db, usuario):
        self.db = db
        self.usuario = usuario
        self.cart = []  # Lista de productos seleccionados
        self.win = tk.Toplevel(parent)
        self.win.title("Ventas - Generar ticket")
        self.win.geometry("950x600")
        self.create_widgets()
        self.actualizar_botones()

    def create_widgets(self):
        # ===== TOP: Cliente y búsqueda =====
        top = ttk.Frame(self.win, padding=8)
        top.pack(fill='x', pady=5)

        ttk.Label(top, text="Cliente:").pack(side='left')
        self.client_cb = ttk.Combobox(top, values=[f"{c[0]} - {c[1]}" for c in self.db.listar_clientes()])
        self.client_cb.pack(side='left', padx=5)
        self.client_cb.bind("<<ComboboxSelected>>", lambda e: self.actualizar_botones())

        self.client_search = ttk.Entry(top)
        self.client_search.pack(side='left', padx=5)
        ttk.Button(top, text="Buscar", command=self.buscar_cliente).pack(side='left', padx=5)
        ttk.Button(top, text="Nuevo cliente", command=self.nuevo_cliente).pack(side='left', padx=5)

        # ===== MID: Productos disponibles =====
        mid = ttk.LabelFrame(self.win, text="Productos disponibles", padding=8)
        mid.pack(fill='x', padx=10, pady=5)

        self.tree_products = ttk.Treeview(mid, columns=("id","nombre","precio","stock"), show='headings', height=8)
        for col,h in [("id","ID"),("nombre","Nombre"),("precio","Precio"),("stock","Stock")]:
            self.tree_products.heading(col, text=h)
            self.tree_products.column(col, anchor='center')
        self.tree_products.pack(fill='x')
        self.tree_products.bind("<Double-1>", self.add_from_list)
        self.cargar_productos()

        # ===== CART: Carrito =====
        cart_frame = ttk.LabelFrame(self.win, text="Carrito", padding=8)
        cart_frame.pack(fill='both', expand=True, padx=10, pady=5)

        self.tree_cart = ttk.Treeview(cart_frame, columns=("prodid","nombre","cantidad","precio","importe"), show='headings', height=8)
        for col,h in [("prodid","ID"),("nombre","Nombre"),("cantidad","Cant"),("precio","Precio U"),("importe","Importe")]:
            self.tree_cart.heading(col, text=h)
            self.tree_cart.column(col, anchor='center')
        self.tree_cart.pack(fill='both', expand=True)
        self.tree_cart.bind("<<TreeviewSelect>>", lambda e: self.actualizar_botones())

        # ===== Botones de carrito =====
        self.btn_frame = ttk.Frame(self.win, padding=8)
        self.btn_frame.pack(fill='x', padx=10)
        self.btn_quitar = ttk.Button(self.btn_frame, text="Quitar seleccionado", command=self.quitar_seleccionado)
        self.btn_quitar.pack(side='left', padx=5)
        self.btn_limpiar = ttk.Button(self.btn_frame, text="Limpiar carrito", command=self.limpiar_carrito)
        self.btn_limpiar.pack(side='left', padx=5)

        # ===== Totales =====
        resumen = ttk.Frame(self.win, padding=8)
        resumen.pack(fill='x', padx=10)
        self.lbl_sub = ttk.Label(resumen, text="Subtotal: 0.00")
        self.lbl_iva = ttk.Label(resumen, text=f"IVA ({int(IVA_RATE*100)}%): 0.00")
        self.lbl_total = ttk.Label(resumen, text="Total: 0.00")
        self.lbl_sub.pack(anchor='e')
        self.lbl_iva.pack(anchor='e')
        self.lbl_total.pack(anchor='e')

        # ===== Acciones =====
        actions = ttk.Frame(self.win, padding=8)
        actions.pack(fill='x', padx=10, pady=5)
        self.btn_finalizar = ttk.Button(actions, text="Finalizar venta", command=self.finalizar_venta)
        self.btn_finalizar.pack(side='right', padx=5)

    # ===== Funciones de actualización =====
    def actualizar_botones(self):
        tiene_carrito = len(self.cart) > 0
        sel_carrito = self.tree_cart.selection()
        client_selected = bool(self.client_cb.get())

        # Activar/desactivar botones según estado
        self.btn_limpiar.state(['!disabled'] if tiene_carrito else ['disabled'])
        self.btn_quitar.state(['!disabled'] if sel_carrito else ['disabled'])
        self.btn_finalizar.state(['!disabled'] if tiene_carrito and client_selected else ['disabled'])

    # ===== Productos =====
    def cargar_productos(self):
        self.tree_products.delete(*self.tree_products.get_children())
        for id_, nombre, tipo, cantidad, color, talla, precio in self.db.listar_productos():
            self.tree_products.insert("", "end", values=(id_, nombre, precio, cantidad))

    def add_from_list(self, event):
        sel = self.tree_products.selection()
        if not sel: return
        item = self.tree_products.item(sel[0])['values']
        prod_id, nombre, precio, stock = item
        cant = simpledialog.askinteger("Cantidad", f"Ingrese cantidad para '{nombre}' (stock: {stock})", minvalue=1, maxvalue=stock)
        if not cant: return
        for it in self.cart:
            if it['producto_id'] == prod_id:
                if it['cantidad'] + cant > stock:
                    messagebox.showwarning("Stock insuficiente", f"Solo hay {stock} unidades disponibles")
                    return
                it['cantidad'] += cant
                it['importe'] = round(it['cantidad'] * it['precio_unitario'], 2)
                break
        else:
            importe = round(cant * float(precio), 2)
            self.cart.append({'producto_id':prod_id,'nombre':nombre,'cantidad':cant,'precio_unitario':float(precio),'importe':importe})
        self.refrescar_carrito()

    # ===== Carrito =====
    def refrescar_carrito(self):
        self.tree_cart.delete(*self.tree_cart.get_children())
        for it in self.cart:
            self.tree_cart.insert("", "end", values=(it['producto_id'], it['nombre'], it['cantidad'], f"{it['precio_unitario']:.2f}", f"{it['importe']:.2f}"))
        subtotal = round(sum(it['importe'] for it in self.cart), 2)
        iva = round(subtotal * IVA_RATE, 2)
        total = subtotal + iva
        self.lbl_sub.config(text=f"Subtotal: {subtotal:.2f}")
        self.lbl_iva.config(text=f"IVA ({int(IVA_RATE*100)}%): {iva:.2f}")
        self.lbl_total.config(text=f"Total: {total:.2f}")
        self.actualizar_botones()

    def quitar_seleccionado(self):
        sel = self.tree_cart.selection()
        if not sel: return
        idx = self.tree_cart.index(sel[0])
        del self.cart[idx]
        self.refrescar_carrito()

    def limpiar_carrito(self):
        self.cart.clear()
        self.refrescar_carrito()

    # ===== Clientes =====
    def nuevo_cliente(self):
        nombre = simpledialog.askstring("Nuevo cliente","Nombre")
        if not nombre: return
        tel = simpledialog.askstring("Nuevo cliente","Teléfono")
        dir_ = simpledialog.askstring("Nuevo cliente","Dirección")
        mail = simpledialog.askstring("Nuevo cliente","Correo")
        self.db.agregar_cliente(nombre, tel or "", dir_ or "", mail or "")
        self.client_cb['values'] = [f"{c[0]} - {c[1]}" for c in self.db.listar_clientes()]

    def buscar_cliente(self):
        texto = self.client_search.get().lower()
        clientes = [f"{c[0]} - {c[1]}" for c in self.db.listar_clientes() if texto in str(c[0]).lower() or texto in c[1].lower()]
        self.client_cb['values'] = clientes
        if clientes: self.client_cb.set(clientes[0])
        self.actualizar_botones()

    # ===== Finalizar venta y generar PDF =====
    def finalizar_venta(self):
        if not self.cart or not self.client_cb.get():
            return

        cliente_id = int(self.client_cb.get().split(" - ")[0])
        venta_id, subtotal, iva, total = self.db.guardar_venta(cliente_id, [
            {'producto_id': it['producto_id'], 'cantidad': it['cantidad'],
             'precio_unitario': it['precio_unitario'], 'importe': it['importe']}
            for it in self.cart
        ])

        self.generar_ticket_pdf(venta_id)

        messagebox.showinfo(
            "Venta finalizada",
            f"Venta #{venta_id} guardada y ticket PDF generado."
        )

        # Limpiar carrito y productos para la siguiente venta
        self.limpiar_carrito()
        self.cargar_productos()

        # Reiniciar selección de cliente para nueva venta
        self.client_cb.set('')
        self.actualizar_botones()

    def generar_ticket_pdf(self, venta_id):
        os.makedirs("tickets", exist_ok=True)
        filename = f"tickets/venta_{venta_id}.pdf"
        c = canvas.Canvas(filename, pagesize=letter)
        c.setFont("Helvetica", 12)
        y = 750
        c.drawString(50, y, f"Tienda - Ticket de Venta #{venta_id}")
        y -= 20
        c.drawString(50, y, f"Cliente: {self.client_cb.get()}")
        y -= 20
        c.drawString(50, y, f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        y -= 20
        c.drawString(50, y, "-"*60)
        y -= 20
        c.drawString(50, y, f"{'Producto':20} {'Cant':>4} {'P.U.':>8} {'Importe':>10}")
        y -= 20
        for it in self.cart:
            c.drawString(50, y, f"{it['nombre'][:20]:20} {it['cantidad']:>4} {it['precio_unitario']:>8.2f} {it['importe']:>10.2f}")
            y -= 20
        y -= 10
        subtotal = round(sum(it['importe'] for it in self.cart), 2)
        iva = round(subtotal * IVA_RATE, 2)
        total = subtotal + iva
        c.drawString(50, y, "-"*60)
        y -= 20
        c.drawString(300, y, f"Subtotal: {subtotal:.2f}")
        y -= 20
        c.drawString(300, y, f"IVA ({int(IVA_RATE*100)}%): {iva:.2f}")
        y -= 20
        c.drawString(300, y, f"Total: {total:.2f}")
        c.save()
