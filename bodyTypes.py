from pydantic import BaseModel
from fastapi import UploadFile
from datetime import date
from typing import Optional
class History(BaseModel):
    songID: str
    duration:str|int 

class User(BaseModel):
    userName: str
    email: str
class UserProfile(BaseModel):
    profile: bytes|None=None
    dob: date|None=None
    userName: str|None=None
    email: str|None=None
    userID: int
class Podcast(BaseModel):
    name: str
    duration: int
    userID: int
    image: bytes|None
    audio: bytes
    
    
class Playlist(BaseModel):
    
    name:str
    image_blob:bytes|None
    owner_id:int

class PlaylistTrack(BaseModel):
    userID: int
    playlistID: int
    trackID: int

class DeleteMedia(BaseModel):
    mediaType:str
    mediaID:int
    userID:int

class RecentTrack(BaseModel):
    songID:int
    userID:int

class OPlaylist(BaseModel):
    userID:int
    playlistID:int