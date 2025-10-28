from abc import ABC
import discord
from discord.ext import commands

from services.server_config_service import ServerConfigService

import lenguajes as leng
from utils.permissions import is_admin_or_dev, is_dev_user


class BaseCommand(commands.Cog, ABC):
	"""Clase base abstracta para todos los comandos del bot."""

	def __init__(self, bot: commands.Bot):
		self.bot = bot
		self.config_service = ServerConfigService()

	# ========== Ayudas comunes ==========

	def get_language(self, ctx: commands.Context) -> int:
		"""Obtiene el idioma configurado del servidor."""
		return self.config_service.get_language(ctx.guild.id)

	def get_prefix(self, ctx: commands.Context) -> str:
		"""Obtiene el prefijo configurado del servidor."""
		return self.config_service.get_prefix(ctx.guild.id)

	async def send_error(self, ctx: commands.Context, error_key: str):
		"""Envía un mensaje de error traducido."""
		lang = self.get_language(ctx)
		await ctx.send(leng.errors[error_key][lang])

	async def send_success(self, ctx: commands.Context, message: str):
		"""Envía un mensaje de éxito con formato."""
		embed = discord.Embed(description=f"✅ {message}", color=0x2ECC71)
		await ctx.send(embed=embed)

	def log_command_user(self, ctx: commands.Context, command_name: str):
		"""Registra el uso de un comando."""
		print(f"[{ctx.guild.name}] {ctx.author} usó el comando: {command_name}")


class UserCommand(BaseCommand):
	"""Comandos disponibles para todos los usuarios."""

	pass


class AdminCommand(BaseCommand):
	"""Comandos que requieren permisos de administrador."""

	async def check_permissions(self, ctx: commands.Context) -> bool:
		"""Verificar si el usuario tiene permisos de admin."""
		if not is_admin_or_dev(ctx):
			lang = self.get_language(ctx)
			await ctx.send(leng.sapuec[lang])  # Mensaje de permisos insuficientes
			return False
		return True


class DevCommand(BaseCommand):
	"""Comandos solo para desarrolladores."""

	async def check_permissions(self, ctx: commands.Context) -> bool:
		"""Verificar si el usuario es desarrollador."""
		if not is_dev_user(ctx.author.id):
			await ctx.send("🔒 Solo desarrolladores pueden usar este comando.")
			return False
		return True
