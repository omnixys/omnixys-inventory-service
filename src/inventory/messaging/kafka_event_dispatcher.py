from typing import Callable, Awaitable, Any


class KafkaEventDispatcher:
    def __init__(self):
        self._handlers: dict[str, Callable[[dict, dict], Awaitable[Any]]] = {}

    def register(self, topic: str, handler: Callable[[dict, dict], Awaitable[Any]]):
        self._handlers[topic] = handler

    def get_handler(self, topic: str) -> Callable[[dict, dict], Awaitable[Any]] | None:
        return self._handlers.get(topic)
