
from fastapi import FastAPI, WebSocket



app = FastAPI()



@app.websocket('/room')
async def wsroom (room: WebSocket, clientName: str):
    await room.accept()
    while True:
        data = await room.receive_text()
        await room.send_text(data)