import os

import discord
from discord.ext import commands
import data
import lenguajes as leng

a = data.datos()
formatos = a.formatos


class links(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

#-----------------------------ADDLINK-----------------------------#

    @commands.command(  # para agregar un link codigo LARGOOOOOOOOOOOOOOOOOOOOOO
        aliases=['al'],
        name='addlink',
    )
    async def add_link(self, ctx, *args):
        a = data.datos()
        grupos = a.get_data()
        print("addlink usado")
        if(len(args) <= 0):
            await ctx.send(leng.eulopjcec[a.get_lenguaje(ctx.message)])
            return 0

        for arg in args:
            x = arg.rfind('.')
            y = arg.rfind('?')
            if(x != -1):
                if(y != -1):
                    formato = arg[x:y]
                else:
                    formato = arg[x:]
                    
                if(formato not in a.get_formatos() and arg.find("youtu") == -1 and args[0].lower() != 'exception'):
                    await ctx.send(leng.fi[a.get_lenguaje(ctx.message)])
                    return 0
            else:
                if(args[0].lower() != 'exception' and args[0].lower() != 'continue'):
                    await ctx.send(leng.lnkinv[a.get_lenguaje(ctx.message)])
                    return 0



        ladded = 0
        gstate = 0

        while gstate == 0:
            await ctx.send(leng.eqgqael[a.get_lenguaje(ctx.message)])
            embed = discord.Embed(title=leng.grupos[a.get_lenguaje(
                ctx.message)], color=0x3498DB, description=a.get_gruposText(ctx.message))
            await ctx.send(embed=embed)
            # se espera la respuesta del grupo
            msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)

            if(msg.content.lower() == 'cancel'):
                return 0

            for grupo in grupos:
                if(msg.content == grupos[grupos.index(grupo)]["name"]):
                    selectedGroup = grupo
                    gstate = 1
                    break

            if(gstate == 0):
                await ctx.send(leng.gi[a.get_lenguaje(ctx.message)])

        for arg in args:
            if(arg in selectedGroup["data"] or arg+"\n" in selectedGroup["data"]):
                await ctx.send(leng.elyeell[a.get_lenguaje(ctx.message)])
                return 0

            if(args[0].lower() == 'exception'):
                if(arg != args[0]):
                    a.set_data(selectedGroup, arg)
                    ladded += 1

            elif(args[0].lower() == 'continue'):
                await ctx.send(leng.ei[a.get_lenguaje(ctx.message)])

                while True:
                    gstate=0
                    msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)

                    if(msg.content.lower() == 'end'):
                        await ctx.send(leng.terminado[a.get_lenguaje(ctx.message)])
                        break

                    for c in msg.attachments:
                        img = c.url
                        if(img in selectedGroup["data"] or img+"\n" in selectedGroup["data"]):
                            await ctx.send(leng.elyeell[a.get_lenguaje(ctx.message)])
                            gstate = 1
                            break

                        if(gstate != 1):
                            a.set_data(selectedGroup, img)
                            ladded += 1
            else:
                a.set_data(selectedGroup, arg)
                ladded += 1

        if ladded == 1:  # cantidad de links igual a 1
            await ctx.send(str(ladded)+" "+leng.laa_lsaa[a.get_lenguaje(ctx.message)][0]+" '"+str(selectedGroup["name"])+"'")
        elif ladded > 1:  # cantidad de links agregados mayor a uno se dice
            await ctx.send(str(ladded)+" "+leng.laa_lsaa[a.get_lenguaje(ctx.message)][1]+" '"+str(selectedGroup["name"])+"'")

#-----------------------------REMOVELINK-----------------------------#

    @commands.command(  # comando de removelink para remover links....
        aliases=['rl'],
        name='removelink',
    )
    async def removelink(self, ctx, *args):
        a = data.datos()
        grupos = a.get_data()  # agarra la data de grupos
        print("removelink usado")
        removedLinks=[]
        for g in grupos:
            removedLinks.append(0)
        
        for x in args:  # agarra el argumento
            if len(args) > 0:  # checkea que haya argumentos
                done=False
                for grupo in grupos:  # checkea en cada grupo
                    if not x in grupo["data"]:  # si no esta entre los links
                        z = (x+"\n")
                    else:
                        z = x

                    if z in grupo["data"]:
                        a.rem_data(grupo, z, x)  # saca la data
                        removedLinks[grupos.index(grupo)]+=1 # sube el contado
                        print("link removido")
                        done=True
                    
                if(done == False):
                    await ctx.send(leng.el_nseeng[a.get_lenguaje(ctx.message)][0]+" '"+x+"' "+leng.el_nseeng[a.get_lenguaje(ctx.message)][1])
            else:
                await ctx.send(leng.eeldlijcec[a.get_lenguaje(ctx.message)])
        for removed in removedLinks:  # se escribe cuantos links se eliminaron de que grupos
            if removed > 0:
                if removed == 1:
                    await ctx.send(str(removed)+" "+leng.lrd_lsrd[a.get_lenguaje(ctx.message)][0]+" '"+str(grupos[removedLinks.index(removed)]["name"])+"'")
                elif removed > 1:
                    await ctx.send(str(removed)+" "+leng.lrd_lsrd[a.get_lenguaje(ctx.message)][1]+" '"+str(grupos[removedLinks.index(removed)]["name"])+"'")


async def setup(bot):
    await bot.add_cog(links(bot))
