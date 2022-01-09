import random
import json
import lenguajes as leng

LINKS_FOLDER = "sources/links/"
SOURCES_FOLDER = "sources/"


class datos:
    def __init__(self):

        formatos = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.mp4', '.mov', '.JPG',
                    '.JPEG', '.PNG', '.GIF', '.WEBP', '.MP4', '.MOV']  # formatos admitidos
        grupos = {  # grupos de links con su informacion
            "carplinks": {
                "fileName": "carplinks.txt",
                "data": [],
                "name": "carpincho",
            },
            "rayllumlinks": {
                "fileName": "rayllumlinks.txt",
                "data": [],
                "name": "rayllum",
            },
            "tdplinks": {
                "fileName": "tdplinks.txt",
                "data": [],
                "name": "tdp",
            },
            "avatarlinks": {
                "fileName": "avatarlinks.txt",
                "data": [],
                "name": "avatar",
            },
            "memelinks": {
                "fileName": "memelinks.txt",
                "data": [],
                "name": "meme",
            },
            "csmlinks": {
                "fileName": "csmlinks.txt",
                "data": [],
                "name": "csm",
            },
            "owlinks": {
                "fileName": "owlinks.txt",
                "data": [],
                "name": "owl",
            },
            "catlinks": {
                "fileName": "catlinks.txt",
                "data": [],
                "name": "cat",
            }
        }

        frases = []
        debugmode = 0  # debugmode
        self.frases = frases
        self.grupos = grupos
        self.formatos = formatos
        self.debugmode = debugmode

#-----------------------GET DATA------------------------#

    def get_data(self):
        grupos = self.grupos
        for key in grupos.keys():
            with open(LINKS_FOLDER+grupos[key]["fileName"], "r") as f:
                for line in f:
                    if line != '\n':
                        grupos[key]["data"].append(line)
        self.grupos = grupos  # agarra la data del archivo de texto y devuelve grupos
        return grupos

#-----------------------SET DATA------------------------#

    def set_data(self, grupo, arg):  # agrega links a data y al archivo
        grupos = self.grupos
        archivo = LINKS_FOLDER+grupos[grupo]["fileName"]
        grupos[grupo]["data"].append(arg)
        with open(archivo, "w")as txt_file:
            for line in grupos[grupo]["data"]:
                txt_file.write("".join(line)+"\n")

#-----------------------REM DATA------------------------#

    def rem_data(self, grupo, arg, x):  # remueve links del archivo
        grupos = self.grupos
        y = grupos[grupo]["data"].index(arg)
        grupos[grupo]["data"].pop(y)
        archivo = LINKS_FOLDER+grupos[grupo]["fileName"]
        with open(archivo, "r") as f:
            lines = f.readlines()
        with open(archivo, "w") as f:
            for line in lines:
                if line.strip("\n") != x:
                    f.write(line)

#-----------------------GET FORMATOS------------------------#

    def get_formatos(self):
        return self.formatos

#-----------------------GET GRUPOSTEXT------------------------#

    def get_gruposText(self, message):
        lenguage = self.get_lenguaje(message)
        return leng.gruposText[lenguage]

#-----------------------GET 8B------------------------#

    def get_respuestas8ball(self, message):
        lenguage = self.get_lenguaje(message)
        return leng.Respuestas8ball[lenguage]

#-----------------------GET DEBUGMODE------------------------#

    def get_debugmode(self):
        return self.debugmode

#-----------------------SET DEBUGMODE------------------------#

    def set_debugmode(self, state):
        self.debugmode = state

#-----------------------SET FRASE------------------------#

    def set_frase(self, frase):  # pone una frase
        frases = self.frases
        frasesFile = []
        with open(SOURCES_FOLDER+"frases.txt", "r") as f:
            for line in f:
                if line != '\n':
                    frasesFile.append(line)
        frases = frasesFile  # agarra las frases del archivo
        if (frase+"\n") not in frases:  # si la frase no esta ya en el archivo la agrega
            frases.append(frase)
            with open(SOURCES_FOLDER+"frases.txt", "w")as txt_file:
                for line in frases:
                    txt_file.write("".join(line)+"\n")
            return 1  # si fue exitoso retorna un 1
        else:
            return 0  # sino retorna un 0

#-----------------------GET FRASE------------------------#

    def get_frase(self, type, *dato):
        frases = self.frases
        frasesFile = []
        with open(SOURCES_FOLDER+"frases.txt", "r") as f:
            for line in f:
                if line != '\n':
                    frasesFile.append(line)
        frases = frasesFile  # agarra las frases del archivo
        arrayReturns = []
        if type == "none":
            # si el type es none retorna una frase random
            return random.choice(frases)

        elif type == "autor":  # si el type es autor
            for texto in frases:
                textolow = texto.lower()
                x = textolow.find('!')
                y = textolow.rfind('!')
                autor = textolow[x+1:y-1]  # busca el autor de todas las frases
                if autor == dato[0].lower():  # si coincide se guarda la fras en una array
                    arrayReturns.append(texto)
            if len(arrayReturns) > 0:  # si la array tiene algun valor se retorna
                return arrayReturns
            else:
                return -1  # si la array esta vacia se retorna -1

        elif type == "fecha":  # si el type es fecha
            for texto in frases:
                textolow = texto.lower()
                x = textolow.find('!')
                y = textolow.rfind('!')
                fecha = textolow[y+1:]  # se busca la fecha
                fecha = fecha.replace("\n", '')
                if fecha == dato[0].lower():  # si es igual se guarda la frase en una array
                    arrayReturns.append(texto)
            if len(arrayReturns) > 0:  # si la array tiene algun valor se retorna
                return arrayReturns
            else:
                return -1  # si la array esta vacia se retorna -1

        elif type == "palabra":  # si el type es palabra
            for texto in frases:
                textolow = texto.lower()
                x = textolow.find("!")
                textolow = textolow[:x]
                x = textolow.find(dato[0].lower())
                y = textolow[x:].find(" ")  # se busca si esta
                if x > -1:
                    # se compara la palabra encontrada con la palabra dada
                    word = textolow[x:x+y]
                    if word == dato[0].lower():
                        # si coincide se guarda la frase en la array
                        arrayReturns.append(texto)
            if len(arrayReturns) > 0:
                return arrayReturns  # se retorna la array
            else:
                return -1  # si esta vacia se retorna -1
        else:
            return 0  # si no es un type invalido se retorna 0

#-----------------------REM FRASE------------------------#

    def rem_frase(self, frase):
        frases = self.frases
        frasesFile = []
        with open(SOURCES_FOLDER+"frases.txt", "r") as f:
            for line in f:
                if line != '\n':
                    frasesFile.append(line)
        frases = frasesFile  # se cargan las frases del archivo
        if (frase+"\n") in frases:  # se checkea ke la frase ya este
            x = frases.index(frase+"\n")
            frases = frases.pop(x)
            with open(SOURCES_FOLDER+"frases.txt", "r") as f:
                lines = f.readlines()
            with open(SOURCES_FOLDER+"frases.txt", "w") as f:
                for line in lines:
                    if line.strip("\n") != frase:
                        f.write(line)  # se busca y se elimina
            return 1  # si funciona se retorna 1
        else:
            return 0  # sino se retorna 0

#-----------------------GET PREFIX------------------------#
    async def get_prefix(self, bot, message):
        id = message.guild.id
        f = open(SOURCES_FOLDER+"prefix.json")
        data = json.load(f)
        for server in data:
            if(server["id"] == int(id)):
                return server["prefix"]
        with open(SOURCES_FOLDER+'prefix.json', 'w') as f:
            data.append(
                {
                    "id": int(id),
                    "prefix": "\"",
                    "leng":"EN"
                }
            )
            json.dump(data, f)
            return "\""

#-----------------------SET PREFIX------------------------#
    async def set_prefix(self, newprefix, message):
        id = message.guild.id
        with open(SOURCES_FOLDER+'prefix.json') as f:
            data = json.load(f)

        for server in data:
            if(server["id"] == int(id)):
                server["prefix"] = newprefix
        with open(SOURCES_FOLDER+'prefix.json', "w") as f:
            json.dump(data, f)

#-----------------------GET LENGUAJE-----------------------#

    def get_lenguaje(self, message):
        id = message.guild.id
        f = open(SOURCES_FOLDER+"prefix.json")
        data = json.load(f)

        for server in data:
            if(server["id"] == int(id)):
                return server["leng"]
        with open(SOURCES_FOLDER+'prefix.json', 'w') as f:
            data.append(
                {
                    "id": int(id),
                    "prefix": "\"",
                    "leng":"EN"
                }
            )
            json.dump(data, f)
            return "EN"

#-----------------------SET LENGUAJE------------------------#

    def set_lenguaje(self, newlenguaje, message):
        id = message.guild.id
        with open(SOURCES_FOLDER+'prefix.json') as f:
            data = json.load(f)

        for server in data:
            if(server["id"] == int(id)):
                server["leng"] = newlenguaje
        with open(SOURCES_FOLDER+'prefix.json', "w") as f:
            json.dump(data, f)