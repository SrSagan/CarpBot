import json
import os
import data
# import server as sv

SAVEDPLAYLIST = "./savedplaylists/"
servers = []
servers_id = []

a = data.datos()


class serverManager:
    def __init__(self):
        self

    def get_server(self, id):
        index = self.get_index(id)
        global servers
        return servers[index]

    # -----------------------CLEAR SERVER------------------------#
    def clear(self, id):
        # clear a server from servers
        id = int(id)
        global servers
        global servers_id

        for server in servers_id:
            if id == server:
                servers.pop(servers_id.index(server))
                servers_id.pop(
                    servers_id.index(server)
                )  # index should be the same in both

    # -----------------------GET INDEX------------------------#
    def get_index(self, id):
        # get server index from id
        id = int(id)
        global servers
        global servers_id
        for server in servers:
            print(server.id)
            print(id)
            if server.id == id:
                return servers.index(server)

    # -----------------------EXISTS------------------------#
    def exists(self, id):
        # check if server exists
        id = int(id)
        global servers_id

        if id in servers_id:
            return True
        else:
            return False

    # -----------------------SAVE PLAYLIST------------------------#
    def save_playlist(self, id, userid, name):
        id = int(id)
        global servers_id
        global servers

        index = self.get_index(id)

        playlist = {"name": name, "songs": servers[index]["songs"]}

        if os.path.exists(
            SAVEDPLAYLIST + str(userid) + ".json"
        ):  # si el archivo ya existe
            with open(SAVEDPLAYLIST + str(userid) + ".json", "r") as f:
                saved = json.load(f)  # read it
            if len(saved) >= 5:
                return 0  # return something when it reached the limit
            else:
                for queue in saved:  # return something if playlist alr exists
                    if queue["name"] == name:
                        return 2
                saved.append(playlist)
                with open(
                    SAVEDPLAYLIST + str(userid) + ".json", "w"
                ) as f:  # append the song
                    json.dump(saved, f, indent=4)  # create it
                return 1
        else:  # if it doesn't exist
            with open(SAVEDPLAYLIST + str(userid) + ".json", "w") as f:
                json.dump([playlist], f, indent=4)  # create it
            return 1

    # -----------------------LOAD PLAYLIST------------------------#
    def load_playlist(self, id, userid, name):
        id = int(id)
        global servers_id
        global servers

        if os.path.exists(
            SAVEDPLAYLIST + str(userid) + ".json"
        ):  # si el archivo ya existe
            with open(SAVEDPLAYLIST + str(userid) + ".json", "r") as f:
                saved = json.load(f)  # read it

                for playlist in saved:
                    if playlist["name"] == name:
                        if self.exists(id):
                            servers[self.get_index(id)]["songs"] += playlist["songs"]
                            return 1
                        else:
                            return playlist["songs"]
        return 0

    # -----------------------SHOW PLAYLIST------------------------#
    def show_playlist(self, userid):
        global servers
        global servers_id

        if os.path.exists(
            SAVEDPLAYLIST + str(userid) + ".json"
        ):  # si el archivo ya existe
            with open(SAVEDPLAYLIST + str(userid) + ".json", "r") as f:
                saved = json.load(f)  # read it
        else:
            return 0

        return saved

    # -----------------------REMOVE PLAYLIST------------------------#
    def remove_playlist(self, userid, name):

        playlists = self.show_playlist(userid)

        for playlist in playlists:
            if name == playlist["name"]:
                playlists.pop(playlists.index(playlist))
                with open(
                    SAVEDPLAYLIST + str(userid) + ".json", "w"
                ) as f:  # append the song
                    json.dump(playlists, f, indent=4)  # create it
                return 1

        return 0
