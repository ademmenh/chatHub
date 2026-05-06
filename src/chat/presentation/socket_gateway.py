import logging
from typing import Dict
import socketio
from ..domain.ports import ISocketGateway

class SocketGateway(ISocketGateway):
    """Presentation adapter that delivers notifications via Socket.IO."""

    def __init__(self, sio: socketio.AsyncServer, logger: logging.Logger) -> None:
        self._sio = sio
        self._logger = logger
        self._connected_users: Dict[str, str] = {}
        self._register_events()

    # ── event handlers ─────────────────────────────────────────────────────────

    def _register_events(self) -> None:
        @self._sio.event
        async def connect(sid, environ, auth):
            query_string = environ.get("QUERY_STRING", "")
            user_id = None
            for param in query_string.split("&"):
                if param.startswith("user_id="):
                    user_id = param.split("=")[1]
                    break

            if user_id:
                self._connected_users[user_id] = sid
                self._sio.enter_room(sid, str(user_id))
                self._logger.info("User %s connected (sid=%s)", user_id, sid)
            else:
                self._logger.warning("Connection %s has no user_id, disconnecting", sid)
                await self._sio.disconnect(sid)

        @self._sio.event
        async def disconnect(sid):
            user_id = next(
                (uid for uid, s in self._connected_users.items() if s == sid), None
            )
            if user_id:
                del self._connected_users[user_id]
                self._logger.info("User %s disconnected", user_id)

    # ── ISocketGateway ─────────────────────────────────────────────────────────

    async def send_to_user(self, user_id: str, event: str, payload: dict) -> None:
        await self._sio.emit(event, payload, room=str(user_id))
