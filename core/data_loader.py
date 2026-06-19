import pandas as pd
import geopandas as gpd
from .config import DATA_DIR
from .validation import validate_data

def load_data(data_dir=DATA_DIR):
    """Indlæs aktivt provstidataark og GeoJSON samt valideringsrapport."""
    excel_path = data_dir / "provstidata.xlsx"
    geo_path = data_dir / "provstier.geojson"

    df = pd.read_excel(excel_path, sheet_name="Provstidata")
    df["Provsti"] = df["Provsti"].astype(str).str.strip()
    df["Stift"] = df["Stift"].astype(str).str.strip()

    geo = gpd.read_file(geo_path)
    geo["provsti"] = geo["provsti"].astype(str).str.strip()

    report = validate_data(df, geo)
    return df, geo, report

def source_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Returner en kompakt oversigt over registrerede datakilder."""
    rows = []
    for col in ["Datakilde primær", "Datakilde supplerende", "2040-kilde"]:
        if col in df.columns:
            counts = df[col].fillna("Ikke angivet").astype(str).value_counts(dropna=False)
            for source, count in counts.items():
                rows.append({"Kildetype": col, "Kilde": source, "Provstier": int(count)})
    return pd.DataFrame(rows)
