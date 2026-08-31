"""
Taller Sistemas Distribuidos - Parte 3: WebSockets (TCP)
Servidor WebSocket para chat en tiempo real y notificaciones de productos.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import uvicorn
import json
from datetime import datetime


app = FastAPI(title="WebSockets - Chat y Notificaciones")


# Gestor de conexiones activas
class ConnectionManager:
    def __init__(self):
        self.conexiones: list[WebSocket] = []

    async def conectar(self, websocket: WebSocket):
        await websocket.accept()
        self.conexiones.append(websocket)
        print(f"[WS] Cliente conectado. Total: {len(self.conexiones)}")

    def desconectar(self, websocket: WebSocket):
        self.conexiones.remove(websocket)
        print(f"[WS] Cliente desconectado. Total: {len(self.conexiones)}")

    async def broadcast(self, mensaje: dict):
        for conexion in self.conexiones:
            await conexion.send_json(mensaje)


manager = ConnectionManager()


@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """Chat en tiempo real entre todos los clientes conectados."""
    await manager.conectar(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            mensaje = {
                "tipo": "chat",
                "mensaje": data,
                "hora": datetime.now().strftime("%H:%M:%S"),
                "clientes": len(manager.conexiones)
            }
            await manager.broadcast(mensaje)
    except WebSocketDisconnect:
        manager.desconectar(websocket)


@app.websocket("/ws/productos")
async def websocket_productos(websocket: WebSocket):
    """Notificaciones de cambios en el catalogo de productos."""
    await manager.conectar(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            evento = json.loads(data)

            if evento.get("accion") == "agregar":
                notificacion = {
                    "tipo": "notificacion",
                    "evento": "producto_agregado",
                    "producto": evento.get("producto"),
                    "hora": datetime.now().strftime("%H:%M:%S")
                }
            elif evento.get("accion") == "eliminar":
                notificacion = {
                    "tipo": "notificacion",
                    "evento": "producto_eliminado",
                    "producto": evento.get("producto"),
                    "hora": datetime.now().strftime("%H:%M:%S")
                }
            else:
                notificacion = {
                    "tipo": "notificacion",
                    "evento": "actualizacion",
                    "datos": evento,
                    "hora": datetime.now().strftime("%H:%M:%S")
                }

            await manager.broadcast(notificacion)
    except WebSocketDisconnect:
        manager.desconectar(websocket)


@app.get("/", response_class=HTMLResponse)
def interfaz():
    return """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WebSockets - Chat y Notificaciones</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', sans-serif; background: #0f0f23; color: #e0e0e0; }
        .container { display: grid; grid-template-columns: 1fr 1fr; height: 100vh; gap: 2px; }
        .panel { background: #1a1a2e; padding: 20px; display: flex; flex-direction: column; }
        .panel h2 { color: #00d4ff; margin-bottom: 15px; font-size: 1.1em; }
        .panel h2 i { margin-right: 8px; }
        .status { display: flex; align-items: center; gap: 8px; margin-bottom: 15px; font-size: 0.85em; }
        .status-dot { width: 10px; height: 10px; border-radius: 50%; background: #ff4444; }
        .status-dot.online { background: #00ff88; animation: pulse 1.5s infinite; }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
        .mensajes { flex: 1; overflow-y: auto; padding: 10px; background: #0f0f23; border-radius: 8px; margin-bottom: 15px; }
        .mensaje { padding: 8px 12px; margin-bottom: 8px; border-radius: 8px; max-width: 80%; }
        .mensaje.enviado { background: #00d4ff22; border-left: 3px solid #00d4ff; margin-left: auto; }
        .mensaje.recibido { background: #1a1a3e; border-left: 3px solid #ff6b6b; }
        .mensaje.sistema { background: #2a2a4e; border-left: 3px solid #ffd93d; text-align: center; max-width: 100%; font-size: 0.85em; color: #aaa; }
        .mensaje .hora { font-size: 0.75em; color: #888; margin-top: 4px; }
        .mensaje .clientes { font-size: 0.75em; color: #00ff88; }
        .input-area { display: flex; gap: 10px; }
        .input-area input { flex: 1; padding: 12px; border: 1px solid #333; border-radius: 8px; background: #0f0f23; color: white; font-size: 14px; }
        .input-area input:focus { outline: none; border-color: #00d4ff; }
        .input-area button { padding: 12px 20px; border: none; border-radius: 8px; cursor: pointer; font-weight: 600; }
        .btn-enviar { background: #00d4ff; color: #0f0f23; }
        .btn-enviar:hover { background: #00b8d4; }
        .btn-notificar { background: #ff6b6b; color: white; }
        .btn-notificar:hover { background: #ff5252; }
        .acciones { display: flex; gap: 10px; margin-top: 10px; }
        .acciones button { flex: 1; padding: 10px; border: none; border-radius: 8px; cursor: pointer; font-size: 0.85em; font-weight: 600; }
        .btn-agregar { background: #00ff8822; color: #00ff88; border: 1px solid #00ff8844; }
        .btn-eliminar { background: #ff444422; color: #ff4444; border: 1px solid #ff444444; }
        .info-box { background: #0f0f23; padding: 15px; border-radius: 8px; margin-top: 15px; font-size: 0.85em; }
        .info-box p { margin-bottom: 8px; color: #aaa; }
        .info-box code { background: #2a2a4e; padding: 2px 6px; border-radius: 4px; color: #00d4ff; }
    </style>
</head>
<body>
    <div class="container">
        <div class="panel">
            <h2><i class="fas fa-comments"></i> Chat en Tiempo Real</h2>
            <div class="status">
                <div class="status-dot" id="status-chat"></div>
                <span id="status-text-chat">Desconectado</span>
            </div>
            <div class="mensajes" id="mensajes-chat"></div>
            <div class="input-area">
                <input type="text" id="input-chat" placeholder="Escribe un mensaje..." onkeypress="if(event.key==='Enviar') enviarChat()">
                <button class="btn-enviar" onclick="enviarChat()"><i class="fas fa-paper-plane"></i> Enviar</button>
            </div>
        </div>

        <div class="panel">
            <h2><i class="fas fa-bell"></i> Notificaciones de Productos</h2>
            <div class="status">
                <div class="status-dot" id="status-notif"></div>
                <span id="status-text-notif">Desconectado</span>
            </div>
            <div class="mensajes" id="mensajes-notif"></div>
            <div class="acciones">
                <button class="btn-agregar" onclick="notificarAccion('agregar')"><i class="fas fa-plus"></i> Agregar Producto</button>
                <button class="btn-eliminar" onclick="notificarAccion('eliminar')"><i class="fas fa-trash"></i> Eliminar Producto</button>
            </div>
            <div class="info-box">
                <p><strong>Protocolo:</strong> WebSocket (TCP)</p>
                <p><strong>Puerto:</strong> 8081</p>
                <p><strong>Endpoints:</strong></p>
                <p><code>ws://localhost:8081/ws/chat</code></p>
                <p><code>ws://localhost:8081/ws/productos</code></p>
            </div>
        </div>
    </div>

    <script>
        let wsChat, wsNotif;

        function conectarChat() {
            wsChat = new WebSocket('ws://localhost:8081/ws/chat');
            wsChat.onopen = () => {
                document.getElementById('status-chat').classList.add('online');
                document.getElementById('status-text-chat').textContent = 'Conectado';
                agregarMensaje('sistema', 'Conectado al chat', '', '', 'mensajes-chat');
            };
            wsChat.onmessage = (e) => {
                const data = JSON.parse(e.data);
                agregarMensaje('recibido', data.mensaje, data.hora, data.clientes + ' conectados', 'mensajes-chat');
            };
            wsChat.onclose = () => {
                document.getElementById('status-chat').classList.remove('online');
                document.getElementById('status-text-chat').textContent = 'Desconectado';
            };
        }

        function conectarNotificaciones() {
            wsNotif = new WebSocket('ws://localhost:8081/ws/productos');
            wsNotif.onopen = () => {
                document.getElementById('status-notif').classList.add('online');
                document.getElementById('status-text-notif').textContent = 'Conectado';
                agregarMensaje('sistema', 'Suscrito a notificaciones', '', '', 'mensajes-notif');
            };
            wsNotif.onmessage = (e) => {
                const data = JSON.parse(e.data);
                const texto = data.evento === 'producto_agregado'
                    ? 'Nuevo producto: ' + data.producto
                    : data.evento === 'producto_eliminado'
                    ? 'Producto eliminado: ' + data.producto
                    : 'Actualizacion: ' + JSON.stringify(data.datos);
                agregarMensaje('recibido', texto, data.hora, '', 'mensajes-notif');
            };
            wsNotif.onclose = () => {
                document.getElementById('status-notif').classList.remove('online');
                document.getElementById('status-text-notif').textContent = 'Desconectado';
            };
        }

        function enviarChat() {
            const input = document.getElementById('input-chat');
            if (input.value.trim() && wsChat.readyState === WebSocket.OPEN) {
                wsChat.send(input.value);
                agregarMensaje('enviado', input.value, new Date().toLocaleTimeString(), '', 'mensajes-chat');
                input.value = '';
            }
        }

        function notificarAccion(accion) {
            const producto = accion === 'agregar' ? 'Monitor ' + Math.floor(Math.random() * 100) : 'Producto-' + Math.floor(Math.random() * 100);
            if (wsNotif && wsNotif.readyState === WebSocket.OPEN) {
                wsNotif.send(JSON.stringify({ accion: accion, producto: producto }));
            }
        }

        function agregarMensaje(tipo, texto, hora, extra, contenedorId) {
            const div = document.getElementById(contenedorId);
            const msg = document.createElement('div');
            msg.className = 'mensaje ' + tipo;
            msg.innerHTML = texto + (hora ? '<div class="hora">' + hora + (extra ? ' | ' + extra : '') + '</div>' : '');
            div.appendChild(msg);
            div.scrollTop = div.scrollHeight;
        }

        conectarChat();
        conectarNotificaciones();
    </script>
</body>
</html>
"""


if __name__ == "__main__":
    print("========================================")
    print("  SERVIDOR WEBSOCKETS")
    print("  http://localhost:8081")
    print("  Chat:           ws://localhost:8081/ws/chat")
    print("  Notificaciones: ws://localhost:8081/ws/productos")
    print("========================================")
    uvicorn.run(app, host="0.0.0.0", port=8081)
