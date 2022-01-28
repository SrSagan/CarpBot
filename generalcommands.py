from logging import debug
import discord
from discord import embeds
from discord.ext import commands
import data
import random
import lenguajes as leng


a = data.datos()

a.set_debugmode(0)
debugmode = a.debugmode


class general(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

#-----------------------------DADO-----------------------------#

    @commands.command(  # dado....
        name="dado",
    )
    async def dado(self, ctx, *args):
        print("dado usado")
        # num random desde el 1 al 6.... es un dado
        response = random.randrange(1, 6)
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

#-----------------------------8BALL-----------------------------#
    @commands.command(
        aliases=['8b'],  # 8ball responde con si o no
        name="8ball",
    )
    async def eightball(self, ctx, *args):

        print("8ball usado")
        if len(args) > 0:
            texto = ''
            for word in args:
                texto = (texto+" "+word)  # junta todo el texto del msg
            embed = discord.Embed(title="8-ball", color=0x3498DB)
            # pone to el marquito bonito
            embed.add_field(name=leng.p_r[a.get_lenguaje(ctx.message)][0], value=texto, inline=False)
            respuestas = a.get_respuestas8ball(ctx.message)  # agarra las respuestas de data
            # junta una respuesta random con la pregunta
            embed.add_field(name=leng.p_r[a.get_lenguaje(ctx.message)][1], value=random.choice(
                respuestas), inline=False)
            await ctx.send(embed=embed)  # envia la respuesta
        else:
            await ctx.send(leng.tqhupsqqr[a.get_lenguaje(ctx.message)])

#-----------------------------ADDFRASE-----------------------------#

    @commands.command(
        aliases=["af"],
        name="addfrase",
    )
    async def addfrase(self, ctx, *args):
        print("addfrase usado")
        frasesArray = []
        if len(args) > 0:
            texto = ''
            for word in args:
                texto = (texto+" "+word)  # junta todo el texto del msg
            x = texto.find('!')  # busca los simbolos divisores (!)
            y = texto.rfind('!')
            autor = texto[x+1:y-1]
            fecha = texto[y+1:]
            frase = texto[:x-1]
            done = a.set_frase(texto)  # guarda la frase
            if done:  # si la frase se guardo lo envia
                print("frase agregada")
                embed = discord.Embed(title=leng.fa[a.get_lenguaje(ctx.message)], color=0x3498DB)
                embed.add_field(name="Frase", value=frase,
                                inline=False)  # pone la frase
                embed.add_field(name="Autor", value=autor,
                                inline=True)  # pone el autor
                embed.add_field(name="Fecha", value=fecha,
                                inline=True)  # pone la fecha
                await ctx.send(embed=embed)  # envia la respuesta
            else:
                # si la frase no se guardo estaba en la lista e informa
                await ctx.send(leng.lfyseell[a.get_lenguaje(ctx.message)])
        else:
            await ctx.send(leng.eufpa[a.get_lenguaje(ctx.message)])

#-----------------------------FRASEFILOSOFICA-----------------------------#

    @commands.command(
        aliases=["ff"],
        name="frasefilosofica",
    )
    async def frasefilosofica(self, ctx, *args):
        print("Frase Filosofica usado")
        if len(args) > 0:
            texto = ''
            for word in args:
                texto = (texto+" "+word)  # junta todo el texto del msg
            x = texto.find("!")
            y = texto.find("¡")  # checkea por cualquiera de los 3 divisores
            z = texto.find("?")

            if x > -1:  # separa el autor y lo busca
                j = len(texto)
                autor = texto[x+1:j]
                if debugmode:
                    await ctx.send(autor)
                frases = a.get_frase("autor", autor)
                if debugmode:
                    await ctx.send(str(frases))

            elif y > -1:  # separa la fecha y la busca
                j = len(texto)
                fecha = texto[y+1:j]
                if debugmode:
                    await ctx.send(fecha)
                frases = a.get_frase("fecha", fecha)
                if debugmode:
                    await ctx.send(str(frases))

            elif z > -1:  # separa una palabra y la busca
                j = len(texto)
                word = texto[z+1:j]
                if debugmode:
                    await ctx.send(word)
                frases = a.get_frase("palabra", word)
                if debugmode:
                    await ctx.send(str(frases))

            else:
                # si no se encontro nada informa
                await ctx.send(leng.nsen[a.get_lenguaje(ctx.message)])

            if frases != -1:  # si se encontraron frases las envia todas
                for frase in frases:
                    x = frase.find('!')
                    y = frase.rfind('!')
                    autor = frase[x+1:y-1]
                    fecha = frase[y+1:]
                    frase = frase[:x-1]
                    embed = discord.Embed(
                        title=leng.ff[a.get_lenguaje(ctx.message)], color=0x3498DB)
                    embed.add_field(name=leng.f_a_f[a.get_lenguaje(ctx.message)][0], value=frase,
                                    inline=False)  # pone la frase
                    embed.add_field(name=leng.f_a_f[a.get_lenguaje(ctx.message)][1], value=autor,
                                    inline=True)  # pone el autor
                    embed.add_field(name=leng.f_a_f[a.get_lenguaje(ctx.message)][2], value=fecha,
                                    inline=True)  # pone la fecha

                    await ctx.send(embed=embed)  # envia la respuesta
            else:
                # si no se encuentra nada se informa
                await ctx.send(leng.nsen[a.get_lenguaje(ctx.message)])

        else:  # si no se busca nada pone una random
            frase = a.get_frase("none")
            x = frase.find('!')
            y = frase.rfind('!')
            autor = frase[x+1:y-1]
            fecha = frase[y+1:]
            frase = frase[:x-1]
            embed = discord.Embed(title=leng.ff[a.get_lenguaje(ctx.message)], color=0x3498DB)
            embed.add_field(name=leng.f_a_f[a.get_lenguaje(ctx.message)][0], value=frase,
                            inline=False)  # pone la frase
            embed.add_field(name=leng.f_a_f[a.get_lenguaje(ctx.message)][1], value=autor,
                            inline=True)  # pone el autor
            embed.add_field(name=leng.f_a_f[a.get_lenguaje(ctx.message)][2], value=fecha,
                            inline=True)  # pone la fecha
            await ctx.send(embed=embed)  # envia la respuesta

#-----------------------------REMOVEFRASE-----------------------------#

    @commands.command(
        name="removefrase",
        aliases=["rf"],
    )
    async def removefrase(self, ctx, *args):
        print("removefrase usado")
        if len(args) > 0:
            texto = ''
            for word in args:
                texto = (texto+" "+word)
            removed = a.rem_frase(texto)  # remueve la frase e informa
            if removed:
                await ctx.send(leng.fr[a.get_lenguaje(ctx.message)])
            else:
                await ctx.send(leng.lfnfr[a.get_lenguaje(ctx.message)])
        else:
            await ctx.send(leng.eufpa[a.get_lenguaje(ctx.message)])

#-----------------------------CHANGEPREFIX-----------------------------#

    @commands.command(
        name="changeprefix",
        aliases=["cp"],
    )
    async def changeprefix(self, ctx, *args):
        if(ctx.message.author.guild_permissions.administrator):
            print("change prefix usado")

            embed = discord.Embed(title=leng.cp[a.get_lenguaje(ctx.message)], color=0x3498DB)
            embed.add_field(name=leng.pa[a.get_lenguaje(ctx.message)], value="**"+await a.get_prefix(0, ctx.message)+"**")

            await ctx.send(leng.eunp[a.get_lenguaje(ctx.message)])
            message = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
            newprefix = message.content

            if(newprefix.lower() == "cancel"):
                await ctx.send(leng.oc[a.get_lenguaje(ctx.message)])
                return 0

            embed.add_field(name=leng.np[a.get_lenguaje(ctx.message)], value="**"+newprefix+"**")
            await a.set_prefix(newprefix, ctx.message)

            await ctx.send(embed=embed)
        else:
            await ctx.send(leng.sapuec[a.get_lenguaje(ctx.message)])

#-----------------------------HELP-----------------------------#

    @commands.command(
        name="help",
        aliases=["h"],
    )
    async def help(self, ctx, *args):

        lenguaje = a.get_lenguaje(ctx.message)

        embed = discord.Embed(title="Help", color=0x3498DB)

        help = leng.help[lenguaje]

        while True:
            x = help.find("##")
            if(x == -1):
                break
            y = help.find("-")
            name=help[x+2:y]
            help = help[y:]
            x = help.find("##")
            if(x == -1):
                break
            value=help[:x]
            help=help[x:]
            embed.add_field(name=name, value=value, inline=False)

        await ctx.send(embed=embed)

#-----------------------------CHANGE LENGUAJE-----------------------------#

    @commands.command(
        name="changelenguage",
        aliases=["cl"],
    )
    async def change_lenguage(self, ctx, *args):
        if(ctx.message.author.guild_permissions.administrator):
            valid_lenguajes=["EN", "ES", "PT"]

            if(len(args) > 0 and args[0].upper() in valid_lenguajes):
                newlenguaje = args[0].upper()
            else:
                embed = discord.Embed(title=leng.cel[a.get_lenguaje(ctx.message)], color=0x3498DB)
                embed.add_field(name=leng.eul[a.get_lenguaje(ctx.message)], value=leng.pei[a.get_lenguaje(ctx.message)])
                await ctx.send(embed=embed)
                message = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
                newlenguaje = message.content
                newlenguaje = newlenguaje.upper()
                

            if(newlenguaje == "CANCEL"):
                await ctx.send(leng.oc[a.get_lenguaje(ctx.message)])
                return 0
            elif(newlenguaje in valid_lenguajes):
                await ctx.send(leng.lca[a.get_lenguaje(ctx.message)]+" "+newlenguaje)
                a.set_lenguaje(newlenguaje, ctx.message)
            else:
                await ctx.send(leng.li[a.get_lenguaje(ctx.message)])
        else:
            await ctx.send(leng.sapuec[a.get_lenguaje(ctx.message)])

def setup(bot):
    bot.add_cog(general(bot))
