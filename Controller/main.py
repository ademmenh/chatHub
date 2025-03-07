
from fastapi import FastAPI
from .wsockets.manager import WebSocket, wsManager, WebSocketDisconnect

app = FastAPI()


manager = wsManager()

@app.websocket('/room')
async def wsroom (room: WebSocket, clientName: str):
    await manager.connect(room)

    try:
        while True:
            message = await manager.receive_message (room)
            await manager.broadcast(room, clientName, message)
    except WebSocketDisconnect:
        await manager.disconnect(room, clientName)
