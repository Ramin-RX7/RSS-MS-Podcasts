from datetime import datetime

from bson import ObjectId
from pydantic import BaseModel,Field, field_serializer, field_validator

from .base import *
from .jwt import *





USER_ID = int
PODCAST_ID = int
EPISODE_ID = int




class MongoScheme(BaseModel):
    id : ObjectId|None = Field(alias="_id")
    class Config:
        arbitrary_types_allowed=True

    @field_serializer('id')
    def id_serializer(self, id, _info):
        return str(id)

    @field_validator("id", mode="before")
    def id_validator(cls, v):
        if type(v) is str:
            return ObjectId(v)
        return v


class CommentStruct(BaseModel):
    user : ObjectId
    date : datetime
    content : str
    class Config:
        arbitrary_types_allowed=True

    @field_serializer('user')
    def id_serializer(self, id, _info):
        return str(id)

    @field_validator("user")
    def id_validator(cls, v):
        if type(v) is str:
            return ObjectId(v)
        return v


class UserSubsStruct(BaseModel):
    podcast : ObjectId
    notification : bool
    class Config:
        arbitrary_types_allowed=True

    @field_serializer('podcast')
    def id_serializer(self, id, _info):
        return str(id)

    @field_validator("podcast")
    def id_validator(cls, v):
        if type(v) is str:
            return ObjectId(v)
        return v

class PodcastSubsStruct(BaseModel):
    user : ObjectId
    notification : bool = False
    class Config:
        arbitrary_types_allowed=True

    @field_serializer('user')
    def id_serializer(self, id, _info):
        return str(id)

    @field_validator("user")
    def id_validator(cls, v):
        if type(v) is str:
            return ObjectId(v)
        return v



class Episode(BaseModel):
    api_identifier : EPISODE_ID
    likes : list[ObjectId] = []
    comments : list[CommentStruct] = []
    id : ObjectId|None = Field(default_factory=ObjectId)

    class Config:
        arbitrary_types_allowed=True

    @field_serializer('id')
    def id_serializer(self, id, _info):
        return str(id)

    @field_validator("id", mode="before")
    def id_validator(cls, v):
        if type(v) is str:
            return ObjectId(v)
        return v

    @field_serializer('likes')
    def likes_serializer(self, likes, _info):
        return list(map(lambda item:str(item), likes))



class Podcast(MongoScheme):
    api_identifier : PODCAST_ID
    subscribers : list[PodcastSubsStruct] = []
    episodes : list[Episode] = []



class UserLikeStruct(BaseModel):
    podcast_identifier : ObjectId
    episode_identifier : str

    class Config:
        arbitrary_types_allowed=True



class User(MongoScheme):
    api_identifier : USER_ID
    liked_episodes : list[UserLikeStruct] = []
    subscriptions : list[UserSubsStruct] = []

    @field_serializer('liked_episodes')
    def id_serializer(self, likes, _info):
        return list(map(lambda item:str(item), likes))
