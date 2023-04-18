from pydantic import BaseModel


class Message(BaseModel):
    chat_id: str
    timestamp: int
    sender_id: str
    body: str
    gossip_id: str

    class Config:
        frozen = True
