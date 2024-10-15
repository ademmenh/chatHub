
async def interpret (manager, room, clientName: str, message: str):
    if message == ':q':
        await manager.disconnect(room, clientName)

        
