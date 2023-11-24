import pandas as pd
import mysql.connector
import os
import requests
import signal
import datetime
import sys
import traceback
proxy={'http':  'socks5://127.0.0.1:9050',
                       'https': 'socks5://127.0.0.1:9050'}


# Define your MySQL database connection parameters
db_config = {

}
csv_file = 'tracks.csv'

def convert_file_to_blob(title,url,file_path):
    if not os.path.exists(file_path+"/"+title+"."+url[-3::]):
    
        try:
            r=requests.get(url,proxies=proxy)
        except Exception as err:
            print(err)
            print("Unable to download ",url)
            with open("error","w") as f:
                f.write(title)
                sys.exit()
        data=r.content
        try:
            if not os.path.exists(file_path):
                os.mkdir(file_path)
            with open(file_path+"/"+title+"."+url[-3::], 'wb') as file:
                file.write(data)
            return data
        except Exception as e:
            print(f"Error converting file to BLOB: {str(e)}")
            with open("error","w") as f:
                f.write(title)
                sys.exit()
    
    else:
          with open(file_path+"/"+title+"."+url[-3::], 'rb') as file:
                return file.read()
        

connection = mysql.connector.connect(**db_config)
cursor = connection.cursor()

df = pd.read_csv(csv_file)
skip=False

if os.path.exists("error") :
                skip=True
                a=open("error","r").read().strip()
elif os.path.exists("last"):
     skip=True
     a=open("last","r").read().strip()
     print(a)
for index, row in df.iterrows():

    try:
                
            if skip:
                    
                    if row["Title"].strip()!=a:
                        print(row["Title"])
                        
                        continue
                    else:
                        print("Found")
                        skip=False
                        if os.path.exists("error"):
                                os.remove("error")
                        if os.path.exists("last"):
                                os.remove("last")
                        continue
                        
                        
            print(row["Title"])
            audio_blob = convert_file_to_blob(row["Title"],row["MusicUrl"],"/".join(row['LocalMusicUrl'].split("/")[0:3]))
            image_blob = convert_file_to_blob(row["Title"],row["ImageUrl"],"/".join(row['LocalImageUrl'].split("/")[0:3]))
            
            author_list = row['Artist']
            if isinstance(author_list, str):
                try:
                    author_list = eval(author_list)
                    
                    author=author_list[0]
                    print(author)
                except Exception as e:
                    print(f"Error converting 'Artist' to list: {str(e)}")
                    author = author_list.split(",")[0][1:]
                    print(author)
                    

            

            cursor.execute("SELECT artist_id FROM artist WHERE artist_name = %s", (author,))
            existing_artist = cursor.fetchone()

            if existing_artist:
                artist_id = existing_artist[0]
            else:
                cursor.execute("INSERT INTO artist (artist_name) VALUES (%s)", (row['Artist'],))
                artist_id = cursor.lastrowid


            cursor.execute("SELECT album_id FROM album WHERE album_name = %s",(row['Album'],))

            existing_album = cursor.fetchone()

            if existing_album:
                album_id = existing_album[0]
            else:
                cursor.execute("INSERT INTO album (artist_id,doc,album_name) VALUES (%s,%s,%s)",(artist_id,datetime.date.today(),row['Album']))
                album_id = cursor.lastrowid


            
            cursor.execute("INSERT INTO track (name, duration, audio_url,image_url,image_blob,audio_blob) VALUES (%s,%s,%s,%s,%s,%s)",(row['Title'], int(row['Duration']), row['MusicUrl'],row['ImageUrl'],image_blob,audio_blob))
            track_id = cursor.lastrowid

            cursor.execute("INSERT INTO composed (track_id,artist_id) VALUES (%s,%s)",(track_id,artist_id))
            cursor.execute("INSERT INTO album_songs (track_id,album_id) VALUES (%s,%s)",(track_id,album_id))
            connection.commit()

            with open("last","w") as l:
                 l.write(row["Title"])
                 
    except Exception as e:
         print(e)
         with open("error","w") as f:
                f.write(row["Title"])
                
                sys.exit()
         



cursor.close()
connection.close()




