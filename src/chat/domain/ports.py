from abc import ABC, abstractmethod

class IMessageBroker(ABC):
    """Interface to implement. Port for publishing and consuming messages via a message broker."""

    @abstractmethod
    async def connect(self) -> None:
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        pass

    @abstractmethod
    async def publish(self, topic: str, payload: str) -> None:
        pass

    @abstractmethod
    async def consume(self, queue_name: str, routing_key: str, callback) -> None:
        """Start consuming from a queue, invoking `callback(payload: dict)` per message."""
        pass


class ISocketGateway(ABC):
    """Interface to implement. Port for delivering real-time notifications to connected clients."""

    @abstractmethod
    async def send_to_user(self, user_id: str, event: str, payload: dict) -> None:
        pass
