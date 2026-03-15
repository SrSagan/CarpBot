from commands.base.base_command import UserCommand


class ImageCommands(UserCommand):
	"""Cog auxiliar para comandos de imagen adicionales."""

	pass


async def setup(bot):
	"""Configura el módulo auxiliar de comandos de imagen."""
	await bot.add_cog(ImageCommands(bot))
