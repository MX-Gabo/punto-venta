import sqlite3
from datetime import datetime
from tienda1.config import DB, IVA_RATE

class Database:
    def __init__(self, db_file=DB):
            self.db_file = db_file

    def connect(self):
            return sqlite3.connect(self.db_file)
    # ---------- USUARIOS ----------
    def verificar_usuario(self, usuario, contrasena):
        with self.connect() as conn:
            c = conn.cursor()
            c.execute("SELECT id, rol FROM usuarios WHERE usuario=? AND contrasena=?", (usuario, contrasena))
            return c.fetchone()

    # ---------- PRODUCTOS ----------
    def listar_productos(self):
        with self.connect() as conn:
            c = conn.cursor()
            c.execute("SELECT id,nombre,tipo,cantidad,color,talla,precio FROM productos")
            return c.fetchall()

    def agregar_producto(self, nombre, tipo, cantidad, color, talla, precio):
        with self.connect() as conn:
            conn.execute("INSERT INTO productos (nombre,tipo,cantidad,color,talla,precio) VALUES (?,?,?,?,?,?)",
                         (nombre, tipo, cantidad, color, talla, precio))

    def actualizar_producto(self, id_, nombre, tipo, cantidad, color, talla, precio):
        with self.connect() as conn:
            conn.execute("""UPDATE productos SET nombre=?,tipo=?,cantidad=?,color=?,talla=?,precio=? WHERE id=?""",
                         (nombre, tipo, cantidad, color, talla, precio, id_))

    def eliminar_producto(self, id_):
        with self.connect() as conn:
            conn.execute("DELETE FROM productos WHERE id=?", (id_,))

    # ---------- CLIENTES ----------
    def listar_clientes(self):
        with self.connect() as conn:
            c = conn.cursor()
            c.execute("SELECT id,nombre,telefono,direccion,correo FROM clientes")
            return c.fetchall()

    def agregar_cliente(self, nombre, telefono, direccion, correo):
        with self.connect() as conn:
            conn.execute("INSERT INTO clientes (nombre,telefono,direccion,correo) VALUES (?,?,?,?)",
                         (nombre, telefono, direccion, correo))

    def actualizar_cliente(self, id_, nombre, telefono, direccion, correo):
        with self.connect() as conn:
            conn.execute("UPDATE clientes SET nombre=?,telefono=?,direccion=?,correo=? WHERE id=?",
                         (nombre, telefono, direccion, correo, id_))

    def eliminar_cliente(self, id_):
        with self.connect() as conn:
            conn.execute("DELETE FROM clientes WHERE id=?", (id_,))

    # ---------- VENTAS ----------
    def guardar_venta(self, cliente_id, items):
        subtotal = sum(item['importe'] for item in items)
        iva = round(subtotal * IVA_RATE, 2)
        total = round(subtotal + iva, 2)
        fecha = datetime.now().isoformat(timespec='seconds')

        with self.connect() as conn:
            c = conn.cursor()
            c.execute("INSERT INTO ventas (cliente_id,fecha,subtotal,iva,total) VALUES (?,?,?,?,?)",
                      (cliente_id, fecha, subtotal, iva, total))
            venta_id = c.lastrowid
            for it in items:
                c.execute("""INSERT INTO venta_detalle (venta_id,producto_id,cantidad,precio_unitario,importe)
                             VALUES (?,?,?,?,?)""",
                          (venta_id, it['producto_id'], it['cantidad'], it['precio_unitario'], it['importe']))
                c.execute("UPDATE productos SET cantidad = cantidad - ? WHERE id=?", (it['cantidad'], it['producto_id']))
        return venta_id, subtotal, iva, total

    def obtener_producto_por_id(self, id_):
        with self.connect() as conn:
            c = conn.cursor()
            c.execute("SELECT id,nombre,precio,cantidad FROM productos WHERE id=?", (id_,))
            return c.fetchone()

    def obtener_cliente_por_id(self, id_):
        with self.connect() as conn:
            c = conn.cursor()
            c.execute("SELECT id,nombre FROM clientes WHERE id=?", (id_,))
            return c.fetchone()
