class music:
    def __init__(self):
        links = []
        names = []
        files = []
        index = 0

        self.links = links
        self.names = names
        self.files = files
        self.index = index

#------------------LINKS------------------#

    def get_links(self):
        return self.links

    def set_links(self, links):
        self.links = links

#------------------NAMES------------------#

    def get_names(self):
        return self.names

    def set_names(self, names):
        self.names = names

#------------------FILES------------------#

    def get_files(self):
        return self.names

    def set_files(self, files):
        self.files = files

#------------------INDEX------------------#

    def get_index(self):
        return self.index

    def set_index(self, index):
        self.inxdex = index