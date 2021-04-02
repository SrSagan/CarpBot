import discord
from discord.ext import commands
import data
import random

a=data.datos()


class generalcommands(commands.Cog):
    def __init__(self, bot):
        self.bot=bot
    @commands.command(
        name="dado",
        brief="Tira un dado",
        help="Tira un dado dando un numero del 1 al 6"
    )
    async def dado(self, ctx, *args):
        print("dado usado")
        response=random.randrange(1, 6)
        await ctx.send(response)
    
    @commands.command(
        aliases=['8b'],
        name="8ball",
        brief="Responde preguntas",
        help="Responde preguntas al igual que una 8-ball"
    )
    async def eightball(self, ctx, *args):
        print("8ball usado")
        if len(args) > 0:
            texto=''
            for word in args:
                texto = (texto+" "+word)
            embed=discord.Embed(title="8-ball",color=0x3498DB)
            embed.add_field(name="Pregunta", value=texto, inline=False)
            embed.add_field(name="Respuesta", value=random.choice(a.respuestas8ball), inline=False)
            await ctx.send(embed=embed)
        else:
            await ctx.send("Tenes que hacer una pregunta si queres que responda")

def setup(bot):
    bot.add_cog(generalcommands(bot))
