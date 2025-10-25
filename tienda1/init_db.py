import sqlite3
from datetime import datetime

DB = "tienda2.db"

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    # Usuarios (para login y roles)
    c.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT UNIQUE NOT NULL,
        contrasena TEXT NOT NULL,
        rol TEXT NOT NULL
    )
    """)

    # Clientes
    c.execute("""
    CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        telefono TEXT,
        direccion TEXT,
        correo TEXT
    )
    """)

    # Productos
    c.execute("""
    CREATE TABLE IF NOT EXISTS productos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        tipo TEXT,
        cantidad INTEGER NOT NULL DEFAULT 0,
        color TEXT,
        talla TEXT,
        precio REAL NOT NULL
    )
    """)

    # Ventas (cabecera) con usuario_id
    c.execute("""
    CREATE TABLE IF NOT EXISTS ventas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id INTEGER,
        usuario_id INTEGER,
        fecha TEXT NOT NULL,
        subtotal REAL NOT NULL,
        iva REAL NOT NULL,
        total REAL NOT NULL,
        FOREIGN KEY(cliente_id) REFERENCES clientes(id),
        FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
    )
    """)

    # Detalle de ventas
    c.execute("""
    CREATE TABLE IF NOT EXISTS venta_detalle (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        venta_id INTEGER NOT NULL,
        producto_id INTEGER NOT NULL,
        cantidad INTEGER NOT NULL,
        precio_unitario REAL NOT NULL,
        importe REAL NOT NULL,
        FOREIGN KEY(venta_id) REFERENCES ventas(id),
        FOREIGN KEY(producto_id) REFERENCES productos(id)
    )
    """)

    # seed: admin user (usuario: admin, contraseña: admin)
    c.execute("INSERT OR IGNORE INTO usuarios (usuario, contrasena, rol) VALUES (?, ?, ?)",
              ("admin", "admin", "Administrador"))

    # seed: empleado
    c.execute("INSERT OR IGNORE INTO usuarios (usuario, contrasena, rol) VALUES (?, ?, ?)",
              ("empleado", "1234", "Empleado"))

    # seed: ejemplo productos
    ejemplos = [
        ("Zapatillas Neo", "Calzado", 10, "Negro", "42", 450.0),
        ("Mocasines 2 T1", "Mocasines", 15, "Marrón", "24", 5060.0),
        ("Tenis Sport", "Tenis", 8, "Azul", "40", 250.0)
    ]
    for p in ejemplos:
        c.execute("SELECT id FROM productos WHERE nombre=?", (p[0],))
        if not c.fetchone():
            c.execute("INSERT INTO productos (nombre,tipo,cantidad,color,talla,precio) VALUES (?,?,?,?,?,?)", p)

    # seed: ejemplo clientes
    clientes = [
        ("Juan Perez", "5512345678", "Calle Falsa 123", "juan@example.com"),
        ("María López", "5511122233", "Av Siempre Viva 5", "maria@example.com")
    ]
    for cl in clientes:
        c.execute("SELECT id FROM clientes WHERE nombre=?", (cl[0],))
        if not c.fetchone():
            c.execute("INSERT INTO clientes (nombre,telefono,direccion,correo) VALUES (?,?,?,?)", cl)

    conn.commit()
    conn.close()
    print("Base de datos inicializada en", DB)

if __name__ == "__main__":
    init_db()
