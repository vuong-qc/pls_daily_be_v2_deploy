from beanie import Document

class TagResultDocument(Document):
    tag_id: str
    object_id: str
    status: int

    class Settings:
        name = "tag_results"