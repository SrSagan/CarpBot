class datos:
    def __init__(self):
        formatos = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.mp4', '.mov', '.JPG', '.JPEG', '.PNG', '.GIF', '.WEBP', '.MP4', '.MOV'] #formatos admitidos
        grupos={ #grupos de links con su informacion
        "carplinks":{
            "fileName":"carplinks.txt",
            "data":[],
        	"name":"carpincho",
        },
        "rayllumlinks":{
            "fileName":"rayllumlinks.txt",
            "data":[],
        	"name":"rayllum",
        },
        "tdplinks":{
            "fileName":"tdplinks.txt",
            "data":[],
        	"name":"tdp",
        },
        "avatarlinks":{
            "fileName":"avatarlinks.txt",
            "data":[],
        	"name":"avatar",
        },
        "memelinks":{
            "fileName":"memelinks.txt",
            "data":[],
        	"name":"meme",
        },
        "csmlinks":{
        	"fileName":"csmlinks.txt",
        	"data":[],
        	"name":"csm",
        },
        "owlinks":{
            "fileName":"owlinks.txt",
            "data":[],
            "name":"owl",
        },
        }
        #texto para grupos
        gruposText = """ 
        **avatar**: Refiriendose a Avatar la Leyenda de Aang
        **tdp**: Refiriendose a The Dragon Prince
        **rayllum**: Refiriendose antra el ship de Rayla y Callum de tdp
        **carpincho**: Refiriendose al mejor animal en la existencia
        **meme**: Todo tipo de memes
        **csm**: Refiriendose a chainsawman
        **owl**: Referiendose a owls/buhos
        """
        #respuestas de 8ball
        respuestas8ball=["Confirmo", "Niego", "No", "Si", "Capaz", "Que pregunta boluda eh", "No, creo que no", "Si, creo...", "Puede ser", "Sabes que no", "Sabes que si", "jajaja no", "jajaja si", "Yes", "Não", "Y a vos que te parece?", "Desconfirmo"]
        debugmode = 0 #debugmode
        self.grupos = grupos
        self.formatos = formatos
        self.gruposText = gruposText
        self.respuestas8ball = respuestas8ball
        self.debugmode = debugmode

    def get_data(self):
        grupos = self.grupos
        for key in grupos.keys():
            with open(grupos[key]["fileName"], "r") as f:
                for line in f:
                    if line != '\n':
                        grupos[key]["data"].append(line)
        self.grupos=grupos #agarra la data del archivo de texto y devuelve grupos
        return grupos
        
    def set_data(self, grupo, arg): #agrega links a data y al archivo
        grupos = self.grupos
        archivo = grupos[grupo]["fileName"]
        grupos[grupo]["data"].append(arg)
        with open(archivo, "w")as txt_file:
            for line in grupos[grupo]["data"]:
                txt_file.write("".join(line)+"\n")

    def rem_data(self, grupo, arg, x): #remueve links del archivo
        grupos = self.grupos
        y = grupos[grupo]["data"].index(arg)
        grupos[grupo]["data"].pop(y)    
        archivo = grupos[grupo]["fileName"]
        with open(archivo, "r") as f:
        	lines = f.readlines()
        with open(archivo, "w") as f:
        	for line in lines:
        		if line.strip("\n") != x:
        			f.write(line)

    def get_formatos(self):
        return self.formatos
    def get_gruposText(self):
        return self.gruposText
    def get_respuestas8ball(self):
        return self.respuestas8ball
    def get_debugmode(self):
        return self.debugmode
    def set_debugmode(self, state):
        self.debugmode=state