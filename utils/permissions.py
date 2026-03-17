import os
from dotenv import load_dotenv

from discord.ext import commands

load_dotenv()

# Carga IDs de dessarrolladores desde .env
DEV_USERS = []
dev_ids = os.getenv("DEV_USERS", "")

if dev_ids:
    DEV_USERS = [int(id.strip()) for id in dev_ids.split(",") if id.strip()]


def is_dev_user(user_id: int) -> bool:
    """Verifica si el usuario es un desarrollador."""
    return user_id in DEV_USERS


def is_admin_or_dev(ctx: commands.Context) -> bool:
    """Verifica si el usuario tiene permisos de administrador o es desarrollador."""
    is_admin = ctx.author.guild_permissions.administrator
    is_dev = is_dev_user(ctx.author.id)
    return is_admin or is_dev
