import orjson
from pydantic import BaseModel

class KafkaSerializerMixin(BaseModel):
    """Mixin für Kafka-kompatible Serialisierung."""

    def to_kafka(self) -> bytes:
        """Serialisiert das Modell für Kafka."""
        return orjson.dumps(self.model_dump())

    def to_dict(self) -> dict:
        """Optional: normales Dict für interne Nutzung."""
        return self.model_dump()
