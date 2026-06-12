from beanie import DocumentWithSoftDelete

class ChatbotTokenDocument(DocumentWithSoftDelete):
    type: str
    token: str
    position: str
    space_id: str
    key: str

    class Settings:
        name='chatbot_token'