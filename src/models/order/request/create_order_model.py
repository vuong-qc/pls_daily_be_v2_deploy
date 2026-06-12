from pydantic import BaseModel

class CreateOrderModel(BaseModel):
    type: str
    object_id: str
    owner_id: str