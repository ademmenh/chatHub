
from fastapi import FastAPI, WebSocket, WebSocketDisconnect



app = FastAPI()


class wsManager:
    def __init__ (self):
        self.Rooms : list[WebSocket] = []
    
    async def connect (self, room: WebSocket):
        await room.accept()
        self.Rooms.append (room)

    async def send_message (self, room: WebSocket, clientName: str, message: str):
        await room.send_text (f'{clientName}: {message}')

    async def send_alerts (self, room: WebSocket, message: str):
        await room.send_text (f'{message}')

    async def broadcast (self, room: WebSocket, clientName: str, message: str):
        for vcRoom in self.Rooms:
            if vcRoom != room:
                await self.send_message (vcRoom, clientName, message)

    async def broadcast_alerts (self, room: WebSocket, message: str):
        for vcRoom in self.Rooms:
            if vcRoom != room:
                await self.send_alerts(vcRoom, message)

    async def disconnect (self, room: WebSocket, clientName: str):
        self.Rooms.remove (room)
        await self.broadcast_alerts(room, f'{clientName} has left the room !')



manager = wsManager()

@app.websocket('/room')
async def wsroom (room: WebSocket, clientName: str):
    await manager.connect(room)

    try:
        while True:
            message = await room.receive_text ()
            await manager.broadcast(room, clientName, message)
    except WebSocketDisconnect:
        await manager.disconnect(room, clientName)
