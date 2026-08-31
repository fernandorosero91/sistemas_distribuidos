"""
Taller Sistemas Distribuidos - Parte 1: REST (HTTP/1.1)
Servidor HTTP que expone un catálogo de productos.
"""

import json
from http.server import HTTPServer, BaseHTTPRequestHandler


# Catálogo de productos en memoria
productos = [
    {"id": 1, "nombre": "Laptop", "precio": 999.99, "stock": 15},
    {"id": 2, "nombre": "Mouse", "precio": 25.50, "stock": 100},
    {"id": 3, "nombre": "Teclado", "precio": 45.00, "stock": 50},
]

siguiente_id = 4


class ProductosHandler(BaseHTTPRequestHandler):
    """Handler para manejar peticiones REST de productos."""

    def _enviar_respuesta(self, codigo, datos):
        """Envía una respuesta JSON con el código de estado dado."""
        self.send_response(codigo)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(datos, ensure_ascii=False).encode("utf-8"))

    def do_GET(self):
        """GET /productos - Retorna el catálogo completo."""
        if self.path == "/productos":
            print(f"[SERVIDOR] GET /productos -> 200 OK ({len(productos)} productos)")
            self._enviar_respuesta(200, {"productos": productos, "total": len(productos)})
        else:
            self._enviar_respuesta(404, {"error": "Endpoint no encontrado"})

    def do_POST(self):
        """POST /productos - Registra un nuevo producto."""
        if self.path == "/productos":
            global siguiente_id
            try:
                longitud = int(self.headers.get("Content-Length", 0))
                cuerpo = self.rfile.read(longitud)
                datos = json.loads(cuerpo.decode("utf-8"))

                nuevo_producto = {
                    "id": siguiente_id,
                    "nombre": datos.get("nombre", ""),
                    "precio": float(datos.get("precio", 0)),
                    "stock": int(datos.get("stock", 0)),
                }
                siguiente_id += 1
                productos.append(nuevo_producto)

                print(f"[SERVIDOR] POST /productos -> 201 Creado: {nuevo_producto}")
                self._enviar_respuesta(201, {"mensaje": "Producto registrado", "producto": nuevo_producto})
            except (json.JSONDecodeError, ValueError) as e:
                self._enviar_respuesta(400, {"error": f"Datos inválidos: {e}"})
        else:
            self._enviar_respuesta(404, {"error": "Endpoint no encontrado"})

    def do_OPTIONS(self):
        """Maneja preflight CORS."""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()


def main():
    host = "localhost"
    puerto = 8080
    servidor = HTTPServer((host, puerto), ProductosHandler)
    print(f"========================================")
    print(f"  SERVIDOR REST - Catálogo de Productos")
    print(f"  http://{host}:{puerto}")
    print(f"  GET  /productos  -> Consultar catálogo")
    print(f"  POST /productos  -> Registrar producto")
    print(f"========================================")
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\n[SERVIDOR] Deteniendo servidor...")
        servidor.server_close()
        print("[SERVIDOR] Servidor detenido.")


if __name__ == "__main__":
    main()
