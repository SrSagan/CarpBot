from logging import debug
import discord
from discord.ext import commands
import data
import random
import os
import asyncio


a=data.datos()

a.set_debugmode(0)
debugmode = a.debugmode


class general(commands.Cog):
    def __init__(self, bot):
        self.bot=bot
    @commands.command( #dado....
        name="dado",
        brief="Tira un dado",
        help="Tira un dado dando un numero del 1 al 6"
    )
    async def dado(self, ctx, *args):
        print("dado usado")
        response=random.randrange(1, 6) #num random desde el 1 al 6.... es un dado
        await ctx.send(response)

    '''@commands.command(
        name="santi",
        brief="santi",
        help="santi"
    )
    async def santi(self, ctx, *args):
        print("santi")
        val = ''
        while val != 'end':
            val = input("Escribi un msg:")
            if val != 'end':
                await ctx.send(val)'''

    @commands.command(
        aliases=['8b'], #8ball responde con si o no
        name="8ball",
        brief="Responde preguntas",
        help="Responde preguntas al igual que una 8-ball"
    )
    async def eightball(self, ctx, *args):
        
        print("8ball usado")
        if len(args) > 0:
            texto=''
            for word in args:
                texto = (texto+" "+word) #junta todo el texto del msg
            embed=discord.Embed(title="8-ball",color=0x3498DB)
            embed.add_field(name="Pregunta", value=texto, inline=False) #pone to el marquito bonito
            respuestas = a.get_respuestas8ball() #agarra las respuestas de data
            embed.add_field(name="Respuesta", value=random.choice(respuestas), inline=False) #junta una respuesta random con la pregunta
            await ctx.send(embed=embed) #envia la respuesta
        else:
            await ctx.send("Tenes que hacer una pregunta si queres que responda")

    @commands.command(
        aliases=["af"],
        name="addfrase",
        brief="Agrega frases filosoficas",
        help='Sirve para agregar frases filosoficas (graciosas) para no tener que pinear mensages. Uso: Frase !autor !fecha'
    )
    async def addfrase(self, ctx, *args):
        print("addfrase usado")
        frasesArray = []
        if len(args) > 0:
            texto=''
            for word in args:
                texto = (texto+" "+word) #junta todo el texto del msg
            x = texto.find('!') #busca los simbolos divisores (!)
            y = texto.rfind('!')
            autor = texto[x+1:y-1]
            fecha = texto[y+1:]
            frase = texto[:x-1]
            done = a.set_frase(texto) #guarda la frase
            if done: #si la frase se guardo lo envia
                print("frase agregada")
                embed=discord.Embed(title="Frase Agregada",color=0x3498DB)
                embed.add_field(name="Frase", value=frase, inline=False) #pone la frase
                embed.add_field(name="Autor", value=autor, inline=True) #pone el autor
                embed.add_field(name="Fecha", value=fecha, inline=True) #pone la fecha
                await ctx.send(embed=embed) #envia la respuesta
            else: await ctx.send("La frase ya se encuentra en la lista") #si la frase no se guardo estaba en la lista e informa
        else: await ctx.send("Escriba una frase para agregar")
    
    @commands.command(
        aliases=["ff"],
        name="frasefilosofica",
        brief="Devuelve frase filosofica",
        help="Responde con una frase filosofica random o dependiendo de lo pedido con frase filosofica por autor o fecha. Uso: Para buscar autor escribir !autor, para fecha ¡fecha y para palabra ?palabra"
    )
    async def frasefilosofica(self, ctx, *args):
        print("Frase Filosofica usado")
        if len(args) > 0:
            texto=''
            for word in args:
                texto = (texto+" "+word) #junta todo el texto del msg
            x = texto.find("!")
            y = texto.find("¡") #checkea por cualquiera de los 3 divisores
            z = texto.find("?")

            if x > -1: #separa el autor y lo busca
                j = len(texto)
                autor = texto[x+1:j]
                if debugmode: await ctx.send(autor)
                frases = a.get_frase("autor", autor)
                if debugmode: await ctx.send(str(frases))

            elif y > -1: #separa la fecha y la busca
                j = len(texto)
                fecha = texto[y+1:j]
                if debugmode: await ctx.send(fecha)
                frases = a.get_frase("fecha", fecha)
                if debugmode: await ctx.send(str(frases))

            elif z > -1: #separa una palabra y la busca
                j = len(texto)
                word = texto[z+1:j]
                if debugmode: await ctx.send(word)
                frases = a.get_frase("palabra", word)
                if debugmode: await ctx.send(str(frases))

            else:
                await ctx.send("No se encontro nada") #si no se encontro nada informa
            
            if frases != -1: #si se encontraron frases las envia todas
                    for frase in frases:
                        x = frase.find('!')
                        y = frase.rfind('!')
                        autor = frase[x+1:y-1]
                        fecha = frase[y+1:]
                        frase = frase[:x-1]
                        embed=discord.Embed(title="Frase Filosofica",color=0x3498DB)
                        embed.add_field(name="Frase", value=frase, inline=False) #pone la frase
                        embed.add_field(name="Autor", value=autor, inline=True) #pone el autor
                        embed.add_field(name="Fecha", value=fecha, inline=True) #pone la fecha

                        await ctx.send(embed=embed) #envia la respuesta
            else: await ctx.send("No se encontro nada") #si no se encuentra nada se informa

        else: #si no se busca nada pone una random
            frase = a.get_frase("none")
            x = frase.find('!')
            y = frase.rfind('!')
            autor = frase[x+1:y-1]
            fecha = frase[y+1:]
            frase = frase[:x-1]
            embed=discord.Embed(title="Frase Filosofica",color=0x3498DB)
            embed.add_field(name="Frase", value=frase, inline=False) #pone la frase
            embed.add_field(name="Autor", value=autor, inline=True) #pone el autor
            embed.add_field(name="Fecha", value=fecha, inline=True) #pone la fecha
            await ctx.send(embed=embed) #envia la respuesta
    
    @commands.command(
        name="removefrase",
        aliases=["rf"],
        brief="Remueve una frase",
        help="Remueve una frase, la frase tiene que ser escrita igual de como se agrego"
    )
    async def removefrase(self, ctx, *args):
        print("removefrase usado")
        if len(args) > 0:
            texto=''
            for word in args:
                texto = (texto+" "+word)
            removed = a.rem_frase(texto) #remueve la frase e informa
            if removed: await ctx.send("Frase removida")
            else: await ctx.send("La frase no fue removida")
        else: await ctx.send("Escriba una frase para remover")

def setup(bot):
    bot.add_cog(general(bot))
