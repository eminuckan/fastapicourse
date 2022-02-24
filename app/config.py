from pydantic import BaseSettings


class Settings(BaseSettings):
    database_hostname: str
    database_port: str  # aslında bu değer int olmalı geçerli bir port olup olmadığını şimdilik kontrol etmediğimiz str diyip geçiyoruz
    database_username: str
    database_password: str
    database_name: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    # Değerlerin küçük harfle yazılması önemli değil pydantic doğrulama yaparken lowercase yapıyor iki değeri.

    class Config:
        env_file = ".env"


# Normalde pydantic bu değerleri makinenin environment variables değerlerinden alır. Production kısmında bu değerleri makineye ekleyip oradan env. var.
# yönetimi yaparız. Ama DEV ortamında kolaylık olması açısından .env adlı bir dosyadan bu değerleri alıyoruz.

settings = Settings()
