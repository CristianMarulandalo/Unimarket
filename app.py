# Flask
from flask import Flask, render_template, request, redirect, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from db_config import get_connection
import os
import time
import re

app = Flask(__name__)
app.secret_key = "engranaje1"

app.config['UPLOAD_FOLDER'] = 'static/uploads'

# ---------------- INICIO ----------------
@app.route('/')
def index():
    if 'usuario_id' in session:
        return redirect('/pedido')
    return redirect('/login')

# ---------------- LOGIN ----------------
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        correo = request.form['correo']
        password = request.form['password']

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM usuarios WHERE correo=%s", (correo,))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['usuario_id'] = user['id']
            session['nombre'] = user['nombre']
            return redirect('/pedido')

    return render_template('login.html')

#  CREAR PRODUCTO (FIX DEFINITIVO)
@app.route('/crear_producto', methods=['POST'])
def crear_producto():
    if 'usuario_id' not in session:
        return redirect('/login')

    nombre = request.form.get('nombre')
    descripcion = request.form.get('descripcion')
    precio = request.form.get('precio')
    categoria = request.form.get('categoria')

    imagen = request.files.get('imagen')
    nombre_imagen = None

    if imagen and imagen.filename != "":
        nombre_imagen = str(int(time.time())) + "_" + secure_filename(imagen.filename)
        ruta = os.path.join(app.config['UPLOAD_FOLDER'], nombre_imagen)
        imagen.save(ruta)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO productos (nombre, descripcion, precio, categoria, imagen, usuario_id)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (nombre, descripcion, precio, categoria, nombre_imagen, session['usuario_id']))

    conn.commit()
    cursor.close()
    conn.close()

    return redirect('/pedido')

#Eliminar producto

@app.route('/eliminar_producto/<int:id>', methods=['POST'])
def eliminar_producto(id):
    if 'usuario_id' not in session:
        return redirect('/login')

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Obtener imagen
    cursor.execute(
        "SELECT imagen FROM productos WHERE id=%s AND usuario_id=%s",
        (id, session['usuario_id'])
    )
    producto = cursor.fetchone()

    # Eliminar imagen del servidor
    if producto and producto['imagen']:
        ruta = os.path.join(app.config['UPLOAD_FOLDER'], producto['imagen'])
        if os.path.exists(ruta):
            os.remove(ruta)

    # Eliminar producto
    cursor.execute(
        "DELETE FROM productos WHERE id=%s AND usuario_id=%s",
        (id, session['usuario_id'])
    )

    conn.commit()
    cursor.close()
    conn.close()

    return redirect('/pedido')

# -----------------Editar Precio-------------
@app.route('/editar_precio/<int:id>', methods=['POST'])
def editar_precio(id):
    if 'usuario_id' not in session:
        return redirect('/login')

    nuevo_precio = request.form.get('precio')

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE productos SET precio=%s WHERE id=%s AND usuario_id=%s",
        (nuevo_precio, id, session['usuario_id'])
    )

    conn.commit()
    cursor.close()
    conn.close()

    return redirect('/pedido')



# ---------------- PRODUCTOS ----------------
@app.route('/pedido', methods=['GET','POST'])
def pedido():
    if 'usuario_id' not in session:
        return redirect('/login')

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM productos")
    productos = cursor.fetchall()

    # GUARDAR PEDIDO
    if request.method == 'POST':
        producto = request.form['producto']
        cantidad = request.form['cantidad']

        cursor.execute("""
            INSERT INTO pedidos (usuario_id, producto, cantidad)
            VALUES (%s,%s,%s)
        """, (session['usuario_id'], producto, cantidad))

        conn.commit()

    cursor.close()
    conn.close()

    return render_template('pedido.html', nombre=session['nombre'], productos=productos)

# ---------------- CARRITO ----------------
@app.route('/pedidos_lista')
def pedidos_lista():
    if 'usuario_id' not in session:
        return redirect('/login')

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
    SELECT pedidos.*, productos.precio 
    FROM pedidos 
    JOIN productos 
    ON pedidos.producto = productos.nombre
    WHERE pedidos.usuario_id = %s
    ORDER BY pedidos.id DESC
""", (session['usuario_id'],))

    pedidos = cursor.fetchall()
    total = 0

    for p in pedidos:
     p['subtotal'] = p['precio'] * p['cantidad']
     total += p['subtotal']

    cursor.close()
    conn.close()

    return render_template('pedidos_lista.html', pedidos=pedidos, total=total)

# ---------------- ELIMINAR PEDIDO ----------------
@app.route('/eliminar_pedido/<int:id>', methods=['POST'])
def eliminar_pedido(id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM pedidos WHERE id=%s", (id,))
    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({'success': True})

# ---------------- ACTUALIZAR PEDIDO ----------------
@app.route('/actualizar_pedido/<int:id>', methods=['POST'])
def actualizar_pedido(id):
    data = request.get_json()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE pedidos 
        SET producto=%s, cantidad=%s 
        WHERE id=%s
    """, (data['producto'], data['cantidad'], id))

    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({'success': True})

# ---------------- LUNA FULL INTELIGENTE ----------------
@app.route('/luna', methods=['POST'])
def luna():
    mensaje = request.json.get('mensaje').lower()

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # SALUDOS
    if any(x in mensaje for x in ["hola", "buenas"]):
        return jsonify({"respuesta": "👋 Hola, soy LUNA tu asistente de compras 💙 dime qué producto buscas por categoria y precio y te ayudare a encontrarlo"})

    if "gracias" in mensaje:
        return jsonify({"respuesta": "💙 ¡Con gusto! Aquí estoy para ayudarte"})

    # DETECTAR PRECIO
    precio = None
    match = re.search(r'(\d+)', mensaje)
    if match:
        precio = int(match.group(1))

        if "millon" in mensaje:
            precio *= 1000000

    #  PALABRAS IMPORTANTES (FILTRADAS)
    palabras = mensaje.split()

    palabras_ignorar = ["de", "menos", "mas", "quiero", "un", "una", "el", "la", "por", "favor"]

    palabras_clave = [p for p in palabras if p not in palabras_ignorar and not p.isdigit()]

    query = "SELECT * FROM productos WHERE 1=1"
    params = []

    # FILTRO PRECIO
    if precio:
        query += " AND precio <= %s"
        params.append(precio)

    # FILTRO INTELIGENTE
    if palabras_clave:
        condiciones = []
        for palabra in palabras_clave:
            condiciones.append("(LOWER(nombre) LIKE %s OR LOWER(descripcion) LIKE %s OR LOWER(categoria) LIKE %s)")
            params.extend([f"%{palabra}%", f"%{palabra}%", f"%{palabra}%"])

        query += " AND (" + " OR ".join(condiciones) + ")"

    cursor.execute(query, params)
    productos = cursor.fetchall()

    # RESPUESTA
    if not productos:
        cursor.execute("SELECT * FROM productos ORDER BY precio ASC LIMIT 3")
        productos = cursor.fetchall()
        respuesta = "😅 No encontré exactamente eso, pero mira estas opciones:"
    else:
        respuesta = "Encontré estos productos para Ti:"

    cursor.close()
    conn.close()

    return jsonify({
        "respuesta": respuesta,
        "productos": productos
    })

# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

#-----------Registro de usuario----------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        correo = request.form.get('correo')
        password = request.form.get('password')

        password_hash = generate_password_hash(password)

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO usuarios (nombre, correo, password)
            VALUES (%s, %s, %s)
        """, (nombre, correo, password_hash))

        conn.commit()
        cursor.close()
        conn.close()

        return redirect('/login')

    return render_template('register.html')

# ---------------- PAGO (BORRAR CARRITO) ----------------
@app.route('/pagar', methods=['POST'])
def pagar():
    if 'usuario_id' not in session:
        return jsonify({"success": False})

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM pedidos WHERE usuario_id = %s",
        (session['usuario_id'],)
    )

    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({"success": True})

# ---------------- RUN ----------------
if __name__ == '__main__':
    app.run(debug=True)