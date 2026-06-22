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
# from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from contextlib import asynccontextmanager
from fastapi import FastAPI


from src.configs import settings

from src.models.user.user_document import UserDocument
from src.models.group.group_document import GroupDocument
from src.models.file.file_document import FileDocument
from src.models.document_item.document_item_document import DocumentItem
from src.models.document_result.document_result_document import DocumentResult
from pymongo import AsyncMongoClient
from src.models.work_item.work_item_document import WorkItemDocument
from src.models.session.session_document import SessionDocument
from src.models.order.order_document import OrderDocument
from src.models.session.session_view import DailySessionView
from src.models.chatbot_token.chatbot_token_document import ChatbotTokenDocument

WorkItemDocument.model_rebuild()
SessionDocument.model_rebuild()
DailySessionView.model_rebuild()



client = AsyncMongoClient(settings.MONGO_URI)
db = client[settings.DB_NAME]

async def init_db():
    try:
        await client.admin.command('ping')
        await init_beanie(
            database=cast(Any, db),
            document_models=[UserDocument, GroupDocument, WorkItemDocument
                , FileDocument, DocumentItem, DocumentResult, SessionDocument,
                             ChatbotTokenDocument, OrderDocument, DailySessionView
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

