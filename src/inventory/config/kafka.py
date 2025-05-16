from pydantic_settings import BaseSettings

from inventory.config import env


class KafkaSettings(BaseSettings):
    bootstrap_servers: str = "localhost:9092"
    topic_log: str = "logstream.log.inventory"
    client_id: str = env.PROJECT_NAME

    class Config:
        env_prefix = "KAFKA_"


def get_kafka_settings() -> KafkaSettings:
    return KafkaSettings()
