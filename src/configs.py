from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# class Settings(BaseSettings):
#     MONGO_URI: str
#     DB_NAME: str
#     SECRET_KEY: str
#     ALGORITHM: str
#
#     model_config = SettingsConfigDict(
#         env_file=".env",
#         extra="ignore"
#     )
#
# settings = Settings()

class Settings(BaseSettings):
    # MONGO DB
    MONGO_USER: str
    MONGO_PASS: str
    DB_NAME: str
    MONGO_HOST: str = "mongodb"
    MONGO_PORT: str = "27017"
    MONGO_URI: str = ""
    ADMIN_MAIL: str = "master@pls.edu.vn"
    ADMIN_PASS: str = "abc12345"

    # ROOT

    ROOT_PATH: str = ""
    ENABLE_DOCS: bool = True

    # redis
    # google token exp
    REFRESH_TOKEN_EXPIRE_SECOND: int = 3600
    # encrypt key


    # KEY
    SECRET_KEY: str
    ALGORITHM: str

    #FILE
    #REDIRECT

    model_config = SettingsConfigDict(
        env_file="../.env",
        extra="ignore"
    )

    @model_validator(mode='after')
    def build_mongo_uri(self):
        if self.MONGO_URI.startswith("mongodb+srv://"):
            raise ValueError(
                "MongoDB Atlas SRV URIs are disabled. Keep MONGO_URI empty and use the self-hosted MongoDB services."
            )

        if not self.MONGO_URI:
            self.MONGO_URI = (
                f"mongodb://{self.MONGO_USER}:{self.MONGO_PASS}@"
                f"{self.MONGO_HOST}:{self.MONGO_PORT}/{self.DB_NAME}?authSource=admin"
            )
        return self

settings = Settings()
