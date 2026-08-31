"""
Taller Sistemas Distribuidos - Parte 1: REST (HTTP/1.1)
Cliente que consume el servicio REST de productos.
"""

import json
import urllib.request
import urllib.error
import time


BASE_URL = "http://localhost:8080"


def analizar_overhead(respuesta_http):
    """Analiza la sobrecarga de datos (overhead) de los encabezados HTTP."""
    headers_raw = ""
    for clave, valor in respuesta_http.headers.items():
        headers_raw += f"{clave}: {valor}\n"

    tamano_headers = len(headers_raw.encode("utf-8"))
    tamano_cuerpo = len(respuesta_http.read())
    tamano_total = tamano_headers + tamano_cuerpo

    print(f"\n--- Análisis de Overhead HTTP ---")
    print(f"  Tamaño encabezados:  {tamano_headers} bytes")
    print(f"  Tamaño cuerpo:       {tamano_cuerpo} bytes")
    print(f"  Tamaño total:        {tamano_total} bytes")
    if tamano_total > 0:
        overhead = (tamano_headers / tamano_total) * 100
        print(f"  Overhead headers:    {overhead:.1f}%")
    print(f"  Protocolo:           HTTP/1.1")
    print(f"  Formato:             JSON (texto)")
    print(f"--------------------------------\n")

    # Resetear la posición de lectura para poder leer el cuerpo nuevamente
    respuesta_http.read(0)


def consultar_productos():
    """GET /productos - Consulta el catálogo completo."""
    print("[CLIENTE] GET /productos - Consultando catálogo...")
    inicio = time.time()

    req = urllib.request.Request(f"{BASE_URL}/productos", method="GET")
    try:
        with urllib.request.urlopen(req) as respuesta:
            datos = json.loads(respuesta.read().decode("utf-8"))
            elapsed = (time.time() - inicio) * 1000

            print(f"[CLIENTE] Respuesta {respuesta.status} en {elapsed:.1f}ms")
            print(f"  Total productos: {datos['total']}")
            for p in datos["productos"]:
                print(f"  - ID: {p['id']} | {p['nombre']} | ${p['precio']} | Stock: {p['stock']}")

            # Analizar overhead
            analizar_overhead(respuesta)
            return datos
    except urllib.error.URLError as e:
        print(f"[CLIENTE] Error: {e}")
        return None


def registrar_producto(nombre, precio, stock):
    """POST /productos - Registra un nuevo producto."""
    print(f"[CLIENTE] POST /productos - Registrando: {nombre}")
    inicio = time.time()

    datos_producto = json.dumps({
        "nombre": nombre,
        "precio": precio,
        "stock": stock
    }).encode("utf-8")

    req = urllib.request.Request(
        f"{BASE_URL}/productos",
        data=datos_producto,
        method="POST",
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req) as respuesta:
            datos = json.loads(respuesta.read().decode("utf-8"))
            elapsed = (time.time() - inicio) * 1000

            print(f"[CLIENTE] Respuesta {respuesta.status} en {elapsed:.1f}ms")
            print(f"  Mensaje: {datos['mensaje']}")
            print(f"  Producto: {datos['producto']}")

            # Analizar overhead
            analizar_overhead(respuesta)
            return datos
    except urllib.error.URLError as e:
        print(f"[CLIENTE] Error: {e}")
        return None


def main():
    print("=" * 50)
    print("  CLIENTE REST - Catálogo de Productos")
    print("=" * 50)

    # 1. Consultar catálogo existente
    print("\n--- Paso 1: Consultar catálogo ---")
    consultar_productos()

    # 2. Registrar un nuevo producto
    print("\n--- Paso 2: Registrar nuevo producto ---")
    registrar_producto("Monitor 27\"", 350.00, 25)

    # 3. Consultar catálogo actualizado
    print("\n--- Paso 3: Consultar catálogo actualizado ---")
    consultar_productos()


if __name__ == "__main__":
    main()
