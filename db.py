import mysql.connector as mc
from datetime import date
from bodyTypes import UserProfile 
class database:
    def __init__(self):
        self.conn={"user":"root",
                   "host":"127.0.0.1",
                   "password":"Silent_guardian@072003",
                   "database":"HPMS"
                   }
        self.cursor=None
        self.connObj=None
        
    def connect(self):
        print(self.conn)
        self.connObj=mc.connect(**self.conn)
        self.cursor=self.connObj.cursor(dictionary=True)

    

    def getSuggestion(self,Mtype:str,search:str):
        try:
            print(Mtype,search)
            self.cursor.callproc("SearchItemsByTypeAndName",[Mtype,search])
            result=[i.fetchall() for i in self.cursor.stored_results()][0]

            
           
            return result
        
        except Exception as e:
            print(e)
            return None
        
        
    
        # return({"result":[{"name":"song1"},{"name":"song2"},{"name":"song3"}]})

    def getSong(self,songID:int):
        try:
            self.cursor.callproc("RetrieveItemDetailsByID",["track",songID])
            
            result=[i.fetchall() for i in self.cursor.stored_results()]

            if len(result[0])>0:
                return result[0][0]
            else:
                print("Item not found")
                return "error"
        except mc.Error as e:
            print(e)
            return "error"

    def updatePopularTrack(self,songID:int):
        self.cursor.execute("")

        # return{"name":"song1","artist":"artist1","duration":1}
    
    def addPlaylist(self,name:str,userID:str,imageBlob:str|None=None):
        
        try:
            doc=date.today().strftime("%Y-%m-%d")
            
            self.cursor.execute("INSERT INTO playlist (name, owner_id, doc, image_blob) VALUES (%s, %s, %s, %s);",(name,userID,doc,imageBlob))
            self.connObj.commit()
            return "ok"
        except mc.Error as e:
            print(e)
            return "error"
        
        
    
    def getUserPlaylist(self,userID:int):
        try:
            self.cursor.execute("SELECT * FROM playlist WHERE playlist.owner_id = %s;",(userID,))
            result=self.cursor.fetchall()
            return result
        except mc.Error as e:
            print(e)
            return "error"
        

        # return({"result":[{"name":"song1"},{"name":"song2"},{"name":"song3"}]})
    
    def getRecentlyPlayed(self,userID:int):
        try:
            self.cursor.execute("""
select track.name,recently_played.order,track.duration,artist_name,recently_played.track_id,track.image_blob
from
composed join recently_played on composed.track_id=recently_played.track_id
join track on recently_played.track_id=track.track_id
join artist on artist.artist_id=composed.artist_id
where recently_played.user_id=%s;

""",(userID,))
            result=self.cursor.fetchall()
            return result
        except mc.Error as e:
            print(e)
            return "Error"
        # return({"result":[{"name":"song1"},{"name":"song2"},{"name":"song3"}]})

    
        
    def insertNewUser(self,userName:str,userEmail:str):
        try:
            
            self.cursor.execute("INSERT IGNORE INTO User (username, email) VALUES (%s, %s);",(userName,userEmail))
            self.connObj.commit()
            self.cursor.execute("SELECT id from User where username=%s and email=%s",(userName,userEmail))
            result=self.cursor.fetchall()

            
            if len(result)>0:
                return result[0]
            else:
                return result
            


            
        except mc.Error as e:
            print(e)
            return "error"
        
    def getUserDetails(self,userID:int):
        try:
            self.cursor.execute("SELECT * FROM User WHERE id = %s;",(userID,))
            result=self.cursor.fetchall()
            if len(result)>0:

                return result
            else:
                return "error"
        except mc.Error as e:
            print(e)
            return "error"
        
    # def updateUserDetails(self,userID:int,userName:str|None,dob:date|None,email:str|None,profile:bytearray|None):
    #     try:
    #         self.cursor.execute("UPDATE TABLE SET user")
        
        
    def insertPlaylistSong(self,userID:int,playlistID:int,trackID:int):
        try:
            self.cursor.execute("INSERT INTO playlist_songs (playlist_id, track_id) VALUES (%s,%s);",(playlistID,trackID))
            self.connObj.commit()
            return "ok"
        except mc.Error as e:
            print(e)
            return "error"
        
    
    def deletePlaylistSong(self,playlistID:int,trackID:int):
        try:
            result=self.cursor.execute("DELETE FROM playlist_songs WHERE track_id=%s and playlist_id=%s;",(trackID,playlistID))
            self.connObj.commit()
            return result
        except mc.Error as e:
            print(e)
            return None
        

    def insertPodcast(self,name:str,duration:int,userID:int,audioBlob:bytes,doc:str=date.today().strftime('%Y-%m-%d'),imageBlob:bytes=None):
        try:
            self.cursor.execute("INSERT INTO podcast (name, doc, duration, user_id, audio_blob,image_blob)VALUES (%s,%s,%s,%s,%s,%s);",(name,doc,duration,userID,audioBlob,imageBlob))
            self.connObj.commit()
            return "ok"
        except mc.Error as e:
            print(e)
            return "error"
        
    def deletePlaylist(self,playlistID:int):
        try:
            self.cursor.execute("delete from playlist where playlist_id=%s",(playlistID,))
            self.connObj.commit()
            return "ok"
        except mc.Error as e:
            print(e)
            return "error"

    def deletPodcast(self,podcastID:int):
        try:
                self.cursor.execute("delete from podcast where podcast_id=%s",(podcastID,))
                self.connObj.commit()
                return "ok"
        except mc.Error as e:
            print(e)
            return "error"
        
    def getUserPodcast(self,userID:int):
        try:
            self.cursor.execute("select podcast_id,name,doc,duration,user_id,image_blob from podcast where user_id=%s",(userID,))
            result=self.cursor.fetchall()
            
            return result
        except mc.Error as e:
            print(e)
            return "error"
        
    # def deleteSong(self,track_id:int):
    #     try:
    #         self.cursor.execute("delete from track where track_id=%s on delete cascade",(track_id))
    #     except mc.Error as e:
    #         print(e)
    #         return "error"
    

    def insertRecentlyPlayed(self,songID:int,userID:int):
        try:
            self.cursor.callproc("UpdateRecentlyPlayed",[userID,songID])
            self.connObj.commit()
            return "ok"
        except mc.Error as e:
            print(e)
            return "error"

    def getFollowedPlaylist(self,userID):
        try:
            self.cursor.execute("""select playlist.playlist_id,playlist.name,playlist.image_blob,playlist.doc,User.username from  playlist join user_playlist on user_playlist.playlist_id=playlist.playlist_id
join User on User.id=playlist.owner_id where user_playlist.user_id=%s""",(userID,))
            result=self.cursor.fetchall()
            return result
        except mc.Error as e:
            print(e)
            return "error"

    def folowPlaylist(self,playlistID,userID):
        try:
            self.cursor.execute("insert into user_playlist value(%s,%s)",(playlistID,userID))
            self.connObj.commit()
            return "ok"
        except mc.Error as e:
            print(e)
            return "error"

    def unfollowPlaylist(self,userID,playlistID):
        try:
            self.cursor.execute("DELETE FROM user_playlist WHERE playlist_id=%s AND user_id=%s",(playlistID,userID))
            self.connObj.commit()
            return "ok"
        except mc.Error as e:
            print(e)
            return "error"
        
    def getPlaylistInfo(self,playlistID):
        try:
            self.cursor.execute("""
select track.track_id, track.name, track.duration,artist.artist_name, track.image_url, track.image_blob from track 
join playlist_songs on playlist_songs.track_id=track.track_id
join playlist on playlist.playlist_id=playlist_songs.playlist_id
join User on playlist.owner_id=User.id
join composed on track.track_id=composed.track_id
join artist on artist.artist_id=composed.artist_id
where playlist_songs.playlist_id=%s;

""",(playlistID,))
            result=self.cursor.fetchall()
            return result
        except mc.Error as e:
            print(e)
            return "error"
        
    def getPodcast(self,podcastID:int):
        try:
            self.cursor.execute("select audio_blob from podcast where podcast_id=%s;",(podcastID,))
            result=self.cursor.fetchall()[0]
            return result
        except mc.Error as e:
            print(e)
            return "error"
    def getAlbumSongs(self,albumID:int):
        try:
            self.cursor.execute("""

select track.name, track.track_id, album.album_name,artist.artist_name,track.image_blob
from track 
join album_songs on track.track_id=album_songs.track_id
join album on album_songs.album_id =album.album_id
join composed on composed.track_id=track.track_id
join artist on artist.artist_id=composed.artist_id
where album.album_id=%s;
""",(albumID,))
            result=self.cursor.fetchall()
            
            return result
        except mc.Error as e:
            print(e)
            return "error"
    
    def getAllPlaylists(self,userID:int):
        followed=self.getFollowedPlaylist(userID)
        userPlaylist=self.getUserPlaylist(userID)

        if followed!="error" and userPlaylist!="error":
            return({"followed":followed,"userPlaylist":userPlaylist})
        
        return "error"
    
    def editUserDetails(self,userDetails:UserProfile):
        try:

            self.cursor.execute(
                """UPDATE User 
SET username=%s, email=%s, dob=%s, profile_image=%s 
WHERE id=%s;""",(userDetails.userName, userDetails.email, userDetails.dob, userDetails.profile, userDetails.userID)

            )

            
            result=self.cursor.fetchall()
            
            self.connObj.commit()
            return "ok"
        except mc.Error as e:
            print(e)
            return "error"


    def getTopTracks(self):
        try:
            self.cursor.execute("""SELECT track.name,track.image_blob,track.track_id,artist.artist_name,popular_tracks.stream_count FROM popular_tracks
                                join track on track.track_id=popular_tracks.track_id
                                join composed on composed.track_id=popular_tracks.track_id
                                join artist on artist.artist_id=composed.artist_id LIMIT 10;""")
            result=self.cursor.fetchall()
            
            return result
        except mc.Error as e:
            print(e)
            return "error"


    def setStreamEvent(self,track_id:int):
        try:
            self.cursor.execute("INSERT INTO track_stream_event(track_id) VALUE (%s);",(track_id,))
            self.connObj.commit()
            return "ok"
        except mc.Error as e:
            print(e)
            return "error"  

    def close(self):
        self.connObj.close()

    


