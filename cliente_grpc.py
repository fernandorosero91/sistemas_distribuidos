"""
Taller Sistemas Distribuidos - Parte 2: gRPC (HTTP/2)
Cliente gRPC que consume el servicio Inventario.
"""

import grpc
import time
import inventario_pb2
import inventario_pb2_grpc


def analizar_overhead_grpc():
    """Analiza las ventajas de gRPC vs REST en términos de overhead."""
    print(f"\n--- Análisis de Overhead gRPC ---")
    print(f"  Protocolo:           HTTP/2")
    print(f"  Serialización:       Protocol Buffers (binario)")
    print(f"  Overhead headers:    Mínimo (HPACK compression en HTTP/2)")
    print(f"  Tamaño mensaje:      ~30-50% menor que JSON equivalent")
    print(f"  Multiplexing:        Sí (múltiples requests en una conexión)")
    print(f"  Streaming:           Soportado")
    print(f"  Contrato fuerte:     Sí (archivos .proto)")
    print(f"--------------------------------\n")


def main():
    canal = grpc.insecure_channel("localhost:50051")
    stub = inventario_pb2_grpc.InventarioStub(canal)

    print("=" * 50)
    print("  CLIENTE gRPC - Inventario")
    print("=" * 50)

    # 1. Listar productos
    print("\n--- Paso 1: Listar productos ---")
    inicio = time.time()
    respuesta = stub.ListarProductos(inventario_pb2.ListaRequest())
    elapsed = (time.time() - inicio) * 1000
    print(f"[CLIENTE] Respuesta en {elapsed:.1f}ms")
    print(f"  Total: {respuesta.total} productos")
    for p in respuesta.productos:
        print(f"  - ID: {p.id} | {p.nombre} | ${p.precio} | Stock: {p.stock}")

    # 2. Obtener producto específico
    print("\n--- Paso 2: Obtener producto ID=2 ---")
    inicio = time.time()
    respuesta = stub.ObtenerProducto(inventario_pb2.ProductoRequest(id=2))
    elapsed = (time.time() - inicio) * 1000
    print(f"[CLIENTE] Respuesta en {elapsed:.1f}ms")
    print(f"  {respuesta.mensaje}: {respuesta.producto.nombre} - ${respuesta.producto.precio}")

    # 3. Registrar nuevo producto
    print("\n--- Paso 3: Registrar nuevo producto ---")
    inicio = time.time()
    respuesta = stub.RegistrarProducto(inventario_pb2.NuevoProductoRequest(
        nombre="Monitor 27\"",
        precio=350.00,
        stock=25
    ))
    elapsed = (time.time() - inicio) * 1000
    print(f"[CLIENTE] Respuesta en {elapsed:.1f}ms")
    print(f"  {respuesta.mensaje}: ID={respuesta.producto.id}, {respuesta.producto.nombre}")

    # 4. Listar productos actualizados
    print("\n--- Paso 4: Listar productos actualizados ---")
    inicio = time.time()
    respuesta = stub.ListarProductos(inventario_pb2.ListaRequest())
    elapsed = (time.time() - inicio) * 1000
    print(f"[CLIENTE] Respuesta en {elapsed:.1f}ms")
    print(f"  Total: {respuesta.total} productos")
    for p in respuesta.productos:
        print(f"  - ID: {p.id} | {p.nombre} | ${p.precio} | Stock: {p.stock}")

    # Análisis de overhead
    analizar_overhead_grpc()

    canal.close()


if __name__ == "__main__":
    main()
