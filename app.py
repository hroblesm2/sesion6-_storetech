from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'tu_clave_secreta_super_segura_cambiar_en_produccion')

# Configuración de la base de datos
DATABASE = 'tienda_tecnologia.db'

def get_db():
    """Obtiene una conexión a la base de datos"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Inicializa la base de datos con las tablas necesarias"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Tabla de usuarios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            nombre_completo TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            rol TEXT NOT NULL CHECK(rol IN ('administrador', 'asesor')),
            activo INTEGER DEFAULT 1,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabla de categorías
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE NOT NULL,
            descripcion TEXT,
            activo INTEGER DEFAULT 1
        )
    ''')
    
    # Tabla de productos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE NOT NULL,
            nombre TEXT NOT NULL,
            descripcion TEXT,
            categoria_id INTEGER,
            marca TEXT,
            modelo TEXT,
            precio REAL NOT NULL,
            stock INTEGER DEFAULT 0,
            stock_minimo INTEGER DEFAULT 5,
            imagen_url TEXT,
            activo INTEGER DEFAULT 1,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (categoria_id) REFERENCES categorias (id)
        )
    ''')
    
    # Tabla de clientes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            documento TEXT UNIQUE NOT NULL,
            tipo_documento TEXT NOT NULL,
            nombre TEXT NOT NULL,
            apellido TEXT NOT NULL,
            email TEXT,
            telefono TEXT,
            direccion TEXT,
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabla de ventas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_venta TEXT UNIQUE NOT NULL,
            cliente_id INTEGER,
            usuario_id INTEGER,
            fecha_venta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            sdetalle   ubtotal REAL NOT NULL,
            igv REAL NOT NULL,
            total REAL NOT NULL,
            estado TEXT DEFAULT 'completada',
            metodo_pago TEXT,
            observaciones TEXT,
            FOREIGN KEY (cliente_id) REFERENCES clientes (id),
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
        )
    ''')
    
    # Tabla de detalle de ventas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS detalle_ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            venta_id INTEGER,
            producto_id INTEGER,
            cantidad INTEGER NOT NULL,
            precio_unitario REAL NOT NULL,
            subtotal REAL NOT NULL,
            FOREIGN KEY (venta_id) REFERENCES ventas (id),
            FOREIGN KEY (producto_id) REFERENCES productos (id)
        )
    ''')
    
    # Tabla de historial de stock (nueva)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS historial_stock (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            producto_id INTEGER NOT NULL,
            usuario_id INTEGER NOT NULL,
            cantidad_anterior INTEGER NOT NULL,
            cantidad_nueva INTEGER NOT NULL,
            tipo_movimiento TEXT NOT NULL,
            motivo TEXT,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (producto_id) REFERENCES productos (id),
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
        )
    ''')
    conn.commit()
    
    # Crear usuario administrador por defecto
    cursor.execute("SELECT * FROM usuarios WHERE username = 'admin'")
    if not cursor.fetchone():
        hash_password= generate_password_hash('admin123')
        cursor.execute('''
            INSERT INTO usuarios (username, password, nombre_completo, email, rol)
            VALUES (?, ?, ?, ?, ?)
        ''', ('admin', hash_password, 'Administrador', 'admin@gpsmanagement.com', 'administrador'))
        
        # Crear usuario asesor por defecto
        hash_password_asesor = generate_password_hash('asesor123')
        cursor.execute('''
            INSERT INTO usuarios (username, password, nombre_completo, email, rol)
            VALUES (?, ?, ?, ?, ?)
        ''', ('asesor', hash_password_asesor, 'Asesor de Ventas', 'asesor@gpsmanagement.com', 'asesor'))
        
        conn.commit()
    
    # Insertar categorías de ejemplo
    cursor.execute("SELECT COUNT(*) as count FROM categorias")
    if cursor.fetchone()['count'] == 0:
        categorias = [
            ('Laptops', 'Computadoras portátiles de diferentes marcas'),
            ('Smartphones', 'Teléfonos inteligentes'),
            ('Tablets', 'Tabletas y iPads'),
            ('Accesorios', 'Accesorios tecnológicos diversos'),
            ('Componentes', 'Componentes de computadora'),
            ('Audio', 'Audífonos, parlantes y equipos de audio'),
            ('Gaming', 'Productos para videojuegos')
        ]
        cursor.executemany('INSERT INTO categorias (nombre, descripcion) VALUES (?, ?)', categorias)
        conn.commit()
    
    # Insertar productos de ejemplo
    cursor.execute("SELECT COUNT(*) as count FROM productos")
    if cursor.fetchone()['count'] == 0:
        productos = [
            ('LAP001', 'Laptop HP Pavilion 15', 'Laptop con procesador Intel Core i5, 8GB RAM, 256GB SSD', 1, 'HP', 'Pavilion 15', 2499.00, 15, 5, None),
            ('LAP002', 'Laptop Lenovo IdeaPad', 'Laptop con procesador AMD Ryzen 5, 16GB RAM, 512GB SSD', 1, 'Lenovo', 'IdeaPad 3', 2799.00, 10, 5, None),
            ('CEL001', 'iPhone 15 Pro', 'Smartphone Apple con chip A17 Pro, 256GB', 2, 'Apple', 'iPhone 15 Pro', 5499.00, 8, 3, None),
            ('CEL002', 'Samsung Galaxy S24', 'Smartphone Samsung con 256GB y cámara de 50MP', 2, 'Samsung', 'Galaxy S24', 4299.00, 12, 5, None),
            ('TAB001', 'iPad Air', 'Tablet Apple con chip M1 y pantalla de 10.9"', 3, 'Apple', 'iPad Air', 3499.00, 6, 3, None),
            ('ACC001', 'Mouse Logitech MX Master', 'Mouse ergonómico inalámbrico', 4, 'Logitech', 'MX Master 3S', 349.00, 25, 10, None),
            ('ACC002', 'Teclado Mecánico RGB', 'Teclado gaming con switches mecánicos', 4, 'Corsair', 'K95 RGB', 599.00, 18, 8, None),
            ('AUD001', 'Audífonos Sony WH-1000XM5', 'Audífonos con cancelación de ruido', 6, 'Sony', 'WH-1000XM5', 1299.00, 20, 10, None)
        ]
        cursor.executemany('''
            INSERT INTO productos (codigo, nombre, descripcion, categoria_id, marca, modelo, precio, stock, stock_minimo, imagen_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', productos)
        conn.commit()
    
    conn.close()

def registrar_historial_stock(producto_id, usuario_id, cantidad_anterior, cantidad_nueva, tipo_movimiento, motivo=''):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO historial_stock (producto_id, usuario_id, cantidad_anterior, cantidad_nueva, tipo_movimiento, motivo)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (producto_id, usuario_id, cantidad_anterior, cantidad_nueva, tipo_movimiento, motivo))
    conn.commit()
    conn.close()

# Decorador para requerir login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Por favor inicia sesión para acceder', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Decorador para requerir rol de administrador
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Por favor inicia sesión para acceder', 'warning')
            return redirect(url_for('login'))
        if session.get('rol') != 'administrador':
            flash('No tienes permisos para acceder a esta sección', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# Rutas de autenticación
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Validar campos vacíos
        if not username or not password:
            flash('Por favor completa todos los campos', 'warning')
            return render_template('login.html')
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM usuarios WHERE username = ? AND activo = 1', (username,))
        user = cursor.fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['nombre_completo'] = user['nombre_completo']
            session['rol'] = user['rol']
            flash(f'Bienvenido {user["nombre_completo"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Usuario o contraseña incorrectos', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada exitosamente', 'info')
    return redirect(url_for('login'))

# Dashboard principal
@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_db()
    cursor = conn.cursor()
    
    # Obtener estadísticas
    cursor.execute('SELECT COUNT(*) as total FROM productos WHERE activo = 1')
    total_productos = cursor.fetchone()['total']
    
    cursor.execute('SELECT COUNT(*) as total FROM productos WHERE activo = 1 AND stock <= stock_minimo')
    productos_bajo_stock = cursor.fetchone()['total']
    
    cursor.execute('SELECT COUNT(*) as total FROM ventas WHERE DATE(fecha_venta) = DATE("now")')
    ventas_hoy = cursor.fetchone()['total']
    
    cursor.execute('SELECT COALESCE(SUM(total), 0) as total FROM ventas WHERE DATE(fecha_venta) = DATE("now")')
    ingresos_hoy = cursor.fetchone()['total']
    
    # Productos con bajo stock
    cursor.execute('''
        SELECT p.*, c.nombre as categoria_nombre
        FROM productos p
        LEFT JOIN categorias c ON p.categoria_id = c.id
        WHERE p.activo = 1 AND p.stock <= p.stock_minimo
        ORDER BY p.stock ASC
        LIMIT 5
    ''')
    productos_alerta = cursor.fetchall()
    
    # Últimas ventas
    cursor.execute('''
        SELECT v.*, u.nombre_completo as vendedor, c.nombre as cliente_nombre
            CASE 
               WHEN c.nombre IS NOT NULL THEN c.nombre || ' ' || c.apellido
               ELSE 'Cliente General'
            END as cliente_nombre
        FROM ventas v
        LEFT JOIN usuarios u ON v.usuario_id = u.id
        LEFT JOIN clientes c ON v.cliente_id = c.id
        ORDER BY v.fecha_venta DESC
        LIMIT 5
    ''')
    ultimas_ventas = cursor.fetchall()
    
    conn.close()
    
    return render_template('dashboard.html',
                         total_productos=total_productos,
                         productos_bajo_stock=productos_bajo_stock,
                         ventas_hoy=ventas_hoy,
                         ingresos_hoy=ingresos_hoy,
                         productos_alerta=productos_alerta,
                         ultimas_ventas=ultimas_ventas)

# Gestión de productos
@app.route('/productos')
@login_required
def productos():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT p.*, c.nombre as categoria_nombre
        FROM productos p
        LEFT JOIN categorias c ON p.categoria_id = c.id
        WHERE p.activo = 1
        ORDER BY p.nombre
    ''')
    productos = cursor.fetchall()
    
    cursor.execute('SELECT * FROM categorias WHERE activo = 1 ORDER BY nombre')
    categorias = cursor.fetchall()
    conn.close()
    
    return render_template('productos.html', productos=productos, categorias=categorias)

@app.route('/api/producto/<int:id>')
@login_required
def api_producto(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM productos WHERE id = ? AND activo = 1', (id,))
    producto = cursor.fetchone()
    conn.close()
    
    if producto:
        return jsonify({
            'id': producto['id'],
            'codigo': producto['codigo'],
            'nombre': producto['nombre'],
            'precio': producto['precio'],
            'stock': producto['stock']
        })
    return jsonify({'error': 'Producto no encontrado'}), 404

@app.route('/producto/nuevo', methods=['GET', 'POST'])
@admin_required
def nuevo_producto():
    if request.method == 'POST':
        conn = get_db()
        cursor = conn.cursor()
        
        try:
            codigo = request.form.get('codigo', '').strip().upper()
            nombre = request.form.get('nombre', '').strip()
            precio = float(request.form.get('precio', 0))
            stock  = int(request.form.get('stock', 0))
            
            # Validar campos obligatorios
            if not codigo or not nombre or precio <= 0:
                flash('Por favor completa todos los campos obligatorios correctamente', 'danger')
                raise ValueError('Datos incompletos')
            
            cursor.execute('''
                INSERT INTO productos (codigo, nombre, descripcion, categoria_id, marca, modelo, precio, stock, stock_minimo)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                request.form['codigo'],
                request.form['nombre'],
                request.form['descripcion'],
                request.form['categoria_id'] if request.form['categoria_id'] else None,
                request.form['marca'],
                request.form['modelo'],
                request.form['precio'],
                request.form['stock'],
                request.form['stock_minimo']
            ))
            conn.commit()
            flash('Producto creado exitosamente', 'success')
            return redirect(url_for('productos'))
        except sqlite3.IntegrityError:
            flash('El código del producto ya existe', 'danger')
        finally:
            conn.close()
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM categorias WHERE activo = 1 ORDER BY nombre')
    categorias = cursor.fetchall()
    conn.close()
    
    return render_template('producto_form.html', categorias=categorias)

@app.route('/producto/editar/<int:id>', methods=['GET', 'POST'])
@admin_required
def editar_producto(id):
    conn = get_db()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        try:
            cursor.execute('''
                UPDATE productos
                SET codigo = ?, nombre = ?, descripcion = ?, categoria_id = ?,
                    marca = ?, modelo = ?, precio = ?, stock = ?, stock_minimo = ?
                WHERE id = ?
            ''', (
                request.form['codigo'],
                request.form['nombre'],
                request.form['descripcion'],
                request.form['categoria_id'] if request.form['categoria_id'] else None,
                request.form['marca'],
                request.form['modelo'],
                request.form['precio'],
                request.form['stock'],
                request.form['stock_minimo'],
                id
            ))
            conn.commit()
            flash('Producto actualizado exitosamente', 'success')
            return redirect(url_for('productos'))
        except sqlite3.IntegrityError:
            flash('El código del producto ya existe', 'danger')
        finally:
            conn.close()
    
    cursor.execute('SELECT stock FROM productos WHERE id = ?', (id,))
    stock_anterior = cursor.fetchone()['stock']
    stock_nuevo = int(request.form.get('stock', 0))

    cursor.execute('SELECT * FROM productos WHERE id = ?', (id,))
    producto = cursor.fetchone()

# Registrar cambio de stock si hubo modificación
    if stock_anterior != stock_nuevo:
        tipo = 'entrada' if stock_nuevo > stock_anterior else 'salida'
        registrar_historial_stock(id, session['user_id'], stock_anterior, stock_nuevo, tipo, 'Ajuste manual')                                   

    cursor.execute('SELECT * FROM categorias WHERE activo = 1 ORDER BY nombre')
    categorias = cursor.fetchall()
    conn.close()
    
    return render_template('producto_form.html', producto=producto, categorias=categorias)

@app.route('/producto/<int:id>/historial')
@login_required
def historial_producto(id):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM productos WHERE id = ?', (id,))
    producto = cursor.fetchone()
    
    if not producto:
        flash('Producto no encontrado', 'danger')
        return redirect(url_for('productos'))
    
    cursor.execute('''
        SELECT h.*, u.nombre_completo as usuario
        FROM historial_stock h
        LEFT JOIN usuarios u ON h.usuario_id = u.id
        WHERE h.producto_id = ?
        ORDER BY h.fecha DESC
        LIMIT 50
    ''', (id,))
    historial = cursor.fetchall()
    
    conn.close()
    
    return render_template('historial_stock.html', producto=producto, historial=historial)

@app.route('/producto/eliminar/<int:id>')
@admin_required
def eliminar_producto(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('UPDATE productos SET activo = 0 WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('Producto eliminado exitosamente', 'success')
    return redirect(url_for('productos'))

# Gestión de ventas
@app.route('/ventas')
@login_required
def ventas():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT v.*, u.nombre_completo as vendedor, 
               c.nombre || ' ' || c.apellido as cliente_nombre
        FROM ventas v
        LEFT JOIN usuarios u ON v.usuario_id = u.id
        LEFT JOIN clientes c ON v.cliente_id = c.id
        ORDER BY v.fecha_venta DESC
    ''')
    ventas = cursor.fetchall()
    conn.close()
    
    return render_template('ventas.html', ventas=ventas)

@app.route('/venta/nueva', methods=['GET', 'POST'])
@login_required
def nueva_venta():
    if request.method == 'POST':
        conn = get_db()
        cursor = conn.cursor()
        
        try:
            # Obtener datos del formulario
            cliente_id = request.form.get('cliente_id')
            productos_ids = request.form.getlist('producto_id[]')
            cantidades = request.form.getlist('cantidad[]')
            
            documento = request.form.get('documento', '').strip()
            nombre = request.form.get('nombre', '').strip()
            apellido = request.form.get('apellido', '').strip()

            if not documento or not nombre or not apellido:
                flash('Por favor completa los campos obligatorios', 'danger')
                return render_template('cliente_form.html')

            if not productos_ids:
                flash('Debe agregar al menos un producto', 'danger')
                return redirect(url_for('nueva_venta'))
            
            # Calcular totales
            subtotal = 0
            detalles = []
            
            for prod_id, cant in zip(productos_ids, cantidades):
                if not prod_id or not cant:
                    continue

                cursor.execute('SELECT * FROM productos WHERE id = ?', (prod_id,))
                producto = cursor.fetchone()
                
                if not producto:
                    flash(f'Producto no encontrado', 'danger')
                    return redirect(url_for('nueva_venta'))
            
                if int(cant) > producto['stock']:
                    flash(f'Stock insuficiente para {producto["nombre"]}. Disponible: {producto["stock"]}', 'danger')
                    return redirect(url_for('nueva_venta'))

                cantidad = int(cant)
                precio_unitario = producto['precio']
                subtotal_item = precio_unitario * cantidad
                
                detalles.append({
                    'producto_id': prod_id,
                    'cantidad': cantidad,
                    'precio_unitario': precio_unitario,
                    'subtotal': subtotal_item
                })
                
                subtotal += subtotal_item
            
            igv = subtotal * 0.18
            total = subtotal + igv
            
            # Generar número de venta
            cursor.execute('SELECT COUNT(*) as count FROM ventas')
            num_venta = f"VTA-{cursor.fetchone()['count'] + 1:06d}"
            
            # Insertar venta
            cursor.execute('''
                INSERT INTO ventas (numero_venta, cliente_id, usuario_id, subtotal, igv, total, metodo_pago, observaciones)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                num_venta,
                cliente_id if cliente_id else None,
                session['user_id'],
                subtotal,
                igv,
                total,
                request.form['metodo_pago'],
                request.form.get('observaciones', '')
            ))
            
            venta_id = cursor.lastrowid
            
            # Insertar detalles y actualizar stock
            for detalle in detalles:
                cursor.execute('''
                    INSERT INTO detalle_ventas (venta_id, producto_id, cantidad, precio_unitario, subtotal)
                    VALUES (?, ?, ?, ?, ?)
                ''', (venta_id, detalle['producto_id'], detalle['cantidad'], 
                      detalle['precio_unitario'], detalle['subtotal']))
                
                cursor.execute('''
                    UPDATE productos SET stock = stock - ? WHERE id = ?
                ''', (detalle['cantidad'], detalle['producto_id']))
            
            conn.commit()
            flash(f'Venta {num_venta} registrada exitosamente', 'success')
            return redirect(url_for('ventas'))
            
        except Exception as e:
            conn.rollback()
            flash(f'Error al registrar la venta: {str(e)}', 'danger')
        finally:
            conn.close()
    
    # GET: mostrar formulario
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM productos WHERE activo = 1 AND stock > 0 ORDER BY nombre')
    productos = cursor.fetchall()
    
    cursor.execute('SELECT * FROM clientes ORDER BY nombre, apellido')
    clientes = cursor.fetchall()
    
    conn.close()
    
    return render_template('venta_form.html', productos=productos, clientes=clientes)

@app.route('/venta/detalle/<int:id>')
@login_required
def detalle_venta(id):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT v.*, u.nombre_completo as vendedor,
               c.nombre || ' ' || c.apellido as cliente_nombre,
               c.documento, c.telefono, c.email
        FROM ventas v
        LEFT JOIN usuarios u ON v.usuario_id = u.id
        LEFT JOIN clientes c ON v.cliente_id = c.id
        WHERE v.id = ?
    ''', (id,))
    venta = cursor.fetchone()
    
    cursor.execute('''
        SELECT dv.*, p.nombre as producto_nombre, p.codigo
        FROM detalle_ventas dv
        JOIN productos p ON dv.producto_id = p.id
        WHERE dv.venta_id = ?
    ''', (id,))
    detalles = cursor.fetchall()
    
    conn.close()
    
    return render_template('venta_detalle.html', venta=venta, detalles=detalles)

# Gestión de clientes
@app.route('/clientes')
@login_required
def clientes():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clientes ORDER BY nombre, apellido')
    clientes = cursor.fetchall()
    conn.close()
    
    return render_template('clientes.html', clientes=clientes)

@app.route('/cliente/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_cliente():
    if request.method == 'POST':
        conn = get_db()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO clientes (documento, tipo_documento, nombre, apellido, email, telefono, direccion)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                request.form['documento'],
                request.form['tipo_documento'],
                request.form['nombre'],
                request.form['apellido'],
                request.form['email'],
                request.form['telefono'],
                request.form['direccion']
            ))
            conn.commit()
            flash('Cliente registrado exitosamente', 'success')
            return redirect(url_for('clientes'))
        except sqlite3.IntegrityError:
            flash('El documento ya está registrado', 'danger')
        finally:
            conn.close()
    
    return render_template('cliente_form.html')

@app.route('/reportes')
@admin_required
def reportes():
    conn = get_db()
    cursor = conn.cursor()
    
    # Productos más vendidos
    cursor.execute('''
        SELECT p.nombre, p.codigo, SUM(dv.cantidad) as total_vendido
        FROM detalle_ventas dv
        JOIN productos p ON dv.producto_id = p.id
        GROUP BY dv.producto_id
        ORDER BY total_vendido DESC
        LIMIT 10
    ''')
    productos_top = cursor.fetchall()
    
    # Ventas por mes
    cursor.execute('''
        SELECT strftime('%Y-%m', fecha_venta) as mes, 
               COUNT(*) as num_ventas,
               SUM(total) as total_ingresos
        FROM ventas
        GROUP BY mes
        ORDER BY mes DESC
        LIMIT 12
    ''')
    ventas_mensuales = cursor.fetchall()
    
    conn.close()
    
    return render_template('reportes.html', 
                         productos_top=productos_top,
                         ventas_mensuales=ventas_mensuales)

# Gestión de usuarios (solo administrador)
@app.route('/usuarios')
@admin_required
def usuarios():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM usuarios ORDER BY nombre_completo')
    usuarios = cursor.fetchall()
    conn.close()
    
    return render_template('usuarios.html', usuarios=usuarios)

@app.route('/usuario/nuevo', methods=['GET', 'POST'])
@admin_required
def nuevo_usuario():
    if request.method == 'POST':
        conn = get_db()
        cursor = conn.cursor()
        
        try:
            hash_password = generate_password_hash(request.form['password'])
            cursor.execute('''
                INSERT INTO usuarios (username, password, nombre_completo, email, rol)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                request.form['username'],
                hash_password,
                request.form['nombre_completo'],
                request.form['email'],
                request.form['rol']
            ))
            conn.commit()
            flash('Usuario creado exitosamente', 'success')
            return redirect(url_for('usuarios'))
        except sqlite3.IntegrityError:
            flash('El nombre de usuario o email ya existe', 'danger')
        finally:
            conn.close()
    
    return render_template('usuario_form.html')

# Categorías (solo administrador)
@app.route('/categorias')
@admin_required
def categorias():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM categorias WHERE activo = 1 ORDER BY nombre')
    categorias = cursor.fetchall()
    conn.close()
    
    return render_template('categorias.html', categorias=categorias)

if __name__ == '__main__':
  def init_db():
    """Inicializa la base de datos con las tablas necesarias"""
    conn = get_db()
    cursor = conn.cursor()
    
    # ... todas tus tablas aquí ...
    
    # Insertar productos de ejemplo
    cursor.execute("SELECT COUNT(*) as count FROM productos")
    if cursor.fetchone()['count'] == 0:
        productos = [
            # ... tus productos ...
        ]
        cursor.executemany('''
            INSERT INTO productos (codigo, nombre, descripcion, categoria_id, marca, modelo, precio, stock, stock_minimo, imagen_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', productos)
        conn.commit()
    
    # ⭐ AGREGAR AQUÍ LOS ÍNDICES (antes de conn.close())
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_productos_activo ON productos(activo)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_productos_stock ON productos(stock)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_ventas_fecha ON ventas(fecha_venta)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_ventas_usuario ON ventas(usuario_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_detalle_venta ON detalle_ventas(venta_id)')
    conn.commit()
    
    conn.close()
