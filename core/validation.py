from dataclasses import dataclass, field
import pandas as pd
import geopandas as gpd
from .config import REQUIRED_DATA_COLUMNS, RECOMMENDED_DATA_COLUMNS, EXPECTED_PROVSTI_COUNT

@dataclass
class ValidationReport:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    info: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors

def _clean_names(values) -> set[str]:
    return {str(v).strip() for v in values if pd.notna(v) and str(v).strip()}

def validate_data(df: pd.DataFrame, geo: gpd.GeoDataFrame) -> ValidationReport:
    report = ValidationReport()

    missing_required = [c for c in REQUIRED_DATA_COLUMNS if c not in df.columns]
    if missing_required:
        report.errors.append("Mangler påkrævede kolonner i provstidata.xlsx: " + ", ".join(missing_required))

    missing_recommended = [c for c in RECOMMENDED_DATA_COLUMNS if c not in df.columns]
    if missing_recommended:
        report.warnings.append("Mangler anbefalede v24-kolonner: " + ", ".join(missing_recommended))

    if "Provsti" in df.columns:
        provstier = df["Provsti"].dropna().astype(str).str.strip()
        duplicate_provstier = sorted(provstier[provstier.duplicated()].unique().tolist())
        if duplicate_provstier:
            report.errors.append("Dubletter i Provsti-kolonnen: " + ", ".join(duplicate_provstier))

        count = provstier.nunique()
        if count == EXPECTED_PROVSTI_COUNT:
            report.info.append(f"Provstidata indeholder {count} unikke provstier.")
        else:
            report.warnings.append(f"Provstidata indeholder {count} unikke provstier; forventet {EXPECTED_PROVSTI_COUNT}.")

    if "provsti" not in geo.columns:
        report.errors.append("GeoJSON mangler kolonnen 'provsti'.")
    else:
        geo_provstier = geo["provsti"].dropna().astype(str).str.strip()
        geo_duplicates = sorted(geo_provstier[geo_provstier.duplicated()].unique().tolist())
        if geo_duplicates:
            report.errors.append("Dubletter i GeoJSON-provstier: " + ", ".join(geo_duplicates))

        geo_count = geo_provstier.nunique()
        if geo_count == EXPECTED_PROVSTI_COUNT:
            report.info.append(f"GeoJSON indeholder {geo_count} unikke provstier.")
        else:
            report.warnings.append(f"GeoJSON indeholder {geo_count} unikke provstier; forventet {EXPECTED_PROVSTI_COUNT}.")

    if "Provsti" in df.columns and "provsti" in geo.columns:
        data_names = _clean_names(df["Provsti"])
        geo_names = _clean_names(geo["provsti"])
        missing_in_geo = sorted(data_names - geo_names)
        missing_in_data = sorted(geo_names - data_names)

        if missing_in_geo:
            report.errors.append("Provstier i Excel, men ikke i GeoJSON: " + ", ".join(missing_in_geo))
        if missing_in_data:
            report.errors.append("Provstier i GeoJSON, men ikke i Excel: " + ", ".join(missing_in_data))
        if not missing_in_geo and not missing_in_data:
            report.info.append("Excel og GeoJSON matcher på provstinavne.")

    text_columns = {
        "Stift",
        "Provsti",
        "Datakilde primær",
        "Datakilde supplerende",
        "2040-fordelingsmetode",
        "2040-fordelingsgruppe",
        "2040-fordelingsstatus",
        "2040-kilde",
    }
    numeric_candidates = [
        c for c in REQUIRED_DATA_COLUMNS + RECOMMENDED_DATA_COLUMNS
        if c not in text_columns and c in df.columns
    ]
    for col in numeric_candidates:
        converted = pd.to_numeric(df[col], errors="coerce")
        if converted.notna().sum() == 0:
            report.warnings.append(f"Kolonnen '{col}' har ingen numeriske værdier.")
        elif df[col].notna().sum() != converted.notna().sum():
            report.warnings.append(f"Kolonnen '{col}' indeholder værdier, der ikke kan tolkes numerisk.")


    # v25.0: 2040-fordelte felter skal være komplette for alle provstier.
    if "Befolkning 2040, fordelt" in df.columns:
        missing_2040 = df[df["Befolkning 2040, fordelt"].isna()]["Provsti"].astype(str).tolist()
        if missing_2040:
            report.errors.append("Mangler fordelt Befolkning 2040 for: " + ", ".join(missing_2040))
        else:
            report.info.append("Fordelte 2040-tal findes for alle provstier.")

    if "Befolkningsændring til 2040, fordelt" in df.columns:
        total_change = pd.to_numeric(df["Befolkningsændring til 2040, fordelt"], errors="coerce").sum(skipna=True)
        report.info.append(f"Samlet fordelt befolkningsændring til 2040: {int(round(total_change)):,}".replace(",", "."))

    return report
