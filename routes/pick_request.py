from pydantic import BaseModel


class PickRequest(BaseModel):

    player_id: int