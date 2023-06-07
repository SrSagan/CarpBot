import json
import os
import data

SERVERPATH="./servers/"
SAVEDPLAYLIST="./savedplaylists/"
servers=[]
servers_id=[]

a = data.datos()

class serverManager():
    def __init__(self):
        self.get_servers()
    
#-----------------------GET SERVERS------------------------#
    def get_servers(self):
        global servers
        global servers_id

        if(os.path.exists(SERVERPATH) == False): #check for file existance and folder
            os.makedirs(SERVERPATH)
            with open(SERVERPATH+"servers.json", "w") as f:
                json.dump(servers, f) #create it
 
        with open(SERVERPATH+"servers.json", "r") as f: 
            servers = json.load(f) #read the file
            f.close() 
        for server in servers:
            servers_id.append(server["id"])
        
        if(os.path.exists(SAVEDPLAYLIST) == False): #check for file existance and folder
            os.makedirs(SAVEDPLAYLIST)

#-----------------------APPLY------------------------#
    def apply(self):
        global servers #save to file
        with open(SERVERPATH+"servers.json", "w") as f:
            json.dump(servers, f, indent=4)

#-----------------------CLEAR SERVER------------------------#
    def clear(self, id):
        #clear a server from servers
        id = int(id)
        global servers
        global servers_id

        for server in servers_id: 
            if(id == server):
                servers.pop(servers_id.index(server))
                servers_id.pop(servers_id.index(server)) #index should be the same in both
                self.apply()

#-----------------------GET INDEX------------------------#
    def get_index(self, id):
        #get server index from id
        id = int(id)
        global servers
        global servers_id

        for server in servers:
            if(server["id"] == id):
                return servers.index(server)

#-----------------------EXISTS------------------------#
    def exists(self, id):
        #check if server exists
        id = int(id)
        global servers_id
        
        if(id in servers_id):
            return True
        else:
            return False

#-----------------------SAVE PLAYLIST------------------------#
    def save_playlist(self, id, userid, name):
        id = int(id)
        global servers_id
        global servers

        index = self.get_index(id)

        playlist = {
            "name": name,
            "songs":servers[index]["songs"]
        }

        if(os.path.exists(SAVEDPLAYLIST+str(userid)+".json")): #si el archivo ya existe
            with open(SAVEDPLAYLIST+str(userid)+".json", "r") as f:
                saved = json.load(f) #read it
            if(len(saved) >= 5):
                return 0 #return something when it reached the limit
            else:
                for queue in saved: #return something if playlist alr exists
                    if(queue["name"] == name):
                        return 2
                saved.append(playlist) 
                with open(SAVEDPLAYLIST+str(userid)+".json", "w") as f: #append the song
                    json.dump(saved, f, indent=4) #create it
                return 1
        else: #if it doesn't exist
            with open(SAVEDPLAYLIST+str(userid)+".json", "w") as f:
                json.dump([playlist], f, indent=4) #create it
            return 1

#-----------------------LOAD PLAYLIST------------------------#
    def load_playlist(self, id, userid, name):
        id = int(id)
        global servers_id
        global servers

        if(os.path.exists(SAVEDPLAYLIST+str(userid)+".json")): #si el archivo ya existe
            with open(SAVEDPLAYLIST+str(userid)+".json", "r") as f:
                saved = json.load(f) #read it

                for playlist in saved:
                    if(playlist["name"] == name):
                        if(self.exists(id)):
                            servers[self.get_index(id)]["songs"]+=playlist["songs"]
                            return 1
                        else:
                            return playlist["songs"]
        self.apply()
        return 0

#-----------------------SHOW PLAYLIST------------------------#
    def show_playlist(self, userid):
        global servers
        global servers_id

        if(os.path.exists(SAVEDPLAYLIST+str(userid)+".json")): #si el archivo ya existe
            with open(SAVEDPLAYLIST+str(userid)+".json", "r") as f:
                saved = json.load(f) #read it
        else:
            return 0
        
        return saved

#-----------------------REMOVE PLAYLIST------------------------#
    def remove_playlist(self, userid, name):

        playlists = self.show_playlist(userid)

        for playlist in playlists:
            if(name == playlist["name"]):
                playlists.pop(playlists.index(playlist))
                with open(SAVEDPLAYLIST+str(userid)+".json", "w") as f: #append the song
                    json.dump(playlists, f, indent=4) #create it
                return 1

        return 0
        
