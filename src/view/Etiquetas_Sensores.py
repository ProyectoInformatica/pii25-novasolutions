_COLOR_BASE = "#00ff00"
_COLOR_SIN_DATOS = "#888888"


def interpretar_calidad_aire(valor: float) -> tuple[str, str]:

    if valor < 800:
        return "Buena",            "#00ff00"
    elif valor < 1400:
        return "Regular",          "#aaff00"
    elif valor < 2200:
        return "Mala",             "#ffaa00"
    elif valor < 3000:
        return "Muy mala",         "#ff6600"
    else:
        return "Muy desfavorable", "#ff0000"


def formatear_medida(tipo_sensor: str, valor: float | None) -> tuple[str, str]:

    if valor is None:
        return "Sin datos", _COLOR_SIN_DATOS

    if tipo_sensor == "airQuality":
        return interpretar_calidad_aire(valor)

    unidades = {
        "temperature": "°C",
        "smoke":       " ADC",
        "light":       " ADC",
        "distance":    " cm",
    }
    sufijo = unidades.get(tipo_sensor, "")
    return f"{valor:.1f}{sufijo}", _COLOR_BASE