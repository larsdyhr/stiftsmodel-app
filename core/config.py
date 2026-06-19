from pathlib import Path

APP_VERSION = "v25.0"
APP_TITLE = "Nøgletal Folkekirken"
DATA_DIR = Path(__file__).resolve().parents[1] / "data"

OPHAVSTEKST = (
    "Dette program er udarbejdet af Provst Dennis Jelstrup, Falster Provsti, "
    "på baggrund af offentligt tilgængelige data. Programmet kan frit anvendes "
    "med angivelse af denne ophavsoplysning."
)

CURRENT_KBH = "Københavns Stift"
CURRENT_HEL = "Helsingør Stift"
CURRENT_ROS = "Roskilde Stift"
CURRENT_LOF = "Lolland-Falsters Stift"
BISHOP_SOUTH = "Storstrøms Stift"

OSTDANMARK_STIFTER = [CURRENT_KBH, CURRENT_HEL, CURRENT_ROS, CURRENT_LOF]

REQUIRED_DATA_COLUMNS = [
    "Stift",
    "Provsti",
    "Indbyggertal",
    "Folkekirkemedlemmer",
    "Medlemsprocent",
]

RECOMMENDED_DATA_COLUMNS = [
    "Ikke-medlemmer",
    "Befolkning 2040",
    "Befolkningsændring til 2040",
    "Befolkningsændring til 2040 %",
    "Befolkningsændring til 2040, original",
    "Befolkning 2040, original",
    "Befolkningsændring til 2040, fordelt",
    "Befolkning 2040, fordelt",
    "Befolkningsændring til 2040 %, fordelt",
    "2040-fordelingsmetode",
    "2040-fordelingsgruppe",
    "2040-fordelingsstatus",
    "2040-kilde",
    "Lokal ligning t.kr.",
    "Maks. stiftsbidrag 1 % (t.kr.)",
    "Menighedsråd",
    "Pastorater",
    "Sogne",
    "Kirker",
    "Præster inkl. LOFI",
    "Præsteårsværk inkl. LOFI",
    "Sognepræster",
    "Overenskomstansatte sognepræster",
    "Præster i alt",
    "Datakilde primær",
    "Datakilde supplerende",
]

EXPECTED_PROVSTI_COUNT = 102

OFFICIAL_STIFT_COLORS = {
    "Københavns Stift": "#1f77b4",
    "Helsingør Stift": "#2ca02c",
    "Roskilde Stift": "#ffcc00",
    "Lolland-Falsters Stift": "#d62728",
    "Fyens Stift": "#9467bd",
    "Aalborg Stift": "#17becf",
    "Viborg Stift": "#8c564b",
    "Ribe Stift": "#ff7f0e",
    "Haderslev Stift": "#e377c2",
    "Aarhus Stift": "#7f7f7f",
    BISHOP_SOUTH: "#d62728",
}

FALLBACK_PALETTE = [
    "#aec7e8", "#98df8a", "#ff9896", "#c5b0d5", "#c49c94",
    "#f7b6d2", "#c7c7c7", "#dbdb8d", "#9edae5",
]
