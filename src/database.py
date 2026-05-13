# from motor.motor_asyncio import AsyncIOMotorClient
# from src.configs import settings
#
# client = AsyncIOMotorClient(settings.MONGO_URI)
# db = client[settings.DB_NAME]
#
# async def test_db_connection():
#     try:
#         await client.admin.command('ping')
#         print("✅ Đã kết nối MongoDB thành công!")
#     except Exception as e:
#         print(f"❌ Lỗi kết nối MongoDB: {e}")

from typing import Any, cast
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from contextlib import asynccontextmanager
from fastapi import FastAPI


from src.configs import settings

from src.documents.user_document import UserDocument

from pymongo import AsyncMongoClient



client = AsyncMongoClient(settings.MONGO_URI)
db = client[settings.DB_NAME]

async def init_db():
    try:
        await client.admin.command('ping')
        await init_beanie(
            database=cast(Any, db),
            document_models=[UserDocument,
                             ]
        )
        print("MongoDB & Beanie initialized!")
    except Exception as e:
        print(f"DB Init Error: {e}")
        raise e


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    client.close()
    print("MongoDB connection closed.")

