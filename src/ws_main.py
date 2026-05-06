import os
import asyncio
import logging
import socketio
from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.chat.infrastructure.rabbitmq_adapter import RabbitMQAdapter
from src.chat.presentation.socket_gateway import SocketGateway
from src.chat.application.deliver_message import DeliverMessage

logger = logging.getLogger(__name__)

# ── Socket.IO server ──────────────────────────────────────────────────────────
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
sio_app = socketio.ASGIApp(sio)

# ── Wiring ─────────────────────────────────────────────────────────────────────
rabbitmq_url = (
    f"amqp://{os.environ.get('RABBITMQ_USER', 'waslini')}"
    f":{os.environ.get('RABBITMQ_PASSWORD', 'waslini')}"
    f"@{os.environ.get('RABBITMQ_HOST', 'rabbitmq')}:5672/"
)
broker = RabbitMQAdapter(rabbitmq_url)
gateway = SocketGateway(sio, logger)
deliver_message = DeliverMessage(broker, gateway, logger)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    for attempt in range(5):
        try:
            await broker.connect()
            asyncio.create_task(deliver_message.execute())
            logger.info("WS server started successfully")
            break
        except Exception as e:
            logger.error("Startup attempt %d failed: %s", attempt + 1, e)
            await asyncio.sleep(5)
    else:
        logger.critical("Could not start WS server after 5 attempts")
    
    yield
    
    # Shutdown logic
    await broker.disconnect()

app = FastAPI(lifespan=lifespan)
app.mount("/", sio_app)
