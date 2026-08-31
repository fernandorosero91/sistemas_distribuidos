"""
Taller Sistemas Distribuidos - Parte 2: gRPC (HTTP/2)
Servidor gRPC que implementa el servicio Inventario.
"""

import grpc
from concurrent import futures
import inventario_pb2
import inventario_pb2_grpc


# Catálogo de productos en memoria
productos = {
    1: inventario_pb2.Producto(id=1, nombre="Laptop", precio=999.99, stock=15),
    2: inventario_pb2.Producto(id=2, nombre="Mouse", precio=25.50, stock=100),
    3: inventario_pb2.Producto(id=3, nombre="Teclado", precio=45.00, stock=50),
}
siguiente_id = 4


class InventarioServicer(inventario_pb2_grpc.InventarioServicer):
    """Implementación del servicio Inventario."""

    def ObtenerProducto(self, request, context):
        """Obtiene un producto por su ID."""
        producto_id = request.id
        print(f"[SERVIDOR gRPC] ObtenerProducto(id={producto_id})")

        if producto_id in productos:
            producto = productos[producto_id]
            print(f"[SERVIDOR gRPC] -> Encontrado: {producto.nombre}")
            return inventario_pb2.ProductoResponse(
                producto=producto,
                mensaje="Producto encontrado"
            )
        else:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Producto con id={producto_id} no encontrado")
            print(f"[SERVIDOR gRPC] -> No encontrado")
            return inventario_pb2.ProductoResponse()

    def ListarProductos(self, request, context):
        """Lista todos los productos."""
        print(f"[SERVIDOR gRPC] ListarProductos")
        lista = list(productos.values())
        print(f"[SERVIDOR gRPC] -> Retornando {len(lista)} productos")
        return inventario_pb2.ListaResponse(
            productos=lista,
            total=len(lista)
        )

    def RegistrarProducto(self, request, context):
        """Registra un nuevo producto."""
        global siguiente_id
        print(f"[SERVIDOR gRPC] RegistrarProducto(nombre={request.nombre})")

        nuevo = inventario_pb2.Producto(
            id=siguiente_id,
            nombre=request.nombre,
            precio=request.precio,
            stock=request.stock
        )
        siguiente_id += 1
        productos[nuevo.id] = nuevo

        print(f"[SERVIDOR gRPC] -> Registrado: id={nuevo.id}, {nuevo.nombre}")
        return inventario_pb2.ProductoResponse(
            producto=nuevo,
            mensaje="Producto registrado exitosamente"
        )


def serve():
    host = "localhost"
    puerto = 50051

    servidor = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    inventario_pb2_grpc.add_InventarioServicer_to_server(InventarioServicer(), servidor)
    servidor.add_insecure_port(f"{host}:{puerto}")
    servidor.start()

    print(f"========================================")
    print(f"  SERVIDOR gRPC - Inventario")
    print(f"  {host}:{puerto}")
    print(f"  Protocolo: HTTP/2 + Protocol Buffers")
    print(f"  Servicios:")
    print(f"    - ObtenerProducto")
    print(f"    - ListarProductos")
    print(f"    - RegistrarProducto")
    print(f"========================================")

    try:
        servidor.wait_for_termination()
    except KeyboardInterrupt:
        print("\n[SERVIDOR gRPC] Deteniendo servidor...")
        servidor.stop(grace=5)
        print("[SERVIDOR gRPC] Servidor detenido.")


if __name__ == "__main__":
    serve()
