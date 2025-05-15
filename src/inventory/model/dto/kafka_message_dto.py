import orjson
from pydantic import BaseModel


class KafkaMessageDTO(BaseModel):
    """Basisklasse für alle Kafka-DTOs."""

    def serialize(self) -> bytes:
        return orjson.dumps(self.model_dump())
