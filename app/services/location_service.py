import math

# Velocidad máxima considerada "plausible" entre dos marcas consecutivas (km/h).
# Superarla implica un desplazamiento físicamente poco realista.
MAX_PLAUSIBLE_SPEED_KMH = 200

# Ignora diferencias pequeñas (ruido normal del GPS) por debajo de este umbral.
MIN_DISTANCE_TO_CHECK_KM = 5


def calculate_distance_km(lat1, lon1, lat2, lon2):
    """Distancia entre dos coordenadas usando la fórmula de Haversine (en km)."""
    R = 6371  # Radio de la Tierra en km

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def is_unusual_location(last_mark, latitude, longitude, current_timestamp):
    """
    Compara la nueva marca contra la última marca del usuario.
    Retorna (True, distancia_km) si el desplazamiento implica una
    velocidad poco realista; de lo contrario (False, None).
    """
    if last_mark is None:
        return False, None

    distance = calculate_distance_km(
        last_mark.latitude, last_mark.longitude, float(latitude), float(longitude)
    )

    if distance < MIN_DISTANCE_TO_CHECK_KM:
        return False, None

    current = current_timestamp
    last_timestamp = last_mark.timestamp

    # MySQL no conserva la zona horaria al guardar un DateTime, así que al
    # leerlo de vuelta viene "naive" (sin tzinfo), aunque se guardó en hora
    # de Costa Rica. Normalizamos ambos a "naive" para poder restarlos,
    # ya que representan la misma zona horaria de todas formas.
    if current.tzinfo is not None:
        current = current.replace(tzinfo=None)
    if last_timestamp.tzinfo is not None:
        last_timestamp = last_timestamp.replace(tzinfo=None)

    elapsed_hours = (current - last_timestamp).total_seconds() / 3600

    if elapsed_hours <= 0:
        elapsed_hours = 1 / 60  # evita división por cero (marca casi instantánea)

    implied_speed = distance / elapsed_hours

    if implied_speed > MAX_PLAUSIBLE_SPEED_KMH:
        return True, round(distance, 1)

    return False, None