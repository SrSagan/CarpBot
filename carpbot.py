"""
CarpBot - Bot de Discord multifuncional
Punto de entrada principal de la aplicación.
"""

# First: Librerías estándar
import asyncio
import os

# Second: Librerías de terceros
import discord
from discord.ext import commands
from dotenv import load_dotenv
from loguru import logger

# Third: Módulos locales
import data

# ========== Configuración del bot ==========

# Cargar variables de entorno desde .env
load_dotenv()  # Carga datos importantes como el token y los dev users del archivo .dev
TOKEN = os.getenv("DISCORD_TOKEN")

# Gestor de datos del bot
data_manager = data.datos()  # Crea una instancia de la clase datos


# ========== Funciones de configuración ==========
def get_prefix(bot, message):
    """
    Obtiene el prefix dinámico para cada servidor.
    Permite usar el prefix configurado o mencionar al bot.

    Args:
            bot: Instancia del bot de Discord.
            message: Mensaje recibido.

    Returns:
            Función que acepta el prefix dinámico.
    """
    server_prefix = data_manager.get_prefix(message.guild.id)
    return commands.when_mentioned_or(*server_prefix)(bot, message)


# ========== Inicialización del bot ==========

# Configurar permisos del bot (Discord Intents)
intents = discord.Intents.default()
intents.message_content = True  # Leer contenido de mensajes
intents.members = True  # Acceder a la lista de miembros del servidor

# Crear instancia del bot
bot = commands.Bot(
    command_prefix=get_prefix,
    case_insensitive=True,
    help_command=None,
    intents=intents,
)  # pone el prefix del comando

# ========== Eventos del bot ==========


@bot.event
async def on_ready():
    """Evento que se ejecuta cuando el bot se conecta exitosamente."""
    logger.success(f"Conectado como: {bot.user.name} (ID: {bot.user.id})")
    try:
        activity = discord.Game(name="Soy carpincho, no carpintero: no arreglo nada.")
        await bot.change_presence(activity=activity, status=discord.Status.online)
        logger.info("Estado del bot actualizado.")
    except Exception as e:
        logger.error(f"Error al actualizar el estado del bot: {e}")


# ========== Carga de extensiones y ejecución del bot ==========


async def load_extensions():
    """Carga todos los módulos de comandos desde la carpeta commands/"""
    commands_dir = "./commands"
    if not os.path.exists(commands_dir):
        logger.error(f"La carpeta {commands_dir} no existe.")
        return

    # Cargar archivos .py en la carpeta principal commands/
    for filename in os.listdir(commands_dir):
        # Ignorar archivos que no son .py o empiecen con _
        if not filename.endswith(".py") or filename.startswith("_"):
            continue

        module_name = filename[:-3]  # Eliminar la extensión .py

        try:
            await bot.load_extension(f"commands.{module_name}")
            logger.success(f"Modulo cargado: {module_name}")
        except Exception as e:
            logger.error(f"Error al cargar el modulo {module_name}: {e}")

    # Cargar archivos .py en subcarpetas (music/, general/, etc.)
    for subdir_name in os.listdir(commands_dir):
        subdir_path = os.path.join(commands_dir, subdir_name)

        # Solo procesar subcarpetas, ignorar 'base' y nombres con '_'
        if (
            not os.path.isdir(subdir_path)
            or subdir_name.startswith("_")
            or subdir_name == "base"
        ):
            continue

        for filename in os.listdir(subdir_path):
            # Ignorar archivos que no son .py o empiecen con _
            if not filename.endswith(".py") or filename.startswith("_"):
                continue

            module_name = filename[:-3]  # Eliminar la extensión .py

            try:
                await bot.load_extension(f"commands.{subdir_name}.{module_name}")
                logger.success(f"Modulo cargado: {subdir_name}.{module_name}")
            except Exception as e:
                logger.error(
                    f"Error al cargar el modulo {subdir_name}.{module_name}: {e}"
                )


def validate_command_collisions(bot_instance: commands.Bot):
    """Valida que no existan colisiones entre nombres y aliases de comandos."""
    command_owner_by_token = {}
    collisions = []

    for command in bot_instance.commands:
        owner = command.qualified_name
        tokens = [command.name, *command.aliases]

        for token in tokens:
            normalized = token.lower().strip()
            if not normalized:
                continue

            previous_owner = command_owner_by_token.get(normalized)

            # Si el token ya lo usa otro comando, es una colisión real.
            if previous_owner and previous_owner != owner:
                collisions.append((normalized, previous_owner, owner))
                continue

            command_owner_by_token[normalized] = owner

    if collisions:
        formatted = ", ".join(
            [
                f"'{token}' entre '{left}' y '{right}'"
                for token, left, right in sorted(set(collisions))
            ]
        )
        raise RuntimeError(f"Se detectaron colisiones de comandos: {formatted}")


# ========== Función principal ==========


async def main():
    """Función principal para iniciar el bot."""
    if not TOKEN:
        logger.error("El token de Discord no está configurado.")
        return

    try:
        logger.error("Iniciando la carga de extensiones...")
        await load_extensions()
        validate_command_collisions(bot)

        logger.info("Iniciando el bot...")
        await bot.start(TOKEN)
    except discord.LoginFailure:
        logger.error("Fallo de inicio de sesión: Token inválido.")
    except Exception as e:
        logger.error(f"Error al iniciar el bot: {e}")


# ========== Punto de entrada ==========

if __name__ == "__main__":
    """Solo ejecuta si este archivo se ejecuta directamente."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.warning("Bot detenido por el usuario (CTRL+C).")
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
