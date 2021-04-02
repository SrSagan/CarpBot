class datos:
    def __init__(self):
        formatos = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.mp4', '.mov', '.JPG', '.JPEG', '.PNG', '.GIF', '.WEBP', '.MP4', '.MOV']
        
        grupos={
        "carplinks":{
            "fileName":"carplinks.txt",
            "data":[],
        	"name":"carpincho"
        },
        "rayllumlinks":{
            "fileName":"rayllumlinks.txt",
            "data":[],
        	"name":"rayllum"
        },
        "tdplinks":{
            "fileName":"tdplinks.txt",
            "data":[],
        	"name":"tdp"
        },
        "avatarlinks":{
            "fileName":"avatarlinks.txt",
            "data":[],
        	"name":"avatar"
        },
        "memelinks":{
            "fileName":"memelinks.txt",
            "data":[],
        	"name":"meme"
        },
        "csmlinks":{
        	"fileName":"csmlinks.txt",
        	"data":[],
        	"name":"csm"
        },
        }
        gruposText = """
        **avatar**: Refiriendose a Avatar la Leyenda de Aang
        **tdp**: Refiriendose a The Dragon Prince
        **rayllum**: Refiriendose antra el ship de Rayla y Callum de tdp
        **carpincho**: Refiriendose al mejor animal en la existencia
        **meme**: Todo tipo de memes
        **csm**: Refiriendose a chainsawman
        """
        for key in grupos.keys():
            with open(grupos[key]["fileName"], "r") as f:
                for line in f:
                    if line != '\n':
                        grupos[key]["data"].append(line)
        respuestas8ball=["Confirmo", "Niego", "No", "Si", "Capaz", "Que pregunta boluda eh", "No, creo que no", "Si, creo...", "Puede ser", "Sabes que no", "Sabes que si", "jajaja no", "jajaja si", "Yes", "Não", "Y a vos que te parece?", "Desconfirmo"]
        self.grupos = grupos
        self.formatos = formatos
        self.gruposText = gruposText
        self.respuestas8ball = respuestas8ball
    
        