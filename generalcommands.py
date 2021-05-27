from logging import debug
import discord
from discord.ext import commands
import data
import random
import os


a=data.datos()

a.set_debugmode(0)
debugmode = a.debugmode


class generalcommands(commands.Cog):
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

def setup(bot):
    bot.add_cog(generalcommands(bot))
