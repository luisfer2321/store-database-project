import os
from flask import Flask, request, render_template, redirect, url_for
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

# --- Datos de conexión a PostgreSQL ---
# En Render, esta variable la pone Render automáticamente al conectar tu base de datos.
# En tu Mac (si no existe la variable), usa tus datos locales como respaldo.
DATABASE_URL = os.environ.get("DATABASE_URL")

def get_connection():
    if DATABASE_URL:
        return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    return psycopg2.connect(
        host="localhost",
        database="storepractice",
        user="postgres",
        password="luis123",
        cursor_factory=RealDictCursor
    )


# ============== INICIO ==============
@app.route("/")
def index():
    return render_template("index.html")


# ============== CLIENTES ==============
@app.route("/clientes")
def clientes_list():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM cliente ORDER BY id_cliente DESC")
    clientes = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("clientes_list.html", clientes=clientes)


@app.route("/clientes/nuevo", methods=["GET", "POST"])
def cliente_nuevo():
    if request.method == "POST":
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO cliente (nombre, apellido, numero) VALUES (%s, %s, %s)",
            (request.form["nombre"], request.form["apellido"], request.form["numero"])
        )
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for("clientes_list"))
    return render_template("cliente_form.html")


# ============== VENDEDORES ==============
@app.route("/vendedores")
def vendedores_list():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM vendedor ORDER BY id_vendedor DESC")
    vendedores = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("vendedores_list.html", vendedores=vendedores)


@app.route("/vendedores/nuevo", methods=["GET", "POST"])
def vendedor_nuevo():
    if request.method == "POST":
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO vendedor (nombre, apellido, numero) VALUES (%s, %s, %s)",
            (request.form["nombre"], request.form["apellido"], request.form["numero"])
        )
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for("vendedores_list"))
    return render_template("vendedor_form.html")


# ============== PROVEEDORES ==============
@app.route("/proveedores")
def proveedores_list():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM proveedor ORDER BY id_proveedor DESC")
    proveedores = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("proveedores_list.html", proveedores=proveedores)


@app.route("/proveedores/nuevo", methods=["GET", "POST"])
def proveedor_nuevo():
    if request.method == "POST":
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO proveedor (nombre_empresa, contacto_nombre, numero) VALUES (%s, %s, %s)",
            (request.form["nombre_empresa"], request.form["contacto_nombre"], request.form["numero"])
        )
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for("proveedores_list"))
    return render_template("proveedor_form.html")


# ============== CATEGORIAS (helper simple, solo para llenar el dropdown de productos) ==============
@app.route("/categorias/nueva", methods=["GET", "POST"])
def categoria_nueva():
    if request.method == "POST":
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO categoria (nombre, descripcion) VALUES (%s, %s)",
            (request.form["nombre"], request.form["descripcion"])
        )
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for("productos_list"))
    return render_template("categoria_form.html")


# ============== PRODUCTOS ==============
@app.route("/productos")
def productos_list():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT p.*, c.nombre AS categoria_nombre, pr.nombre_empresa AS proveedor_nombre
        FROM producto p
        JOIN categoria c ON p.id_categoria = c.id_categoria
        JOIN proveedor pr ON p.id_proveedor = pr.id_proveedor
        ORDER BY p.id_producto DESC
    """)
    productos = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("productos_list.html", productos=productos)


@app.route("/productos/nuevo", methods=["GET", "POST"])
def producto_nuevo():
    conn = get_connection()
    cur = conn.cursor()
    if request.method == "POST":
        cur.execute(
            """INSERT INTO producto (id_categoria, id_proveedor, nombre, precio_unitario, talla, color, stock_actual)
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (request.form["id_categoria"], request.form["id_proveedor"], request.form["nombre"],
             request.form["precio_unitario"], request.form["talla"], request.form["color"],
             request.form.get("stock_actual", 0))
        )
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for("productos_list"))

    cur.execute("SELECT * FROM categoria ORDER BY nombre")
    categorias = cur.fetchall()
    cur.execute("SELECT * FROM proveedor ORDER BY nombre_empresa")
    proveedores = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("producto_form.html", categorias=categorias, proveedores=proveedores)


# ============== VENTAS ==============
@app.route("/ventas")
def ventas_list():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT v.*, c.nombre AS cliente_nombre, c.apellido AS cliente_apellido,
               ve.nombre AS vendedor_nombre
        FROM venta v
        JOIN cliente c ON v.id_cliente = c.id_cliente
        JOIN vendedor ve ON v.id_vendedor = ve.id_vendedor
        ORDER BY v.id_venta DESC
    """)
    ventas = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("ventas_list.html", ventas=ventas)


@app.route("/ventas/<int:id_venta>")
def venta_detalle(id_venta):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM venta WHERE id_venta = %s", (id_venta,))
    venta = cur.fetchone()
    cur.execute("""
        SELECT dv.*, p.nombre AS producto_nombre
        FROM detalle_venta dv
        JOIN producto p ON dv.id_producto = p.id_producto
        WHERE dv.id_venta = %s
    """, (id_venta,))
    detalles = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("venta_detalle.html", venta=venta, detalles=detalles)


@app.route("/ventas/nueva", methods=["GET", "POST"])
def venta_nueva():
    conn = get_connection()
    cur = conn.cursor()

    if request.method == "POST":
        id_cliente = request.form["id_cliente"]
        id_vendedor = request.form["id_vendedor"]
        metodo_pago = request.form["metodo_pago"]

        # 1. Crear la venta (el total lo actualiza el trigger de la BD)
        cur.execute(
            "INSERT INTO venta (id_cliente, id_vendedor, metodo_pago) VALUES (%s, %s, %s) RETURNING id_venta",
            (id_cliente, id_vendedor, metodo_pago)
        )
        id_venta = cur.fetchone()["id_venta"]

        # 2. Insertar cada producto agregado dinámicamente en el formulario
        productos_ids = request.form.getlist("producto_id[]")
        cantidades = request.form.getlist("cantidad[]")

        for pid, cant in zip(productos_ids, cantidades):
            if pid and cant:
                cur.execute("SELECT precio_unitario FROM producto WHERE id_producto = %s", (pid,))
                precio = cur.fetchone()["precio_unitario"]
                cur.execute(
                    "INSERT INTO detalle_venta (id_venta, id_producto, cantidad, precio_unitario) VALUES (%s, %s, %s, %s)",
                    (id_venta, pid, cant, precio)
                )

        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for("venta_detalle", id_venta=id_venta))

    cur.execute("SELECT * FROM cliente ORDER BY nombre")
    clientes = cur.fetchall()
    cur.execute("SELECT * FROM vendedor ORDER BY nombre")
    vendedores = cur.fetchall()
    cur.execute("SELECT * FROM producto ORDER BY nombre")
    productos = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("venta_form.html", clientes=clientes, vendedores=vendedores, productos=productos)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(debug=True, port=port, host="0.0.0.0")
