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
