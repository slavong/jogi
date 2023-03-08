from typing import Optional

from pydantic import BaseModel
from pydantic_settings_yaml import YamlBaseSettings


class Log(BaseModel):
    level: str


class Settings(YamlBaseSettings):
    version: Optional[str]
    log: Log

    class Config:
        case_sensitive = True
        yaml_file = "./config.yaml"


_config = Settings()


def get_config() -> Settings:
    return _config
