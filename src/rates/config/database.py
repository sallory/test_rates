from pydantic_settings import BaseSettings


class DBConfig(BaseSettings):
    database_url: str


db_config = DBConfig()
