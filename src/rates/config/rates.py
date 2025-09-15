from pydantic_settings import BaseSettings


class RatesConfig(BaseSettings):
    fetcher_base_url: str


rates_config = RatesConfig()
