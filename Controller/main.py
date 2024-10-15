
from fastapi import FastAPI, WebSocket



app = FastAPI()


class wsManager:
    def __init__ (self):
        self.Rooms : list[WebSocket] = []
    
    async def connect (self, room: WebSocket):
        await room.accept()
        self.Rooms.append (room)

    async def send_message (self, room: WebSocket, clientName: str, message: str):
        await room.send_text(f'{clientName}: {message}.')

    async def broadcast (self, room: WebSocket, clientName: str, message: str):
        for vcRoom in self.Rooms:
            if vcRoom != room:
                await self.send_message (vcRoom, clientName, message)

    async def disconnect (self, room: WebSocket, clientName: str):
        self.Rooms.remove (room)
        await self.broadcast(room, clientName, f'{clientName} has left the room !')



@app.websocket('/room')
async def wsroom (room: WebSocket, clientName: str):
    await room.accept()
    while True:
        data = await room.receive_text()
        await room.send_text(data)