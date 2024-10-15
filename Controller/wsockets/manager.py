
from fastapi import WebSocket, WebSocketDisconnect
from .interpreter import interpret


class wsManager:


    def __init__ (self):
        self.Rooms : list[WebSocket] = []


    async def connect (self, room: WebSocket):
        await room.accept()
        self.Rooms.append (room)

    async def disconnect (self, room: WebSocket, clientName: str):
        self.Rooms.remove (room)
        await self.broadcast_alerts(room, f'{clientName} has left the room !')
        if room.client_state == room.client_state.CONNECTED:
            await room.close()


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


    async def receive_message (self, room: WebSocket, clientName: str):
        message = await room.receive_text ()
        command = await interpret (self, room, clientName, message)


