from abc import ABC, abstractmethod
from typing import Callable


class IMessageBusChannel(ABC):
    @abstractmethod
    def queue_declare(self, name: str, durable: bool = True) -> None:
        ...

    @abstractmethod
    def publish_message(self, routing_key: str, message_body: bytes) -> None:
        ...

    @abstractmethod
    def consume_messages(self, queue_name: str, callback: Callable[[bytes], None]) -> None:
        ...

    @abstractmethod
    def start_consuming(self) -> None:
        ...


class IMessageBusConnection(ABC):
    @abstractmethod
    def get_channel(self) -> IMessageBusChannel:
        ...