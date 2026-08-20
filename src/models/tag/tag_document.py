from beanie import Document

class TagDocument(Document):
    title: str
    des: str
    color: str
    status: int
    created_at: int
    updated_at: int
    group_id: str| None = None
    firebase_tag_id: str| None = None

    class Settings:
        name="tags"
