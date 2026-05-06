import json
import logging
import aio_pika
from ..domain.ports import IMessageBroker

class RabbitMQAdapter(IMessageBroker):
    """Infrastructure adapter that implements IMessageBroker via RabbitMQ."""

    EXCHANGE_NAME = "chat_events"

    def __init__(self, url: str, logger: logging.Logger) -> None:
        self._url = url
        self._logger = logger
        self._connection: aio_pika.abc.AbstractRobustConnection | None = None
        self._channel: aio_pika.abc.AbstractChannel | None = None

    # ── lifecycle ──────────────────────────────────────────────────────────────

    async def connect(self) -> None:
        self._connection = await aio_pika.connect_robust(self._url)
        self._channel = await self._connection.channel()
        await self._channel.declare_exchange(
            self.EXCHANGE_NAME, aio_pika.ExchangeType.TOPIC
        )
        self._logger.info("RabbitMQAdapter connected")

    async def disconnect(self) -> None:
        if self._connection:
            await self._connection.close()
            self._logger.info("RabbitMQAdapter disconnected")

    # ── publish ────────────────────────────────────────────────────────────────

    async def publish(self, topic: str, payload: str) -> None:
        if not self._channel:
            raise RuntimeError("RabbitMQAdapter is not connected")

        exchange = await self._channel.get_exchange(self.EXCHANGE_NAME)
        message = aio_pika.Message(
            body=payload.encode(),
            content_type="application/json",
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        )
        await exchange.publish(message, routing_key=topic)

    # ── consume ────────────────────────────────────────────────────────────────

    async def consume(self, queue_name: str, routing_key: str, callback) -> None:
        """Bind to `queue_name` and invoke `callback(payload: dict)` for each message."""
        if not self._channel:
            raise RuntimeError("RabbitMQAdapter is not connected")

        exchange = await self._channel.get_exchange(self.EXCHANGE_NAME)
        queue = await self._channel.declare_queue(queue_name, auto_delete=False)
        await queue.bind(exchange, routing_key=routing_key)

        self._logger.info("RabbitMQAdapter consuming queue=%s key=%s", queue_name, routing_key)

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    payload = json.loads(message.body.decode())
                    await callback(payload)
