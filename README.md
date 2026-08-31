# Taller Sistemas Distribuidos

Implementación directa de protocolos de comunicación distribuida: **REST (HTTP/1.1)** y **gRPC (HTTP/2)**.

## Requisitos

- Python 3.8+
- Dependencias:

```bash
pip3 install grpcio grpcio-tools
```

## Estructura

```
.
├── servidor_rest.py        # Servidor REST (HTTP/1.1)
├── cliente_rest.py         # Cliente REST
├── inventario.proto        # Definición del servicio gRPC
├── inventario_pb2.py       # Código generado del proto
├── inventario_pb2_grpc.py  # Código generado del proto (stub)
├── servidor_grpc.py        # Servidor gRPC (HTTP/2)
└── cliente_grpc.py         # Cliente gRPC
```

## Parte 1: REST (HTTP/1.1)

### Servidor

Expone un catálogo de productos con los endpoints:

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/productos` | Consultar catálogo completo |
| `POST` | `/productos` | Registrar nuevo producto |

```bash
python3 servidor_rest.py
```

El servidor inicia en `http://localhost:8080`.

### Cliente

Realiza peticiones al servidor y muestra un análisis de overhead HTTP:

```bash
python3 cliente_rest.py
```

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

### Definición del servicio (inventario.proto)

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

## Comparación: gRPC vs REST

| Característica | REST | gRPC |
|----------------|------|------|
| Serialización | JSON (texto) | Protocol Buffers (binario) |
| Protocolo | HTTP/1.1 | HTTP/2 |
| Tamaño payload | Mayor | 30-50% menor |
| Multiplexing | No | Sí |
| Streaming | No nativo | Sí |
| Contrato | Sin tipado | .proto fuerte |
| Latencia | Mayor | Menor |

### Ventajas de gRPC en microservicios

- **Rendimiento**: Serialización binaria reduce tamaño de mensajes y tiempo de parsing.
- **HTTP/2**: Multiplexing permite múltiples llamadas paralelas en una conexión.
- **Contrato fuerte**: Los archivos `.proto` garantizan compatibilidad entre clientes y servidores.
- **Streaming**: Soporte nativo para flujos de datos bidireccionales.
- **Code generation**: Genera automáticamente stubs en múltiples lenguajes.
