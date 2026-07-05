import time
import datetime


def format_time(seconds: int) -> str:
    """
    Convierte segundos a formato HH:MM:SS

    Args:
            seconds (int): Número de segundos.

    Returns:
            String formateado como "HH:MM:SS".
    """
    s = seconds % 60
    m = (
        (seconds - s) // 60 % 60
    )  # Se resta los segundos ya contados y se divide entre 60 para obtener minutos
    h = seconds // 3600  # Se divide entre 3600 para obtener horas

    return f"{int(h):02d}:{int(m):02d}:{int(s):02d}"


def parse_time_to_seconds(time_str: str) -> float:
    """
    Convierte un string en formato HH:MM:SS a segundos.

    Args:
            time_str (str): Tiempo en formato "HH:MM:SS" o "HH:MM:SS,microseconds".

    Returns:
            float: Número de segundos totales.
    """
    # Remover microsegundos si existen
    clean_time = time_str.split(",")[0]

    x = time.strptime(clean_time, "%H:%M:%S")
    return datetime.timedelta(
        hours=x.tm_hour, minutes=x.tm_min, seconds=x.tm_sec
    ).total_seconds()
