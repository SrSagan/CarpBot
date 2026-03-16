"""
CarpBot - Bot de Discord multifuncional
Punto de entrada principal de la aplicación.
"""

# First: Librerías estándar
import asyncio
import ast
import os

# Second: Librerías de terceros
import discord
from discord.ext import commands
from dotenv import load_dotenv
from loguru import logger

# Third: Módulos locales
import data
from services.server_config_service import ServerConfigService
from utils.constants import DEFAULT_PREFIX

# ========== Configuración del bot ==========

# Cargar variables de entorno desde .env
load_dotenv()  # Carga datos importantes como el token y los dev users del archivo .dev
TOKEN = os.getenv("DISCORD_TOKEN")

# Gestor de datos del bot
data_manager = data.datos()  # Crea una instancia de la clase datos
config_service = ServerConfigService()


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
    # En DMs no hay guild; mantener prefijo por defecto + mención.
    if message.guild is None:
        return commands.when_mentioned_or(DEFAULT_PREFIX)(bot, message)

    server_prefix = config_service.get_prefix(message.guild.id)
    return commands.when_mentioned_or(server_prefix)(bot, message)


# ========== Inicialización del bot ==========

# Configurar permisos del bot (Discord Intents)
intents = discord.Intents.default()
intents.message_content = True  # Leer contenido de mensajes
intents.members = os.getenv("DISCORD_MEMBERS_INTENT", "false").lower() == "true"

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
    logger.info(f"Comandos cargados: {len(bot.commands)}")
    try:
        activity = discord.Game(name="Soy carpincho, no carpintero: no arreglo nada.")
        await bot.change_presence(activity=activity, status=discord.Status.online)
        logger.info("Estado del bot actualizado.")
    except Exception as e:
        logger.error(f"Error al actualizar el estado del bot: {e}")


@bot.event
async def on_message(message: discord.Message):
    """Diagnóstico de recepción de mensajes y procesamiento de comandos."""
    if message.author.bot:
        return

    content_preview = message.content.replace("\n", " ")[:120]
    if not message.content and message.guild is not None:
        logger.warning(
            "Mensaje recibido sin contenido en guild. "
            "Probable falta de Message Content Intent en el portal de Discord. "
            f"(guild={message.guild.id}, user={message.author.id})"
        )
    elif content_preview.startswith('"'):
        logger.info(
            f"Mensaje con prefijo detectado: '{content_preview}' "
            f"(guild={getattr(message.guild, 'id', None)}, user={message.author.id})"
        )

    await bot.process_commands(message)


@bot.event
async def on_command(ctx: commands.Context):
    """Trazas al iniciar ejecución de comandos."""
    logger.info(
        f"Ejecutando comando '{ctx.command}' "
        f"(guild={getattr(ctx.guild, 'id', None)}, user={ctx.author.id})"
    )


@bot.event
async def on_command_error(ctx: commands.Context, error: Exception):
    """Loggea errores de comandos para facilitar diagnóstico en producción."""
    logger.exception(
        f"Error ejecutando comando '{ctx.command}': {error} "
        f"(guild={getattr(ctx.guild, 'id', None)}, user={ctx.author.id})"
    )


# ========== Carga de extensiones y ejecución del bot ==========


def has_setup_function(file_path: str) -> bool:
    """Retorna True solo si el módulo define setup(bot), sync o async."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            source_code = file.read()
    except OSError as e:
        logger.error(f"No se pudo leer el archivo {file_path}: {e}")
        return False

    try:
        syntax_tree = ast.parse(source_code)
    except SyntaxError as e:
        logger.error(f"Archivo con error de sintaxis {file_path}: {e}")
        return False

    for node in syntax_tree.body:
        if (
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name == "setup"
        ):
            return True

    return False


def iter_python_modules(directory: str):
    """Itera nombres de archivo .py válidos para carga de extensiones."""
    for filename in os.listdir(directory):
        if filename.endswith(".py") and not filename.startswith("_"):
            yield filename


async def try_load_extension(module_path: str):
    """Intenta cargar una extensión y deja trazas del resultado."""
    try:
        await bot.load_extension(module_path)
        logger.success(f"Modulo cargado: {module_path.removeprefix('commands.')}")
    except Exception as e:
        logger.error(
            f"Error al cargar el modulo {module_path.removeprefix('commands.')}: {e}"
        )


async def load_extensions():
    """Carga todos los módulos de comandos desde la carpeta commands/"""

    commands_dir = "./commands"
    if not os.path.exists(commands_dir):
        logger.error(f"La carpeta {commands_dir} no existe.")
        return

    # Cargar archivos .py en la carpeta principal commands/
    for filename in iter_python_modules(commands_dir):
        file_path = os.path.join(commands_dir, filename)
        if not has_setup_function(file_path):
            logger.info(f"Modulo omitido (sin setup): {filename}")
            continue

        module_name = filename[:-3]  # Eliminar la extensión .py
        await try_load_extension(f"commands.{module_name}")

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

        for filename in iter_python_modules(subdir_path):
            file_path = os.path.join(subdir_path, filename)
            if not has_setup_function(file_path):
                logger.info(
                    f"Modulo omitido (sin setup): {subdir_name}.{filename[:-3]}"
                )
                continue

            module_name = filename[:-3]  # Eliminar la extensión .py
            await try_load_extension(f"commands.{subdir_name}.{module_name}")


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
        logger.exception(f"Error al iniciar el bot: {e}")
    finally:
        if not bot.is_closed():
            await bot.close()


# ========== Punto de entrada ==========

if __name__ == "__main__":
    """Solo ejecuta si este archivo se ejecuta directamente."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.warning("Bot detenido por el usuario (CTRL+C).")
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
