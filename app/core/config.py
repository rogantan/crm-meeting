from pydantic_settings import BaseSettings

class Settings(BaseSettings):
  
  POSTGRES_HOST: str
  POSTGRES_PORT: int
  POSTGRES_USER: str
  POSTGRES_PASSWORD: str
  POSTGRES_DB: str

