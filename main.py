from fastapi import FastAPI,File,UploadFile,HTTPException,status

from pydantic import BaseModel
from typing import List, Annotated,IO
from datetime import date
from fastapi.middleware.cors import CORSMiddleware

import redis
from db import database
import base64
import gzip
import logging


# Specify the file path where you want to save the logs
log_file_path = "app.log"


# Configure the logging
logging.basicConfig(filename=log_file_path, level=logging.DEBUG)


db=database()
# r=redis.Redis(host="localhost",port=6379,decode_responses=True)
from bodyTypes import User,UserProfile,History, Podcast, Playlist, PlaylistTrack, RecentTrack,DeleteMedia,OPlaylist




def validateFile(file:IO):
    FILE_SIZE = 4*1024*1024 

    if file.content_type not in ["image/png", "image/jpeg", "image/jpg","audio/mp3","audio/wav"]:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Unsupported file type",
        )

    real_file_size = 0
    for chunk in file.file:
        real_file_size += len(chunk)
        if real_file_size > FILE_SIZE:
            raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Too large")
    return "ok"
app=FastAPI()
origins=["*"]
app.add_middleware(CORSMiddleware,   
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],)
total=0
db.connect()
@app.get("/")
async def root():
    global total
    total+=1
    print(total)
    return {"result":"I am root"}

@app.get("/getSuggestions")
async def getSuggestions(Mtype:str,search:str):
    """
        return {"result":[{},{},{},{},{}]}
    """
    
    print(type(Mtype),type(search))
    result=db.getSuggestion(Mtype,search)
    
        
    for i in result:
        
        if "image_blob" in i.keys():
            if Mtype =="track":
                i["image_blob"]=base64.b64encode(i["image_blob"]).decode('utf-8')

        else:
            i["image_blob"]=None
        
        # i[-2]=base64.b64encode(i[-2]).decode('utf-8')
        # i[-2]=""

    return {"result":result}
    
@app.post("/addPlaylistTrack")
async def addPlaylisrSong(track:PlaylistTrack):
    print(track)
    result=db.insertPlaylistSong(track.userID,track.playlistID,track.trackID)
    return {"result":result}




# @app.get("/getSongRecommendation")
# async def getSongRecommendation(userID:str):
#     """
#         calculate and store user recommendation and serve it when requested
#     """

#     pass

# @app.get("/getPlaylistRecommendation")
# async def getPlaylistRecommendation(userID:str):
#     """
#         calculate and store user playlist recommendation and serve it when requested
#     """
#     pass


@app.post("/uploadPodcast")
async def uploadPodcast(user_podcast:Podcast):
   
        
        result=db.insertPodcast(name=user_podcast.name,duration=user_podcast.duration,userID=user_podcast.userID,audioBlob=user_podcast.audio,imageBlob=user_podcast.image)
        
        return {"result": result}


# change this to streaming
@app.get("/getSong")
async def getSong(songID:int):
    result=db.getSong(songID)
    setStreamEvent=db.setStreamEvent(songID)

    print(setStreamEvent)
    if result!="error":
        # print(result.keys())
        result["audio_blob"]=base64.b64encode(result["audio_blob"]).decode('utf-8')
    
    
    
    return({"result":result})
    # return {}

@app.post("/addUser")
async def addUser(User:User):

    result=db.insertNewUser(User.userName,User.email)
    
    return {"result":result}
    
    

@app.get("/userDetails")
async def getUserDetails(userID:int):
    result=db.getUserDetails(userID)
    return {"result":result}

# @app.post("/updateUserDetails")
# async def updateUserDetails(userProfile:UserProfile):
#     result=db.

@app.post("/addPlaylist")
async def addPlaylist(playlist:Playlist):
    result=db.addPlaylist(playlist.name,playlist.owner_id,playlist.image_blob)
    return {"result":result}

@app.get("/getUserPlaylist")
async def getPlaylist(userID:int):
    result=db.getUserPlaylist(userID)
    return {"result":result}

@app.get("/getRecentlyPlayed")
async def getPlaylist(userID:int):
    result=db.getRecentlyPlayed(userID)

    

    for i in result:
        print(i.keys())
        i["image_blob"]=base64.b64encode(i["image_blob"]).decode('utf-8')


    return {"result":result}

@app.post("/setRecentlyPlayed")
async def updateHistory(track:RecentTrack):
    result=db.insertRecentlyPlayed(track.songID,track.userID)
    return {"result":result}
    

@app.get("/getUserPodcast")
async def getUserPodcast(userID:int):
    result=db.getUserPodcast(userID)
    # if result!="error":
    #     for i in result:
    #         if i["image_blob"]:
    #             i["image_blob"]=base64.b64encode(i["image_blob"]).decode('utf-8')
            
    return {"result":result}

@app.post("/deleteUserMedia")
async def deleteUserMedia(media:DeleteMedia):
    print(media)
    if media.mediaType=="playlist":
        result=db.deletePlaylist(media.mediaID)
        return {"result":result}
    elif media.mediaType=="podcast":
        result=db.deletPodcast(media.mediaID)
        return {"result":result}

@app.post("/deletePlaylistSong")
async def deletePlaylistSong(playlist:PlaylistTrack):
    result=db.deletePlaylistSong(playlist.playlistID,playlist.trackID)
    return result



@app.get("/getFollowedPlaylists")
async def getAllPlaylist(userID:int):
    result=db.getFollowedPlaylist(userID)
    if result!="error":
        for i in result:
            i["image_blob"]=base64.b64encode(i["image_blob"]).decode('utf-8')


    
    return{"result":result}

@app.post("/followPlaylist")
async def followPlaylist(playlist:OPlaylist):
    result=db.folowPlaylist(playlist.playlistID,playlist.userID)
    return {"result":result}

@app.post("/unfollowPlaylist")
async def unfollowPlaylist(playlist:OPlaylist):
    result=db.unfollowPlaylist(playlist.userID,playlist.playlistID)
    return {"result":result}

@app.get("/playlistInfo")
async def getPlaylistInfo(playlistID:int):
    result=db.getPlaylistInfo(playlistID)
    for i in result:
        print(i.keys())
        i["image_blob"]=base64.b64encode(i["image_blob"]).decode('utf-8')

    return {"result":result}

@app.post("/deletePlaylistSong")
async def deletePlaylistTrack(playlistID:int,trackID:int):
    result=db.deletePlaylistSong(playlistID,trackID)
    return result

@app.get("/getPodcast")
async def getPodcast(podcastID:int):
    result=db.getPodcast(podcastID)
   
    return result

@app.get("/getAlbumTracks")
async def getAlbumTracks(albumID:int):
    result=db.getAlbumSongs(albumID)
    for i in result:
        i["image_blob"]=base64.b64encode(i["image_blob"]).decode('utf-8')
    return {"result":result}


@app.get("/getAllPlaylists")
async def getAllPlaylists(userID:int):
    result=db.getAllPlaylists(userID)
    return {"result":result}

@app.post("/updateUserDeatils")
async def updateUserDetails(userDetails:UserProfile):
    result=db.editUserDetails(userDetails)
    return {"result":result}

@app.get("/getTopTracks")
async def getTopTracks():
    result=db.getTopTracks()
    if result!="error":
        for i in result:
            i["image_blob"]=base64.b64encode(i["image_blob"]).decode("utf8")
    return {"result":result}