# 🛒 Tienda Virtual de Productos Tecnológicos

Sistema de gestión de tienda virtual desarrollado con Flask y SQLite para GPS Management.

## 📋 Características

### Funcionalidades Principales

- **Sistema de Autenticación**: Login seguro con hash de contraseñas
- **Dos Perfiles de Usuario**:
  - **Administrador**: Acceso completo al sistema
  - **Asesor**: Gestión de ventas y clientes

### Módulos del Sistema

1. **Dashboard**
   - Estadísticas en tiempo real
   - Alertas de stock bajo
   - Resumen de ventas del día
   - Últimas transacciones

2. **Gestión de Productos**
   - CRUD completo de productos
   - Control de stock con alertas automáticas
   - Categorización de productos
   - Búsqueda y filtrado

3. **Gestión de Ventas**
   - Registro de ventas con múltiples productos
   - Cálculo automático de IGV (18%)
   - Detalle completo de cada venta
   - Impresión de comprobantes

4. **Gestión de Clientes**
   - Registro de clientes
   - Historial de compras
   - Datos de contacto

5. **Administración** (solo Administrador)
   - Gestión de usuarios
   - Gestión de categorías

## 🗄️ Estructura de la Base de Datos

### Tablas Principales

**usuarios**
- id, username, password (hash), nombre_completo, email, rol, activo, fecha_creacion

**productos**
- id, codigo, nombre, descripcion, categoria_id, marca, modelo, precio, stock, stock_minimo, imagen_url, activo, fecha_creacion

**categorias**
- id, nombre, descripcion, activo

**clientes**
- id, documento, tipo_documento, nombre, apellido, email, telefono, direccion, fecha_registro

**ventas**
- id, numero_venta, cliente_id, usuario_id, fecha_venta, subtotal, igv, total, estado, metodo_pago, observaciones

**detalle_ventas**
- id, venta_id, producto_id, cantidad, precio_unitario, subtotal

## 🚀 Instalación y Configuración

### Requisitos Previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Pasos de Instalación

1. **Clonar o descargar el proyecto**

2. **Crear un entorno virtual** (opcional pero recomendado)
```bash
python -m venv venv
source venv/bin/activate  # En Linux/Mac
venv\Scripts\activate     # En Windows
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Ejecutar la aplicación**
```bash
python app.py
```

5. **Acceder al sistema**
Abrir el navegador en: `http://localhost:5000`

## 👥 Usuarios por Defecto

### Administrador
- **Usuario**: admin
- **Contraseña**: admin123
- **Permisos**: Acceso completo al sistema

### Asesor
- **Usuario**: asesor
- **Contraseña**: asesor123
- **Permisos**: Ventas, productos (vista), clientes

## 📊 Datos de Ejemplo

El sistema incluye:
- 7 categorías de productos tecnológicos
- 8 productos de ejemplo (laptops, smartphones, tablets, accesorios)
- Stock inicial y precios configurados

## 🔒 Seguridad

- Contraseñas encriptadas con Werkzeug
- Sesiones seguras con Flask
- Validación de roles por endpoint
- Protección contra SQL Injection (uso de parámetros)

## 🎨 Interfaz de Usuario

- **Framework CSS**: Bootstrap 5.3
- **Iconos**: Bootstrap Icons
- **Diseño**: Responsive y moderno
- **Colores**: Esquema profesional con gradientes

## 📱 Funcionalidades por Rol

### Administrador Puede:
✅ Gestionar productos (crear, editar, eliminar)
✅ Gestionar usuarios
✅ Gestionar categorías
✅ Realizar ventas
✅ Gestionar clientes
✅ Ver estadísticas completas

### Asesor Puede:
✅ Ver productos
✅ Realizar ventas
✅ Gestionar clientes
✅ Ver estadísticas básicas
❌ No puede gestionar productos, usuarios ni categorías

## 🛠️ Personalización

### Cambiar la clave secreta
En `app.py`, línea 9:
```python
app.secret_key = 'tu_clave_secreta_super_segura_cambiar_en_produccion'
```

### Modificar el puerto
En `app.py`, última línea:
```python
app.run(debug=True, host='0.0.0.0', port=5000)  # Cambiar el puerto aquí
```

### Agregar nuevas categorías
Ejecutar en Python:
```python
from app import get_db
conn = get_db()
cursor = conn.cursor()
cursor.execute("INSERT INTO categorias (nombre, descripcion) VALUES (?, ?)", 
               ("Nueva Categoría", "Descripción"))
conn.commit()
conn.close()
```

## 📈 Características Destacadas

1. **Control de Stock Automático**
   - Alertas cuando el stock está bajo el mínimo
   - Actualización automática al realizar ventas
   - Código de colores en el dashboard

2. **Cálculo Automático de Impuestos**
   - IGV del 18% calculado automáticamente
   - Desglose claro en cada venta

3. **Búsqueda Dinámica**
   - Búsqueda en tiempo real en todas las tablas
   - Sin necesidad de recargar la página

4. **Interfaz Intuitiva**
   - Diseño moderno y profesional
   - Navegación sencilla
   - Responsive para móviles

## 🔄 Flujo de Trabajo Típico

1. **Inicio de Sesión**: Ingresar con credenciales
2. **Dashboard**: Ver estadísticas y alertas
3. **Registrar Cliente** (si es nuevo)
4. **Nueva Venta**:
   - Seleccionar cliente
   - Agregar productos
   - El sistema calcula automáticamente
   - Confirmar venta
5. **Ver Detalle**: Imprimir comprobante si es necesario

## 📝 Notas Importantes

- La base de datos se crea automáticamente al ejecutar el sistema por primera vez
- Los productos de ejemplo ayudan a probar el sistema
- Se recomienda cambiar las contraseñas por defecto en producción
- El sistema está diseñado para uso local o en red interna

## 🚧 Mejoras Futuras Sugeridas

- [ ] Sistema de reportes en PDF/Excel
- [ ] Gráficos de ventas
- [ ] Historial de movimientos de stock
- [ ] Sistema de notificaciones
- [ ] API REST para integración con otros sistemas
- [ ] Carga de imágenes de productos
- [ ] Sistema de descuentos y promociones
- [ ] Multi-moneda

## 📞 Soporte

Para soporte o consultas sobre el sistema, contactar a GPS Management.

---

**Desarrollado para GPS Management** - Sistema de Gestión de Tienda Tecnológica
Versión 1.0 - Diciembre 2024