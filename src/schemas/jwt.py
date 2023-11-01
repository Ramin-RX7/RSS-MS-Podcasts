from pydantic import BaseModel


class JWTPayload(BaseModel):
    email : str
    payload : dict

    class Config:
        extra = "ignore"
