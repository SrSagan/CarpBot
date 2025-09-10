import json
import os
import data
import servermanager

sm = servermanager.serverManager()

class song():
    def __init__(self, name, link, length, type):
        self.name = name
        self.link = link
        self.length = length
        self.type = type


class server():
    def __init__(self, id):
        self.id = id
        self.cplaying = 0
        self.ptime = None
        self.time = None
        self.status = False
        self.tlength = 0
        self.looping = 0
        self.songs = []