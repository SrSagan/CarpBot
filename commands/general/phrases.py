import discord
from commands.base.base_command import UserCommand
from discord.ext import commands
import lenguajes as leng
from services.phrase_service import PhraseService


class PhrasesCommand(UserCommand):
    """Comandos de frases filosóficas - Disponible para todos."""

    def __init__(self, bot):
        super().__init__(bot)
        self.phrase_service = PhraseService()

    @commands.command(name="addfrase", aliases=["af"])
    async def addfrase(self, ctx: commands.Context, *args):
        """Agrega una frase filosófica al sistema."""
        self.log_command_user(ctx, "addfrase")
        lang = self.get_language(ctx)

        if not args:
            await ctx.send(leng.eufpa[lang])
            return

        # Juntar todo el texto
        texto = " ".join(args)

        # TODO: Reemplazar parsing manual con regex o modelo estructurado
        # Formato legacy: "frase ! autor ! fecha" es frágil
        # Buscar los delimitadores !
        x = texto.find("!")
        y = texto.rfind("!")

        if x == -1 or y == -1:
            await ctx.send(leng.pfeaf[lang])
            return

        # Parsear la frase: "frase ! autor ! fecha"
        frase = texto[:x].strip()
        autor = texto[x + 1 : y].strip()
        fecha = texto[y + 1 :].strip()

        # Intentar guardar la frase
        done = self.phrase_service.add_phrase(texto)

        if done:
            embed = discord.Embed(title=leng.fa[lang], color=0x3498DB)
            embed.add_field(name="Frase", value=frase, inline=False)
            embed.add_field(name="Autor", value=autor, inline=True)
            embed.add_field(name="Fecha", value=fecha, inline=True)
            await ctx.send(embed=embed)
        else:
            await ctx.send(leng.lfyseell[lang])

    @commands.command(name="frasefilosofica", aliases=["ff"])
    async def frasefilosofica(self, ctx: commands.Context, *args):
        """Muestra una frase filosófica aleatoria o busca por palabra clave."""
        self.log_command_user(ctx, "frasefilosofica")
        lang = self.get_language(ctx)

        frases = []

        # Si hay argumentos, buscar por palabra clave
        if args:
            texto = " ".join(args)
            x = texto.find("!")

            if x > -1:
                # Buscar por palabra después del !
                palabra = texto[x + 1 :].strip()
                frases = self.phrase_service.search_phrase(palabra)
            else:
                # Obtener frase aleatoria
                try:
                    frases = [self.phrase_service.get_random_phrase()]
                except ValueError:
                    frases = []
        else:
            # Sin argumentos, frase aleatoria
            try:
                frases = [self.phrase_service.get_random_phrase()]
            except ValueError:
                frases = []

        # Verificar si se encontraron frases
        if not frases:
            await ctx.send(leng.nsen[lang])
            return

        # Mostrar cada frase encontrada
        # TODO: Refactorizar parsing de frases a un método/modelo reutilizable
        for frase_completa in frases:
            x = frase_completa.find("!")
            y = frase_completa.rfind("!")

            if x == -1 or y == -1:
                continue

            frase = frase_completa[:x].strip()
            autor = frase_completa[x + 1 : y].strip()
            fecha = frase_completa[y + 1 :].strip()

            embed = discord.Embed(title=leng.ff[lang], color=0x3498DB)
            embed.add_field(name=leng.f_a_f[lang][0], value=frase, inline=False)
            embed.add_field(name=leng.f_a_f[lang][1], value=autor, inline=True)
            embed.add_field(name=leng.f_a_f[lang][2], value=fecha, inline=True)
            await ctx.send(embed=embed)

    @commands.command(name="removefrase", aliases=["rf"])
    async def removefrase(self, ctx: commands.Context, *args):
        """Elimina una frase filosófica del sistema."""
        self.log_command_user(ctx, "removefrase")
        lang = self.get_language(ctx)

        if not args:
            await ctx.send(leng.eufpa[lang])
            return

        # Juntar el texto
        texto = " ".join(args)

        # Intentar eliminar la frase
        removed = self.phrase_service.remove_phrase(texto)

        if removed:
            await ctx.send(leng.fr[lang])
        else:
            await ctx.send(leng.lfnfr[lang])


async def setup(bot):
    """Configura los comandos de frases."""
    await bot.add_cog(PhrasesCommand(bot))
