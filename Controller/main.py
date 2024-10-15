
from fastapi import FastAPI
from .wsockets.manager import WebSocket, wsManager, WebSocketDisconnect
from .wsockets.interpreter import interpret

app = FastAPI()


manager = wsManager()

@app.websocket('/room')
async def wsroom (room: WebSocket, clientName: str):
    await manager.connect(room)

    try:
        while True:
            message = await manager.receive_message (room, clientName)
            await manager.broadcast(room, clientName, message)
    except WebSocketDisconnect:
        await manager.disconnect(room, clientName)
