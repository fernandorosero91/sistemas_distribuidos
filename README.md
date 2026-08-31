# Taller Sistemas Distribuidos

Implementacion directa de protocolos de comunicacion distribuida: **REST (HTTP/1.1)**, **gRPC (HTTP/2)** y **WebSockets (TCP)**.

## Requisitos

- Python 3.10+
- Dependencias:

```bash
pip3 install -r requirements.txt
```

## Estructura

```
.
├── servidor_rest.py        # Servidor REST con FastAPI + interfaz web
├── cliente_rest.py         # Cliente REST para pruebas
├── inventario.proto        # Definicion del servicio gRPC
├── inventario_pb2.py       # Codigo generado del proto
├── inventario_pb2_grpc.py  # Codigo generado del proto (stub)
├── servidor_grpc.py        # Servidor gRPC (HTTP/2)
├── cliente_grpc.py         # Cliente gRPC
├── servidor_ws.py          # Servidor WebSockets + chat en tiempo real
└── requirements.txt        # Dependencias
```

## Parte 1: REST (HTTP/1.1)

### Servidor

Expone un catalogo de productos con interfaz web incluida.

```bash
python3 servidor_rest.py
```

### URLs disponibles

| URL | Descripcion |
|-----|-------------|
| `http://localhost:8080` | Interfaz web (formulario + tabla) |
| `http://localhost:8080/docs` | Documentacion Swagger UI (probar endpoints) |
| `http://localhost:8080/redoc` | Documentacion ReDoc |
| `http://localhost:8080/productos` | API JSON |

### Endpoints

| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| `GET` | `/productos` | Consultar catalogo completo |
| `POST` | `/productos` | Registrar nuevo producto |
| `GET` | `/` | Interfaz web (formulario + tabla) |

### Prueba con Swagger UI

1. Abre `http://localhost:8080/docs`
2. Haz clic en el endpoint que quieres probar
3. Haz clic en "Try it out"
4. Completa los campos y ejecuta

### Prueba manual con curl

```bash
# Consultar productos
curl http://localhost:8080/productos

# Registrar producto
curl -X POST http://localhost:8080/productos \
  -H "Content-Type: application/json" \
  -d '{"nombre": "Monitor", "precio": 350.00, "stock": 25}'
```

## Parte 2: gRPC (HTTP/2)

### Definicion del servicio (inventario.proto)

```protobuf
service Inventario {
  rpc ObtenerProducto (ProductoRequest) returns (ProductoResponse);
  rpc ListarProductos (ListaRequest) returns (ListaResponse);
  rpc RegistrarProducto (NuevoProductoRequest) returns (ProductoResponse);
}
```

### Compilar el proto

Si modificas `inventario.proto`, recompila:

```bash
python3 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. inventario.proto
```

### Servidor

```bash
python3 servidor_grpc.py
```

El servidor inicia en `localhost:50051`.

### Cliente

```bash
python3 cliente_grpc.py
```

## Comparacion: gRPC vs REST

| Caracteristica | REST | gRPC |
|----------------|------|------|
| Serializacion | JSON (texto) | Protocol Buffers (binario) |
| Protocolo | HTTP/1.1 | HTTP/2 |
| Tamano payload | Mayor | 30-50% menor |
| Multiplexing | No | Si |
| Streaming | No nativo | Si |
| Contrato | Sin tipado | .proto fuerte |
| Latencia | Mayor | Menor |

### Ventajas de gRPC en microservicios

- **Rendimiento**: Serializacion binaria reduce tamano de mensajes y tiempo de parsing.
- **HTTP/2**: Multiplexing permite multiples llamadas paralelas en una conexion.
- **Contrato fuerte**: Los archivos `.proto` garantizan compatibilidad entre clientes y servidores.
- **Streaming**: Soporte nativo para flujos de datos bidireccionales.
- **Code generation**: Genera automaticamente stubs en multiples lenguajes.

## Parte 3: WebSockets (TCP)

### Servidor

Chat en tiempo real y notificaciones de productos via WebSocket.

```bash
python3 servidor_ws.py
```

Abre en el navegador: `http://localhost:8081`

### Endpoints WebSocket

| URL | Descripcion |
|-----|-------------|
| `ws://localhost:8081/ws/chat` | Chat en tiempo real (broadcast a todos los clientes) |
| `ws://localhost:8081/ws/productos` | Notificaciones de cambios en el catalogo |

### Interfaz web

- **Panel izquierdo**: Chat en tiempo real con todos los clientes conectados
- **Panel derecho**: Notificaciones de productos (agregar/eliminar)

### Ejemplo cliente JavaScript

```javascript
// Conectar al chat
const ws = new WebSocket('ws://localhost:8081/ws/chat');

ws.onopen = () => console.log('Conectado');
ws.onmessage = (e) => console.log(JSON.parse(e.data));
ws.send('Hola desde el cliente');
```

## Comparacion de Protocolos

| Caracteristica | REST | gRPC | WebSockets |
|----------------|------|------|------------|
| Protocolo | HTTP/1.1 | HTTP/2 | TCP |
| Conexion | Stateless | Persistente | Persistente |
| Comunicacion | Request-Response | Request-Response | Bidireccional |
| Serializacion | JSON | Protocol Buffers | Texto/Binario |
| Uso principal | CRUD | Microservicios | Tiempo real |
| Latencia | Media | Baja | Muy baja |
