import re

def safe_filename_part(value: str) -> str:
    """Returner et filnavnsegnet tekststykke."""
    value = str(value or "").strip()
    value = value.replace("æ", "ae").replace("ø", "oe").replace("å", "aa")
    value = value.replace("Æ", "Ae").replace("Ø", "Oe").replace("Å", "Aa")
    value = re.sub(r"[^A-Za-z0-9_-]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value or "uden_navn"

def area_export_slug(area_choice: str) -> str:
    mapping = {
        "Østdanmark": "Oestdanmark",
        "Jylland og Fyn": "Jylland_Fyn",
        "Hele Danmark": "Hele_Danmark",
    }
    return mapping.get(area_choice, safe_filename_part(area_choice))

def export_filename(prefix: str, extension: str, area_choice: str | None = None, scenario_name: str | None = None) -> str:
    parts = [safe_filename_part(prefix)]
    if area_choice:
        parts.append(area_export_slug(area_choice))
    if scenario_name:
        parts.append(safe_filename_part(scenario_name))
    return "_".join(parts) + "." + extension.lstrip(".")
