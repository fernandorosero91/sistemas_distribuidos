"""
Taller Sistemas Distribuidos - Parte 1: REST (HTTP/1.1)
Servidor FastAPI con interfaz web para probar el catálogo de productos.
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn


app = FastAPI(title="API Productos", version="1.0.0")


class ProductoBase(BaseModel):
    nombre: str
    precio: float
    stock: int


class Producto(ProductoBase):
    id: int


productos: list[dict] = [
    {"id": 1, "nombre": "Laptop", "precio": 999.99, "stock": 15},
    {"id": 2, "nombre": "Mouse", "precio": 25.50, "stock": 100},
    {"id": 3, "nombre": "Teclado", "precio": 45.00, "stock": 50},
]
siguiente_id = 4


@app.get("/productos")
def listar_productos():
    return {"productos": productos, "total": len(productos)}


@app.post("/productos", status_code=201)
def registrar_producto(producto: ProductoBase):
    global siguiente_id
    nuevo = {"id": siguiente_id, **producto.model_dump()}
    siguiente_id += 1
    productos.append(nuevo)
    return {"mensaje": "Producto registrado", "producto": nuevo}


@app.get("/", response_class=HTMLResponse)
def interfaz():
    return """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Catalogo de Productos</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', sans-serif; background: #f0f2f5; padding: 20px; }
        .container { max-width: 800px; margin: 0 auto; }
        h1 { text-align: center; color: #1a1a2e; margin-bottom: 30px; }
        h1 i { color: #e94560; margin-right: 10px; }
        .card { background: white; border-radius: 10px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .card h2 { color: #1a1a2e; margin-bottom: 15px; font-size: 1.2em; }
        .card h2 i { margin-right: 8px; color: #e94560; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #eee; }
        th { background: #1a1a2e; color: white; }
        tr:hover { background: #f5f5f5; }
        .form-row { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px; margin-bottom: 15px; }
        .form-group { display: flex; flex-direction: column; }
        .form-group label { font-weight: 600; margin-bottom: 5px; color: #333; }
        .form-group input { padding: 10px; border: 1px solid #ddd; border-radius: 5px; font-size: 14px; }
        .form-group input:focus { outline: none; border-color: #e94560; }
        button { background: #e94560; color: white; border: none; padding: 12px 25px; border-radius: 5px; cursor: pointer; font-size: 14px; font-weight: 600; width: 100%; }
        button:hover { background: #c73650; }
        button i { margin-right: 8px; }
        .msg { padding: 10px; border-radius: 5px; margin-top: 10px; display: none; }
        .msg.ok { background: #d4edda; color: #155724; display: block; }
        .msg.err { background: #f8d7da; color: #721c24; display: block; }
        .info { text-align: center; color: #666; font-size: 0.9em; margin-top: 20px; }
        .info i { color: #e94560; }
    </style>
</head>
<body>
    <div class="container">
        <h1><i class="fas fa-boxes-stacked"></i> Catalogo de Productos</h1>

        <div class="card">
            <h2><i class="fas fa-list"></i> Productos Registrados</h2>
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Nombre</th>
                        <th>Precio</th>
                        <th>Stock</th>
                    </tr>
                </thead>
                <tbody id="lista-productos"></tbody>
            </table>
        </div>

        <div class="card">
            <h2><i class="fas fa-plus-circle"></i> Registrar Producto</h2>
            <form id="form-producto">
                <div class="form-row">
                    <div class="form-group">
                        <label>Nombre</label>
                        <input type="text" id="nombre" required placeholder="Ej: Monitor">
                    </div>
                    <div class="form-group">
                        <label>Precio</label>
                        <input type="number" id="precio" step="0.01" required placeholder="Ej: 299.99">
                    </div>
                    <div class="form-group">
                        <label>Stock</label>
                        <input type="number" id="stock" required placeholder="Ej: 50">
                    </div>
                </div>
                <button type="submit"><i class="fas fa-save"></i> Guardar Producto</button>
            </form>
            <div id="msg" class="msg"></div>
        </div>

        <p class="info"><i class="fas fa-circle-info"></i> API REST con FastAPI - Puerto 8080</p>
    </div>

    <script>
        const API = '/productos';

        async function cargarProductos() {
            const res = await fetch(API);
            const data = await res.json();
            const tbody = document.getElementById('lista-productos');
            tbody.innerHTML = data.productos.map(p => `
                <tr>
                    <td>${p.id}</td>
                    <td>${p.nombre}</td>
                    <td>$${p.precio.toFixed(2)}</td>
                    <td>${p.stock}</td>
                </tr>
            `).join('');
        }

        document.getElementById('form-producto').addEventListener('submit', async (e) => {
            e.preventDefault();
            const msg = document.getElementById('msg');
            try {
                const res = await fetch(API, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        nombre: document.getElementById('nombre').value,
                        precio: parseFloat(document.getElementById('precio').value),
                        stock: parseInt(document.getElementById('stock').value)
                    })
                });
                const data = await res.json();
                msg.className = 'msg ok';
                msg.textContent = data.mensaje + ': ' + data.producto.nombre;
                e.target.reset();
                cargarProductos();
            } catch (err) {
                msg.className = 'msg err';
                msg.textContent = 'Error al registrar producto';
            }
        });

        cargarProductos();
    </script>
</body>
</html>
"""


if __name__ == "__main__":
    print("========================================")
    print("  SERVIDOR REST - Catalogo de Productos")
    print("  http://localhost:8080")
    print("  Interfaz web:      http://localhost:8080")
    print("  Documentacion:     http://localhost:8080/docs")
    print("  ReDoc:             http://localhost:8080/redoc")
    print("========================================")
    uvicorn.run(app, host="0.0.0.0", port=8080)
