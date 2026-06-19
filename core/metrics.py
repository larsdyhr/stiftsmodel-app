import pandas as pd

METRIC_MAP = {
    "Indbyggertal": "Indbyggertal",
    "Folkekirkemedlemmer": "Folkekirkemedlemmer",
    "Ikke-medlemmer": "Ikke-medlemmer",
    "Medlemsprocent": "Medlemsprocent",

    # v25.0: standardvisning bruger provstifordelte 2040-estimater.
    "Befolkning 2040 (fordelt)": "Befolkning 2040, fordelt",
    "Befolkningsændring til 2040 (fordelt)": "Befolkningsændring til 2040, fordelt",
    "Befolkningsændring til 2040 % (fordelt)": "Befolkningsændring til 2040 %, fordelt",

    # Originale felter bevares til kontrol og sporbarhed.
    "Befolkning 2040 (original)": "Befolkning 2040, original",
    "Befolkningsændring til 2040 (original)": "Befolkningsændring til 2040, original",
    "Befolkning 2040 (v24-kolonne)": "Befolkning 2040",
    "Befolkningsændring til 2040 (v24-kolonne)": "Befolkningsændring til 2040",

    "Lokal ligning t.kr.": "Lokal ligning t.kr.",
    "Maks. stiftsbidrag 1 % (t.kr.)": "Maks. stiftsbidrag 1 % (t.kr.)",
    "Menighedsråd": "Menighedsråd",
    "Pastorater": "Pastorater",
    "Sogne": "Sogne",
    "Kirker": "Kirker",
    "Præster inkl. LOFI": "Præster inkl. LOFI",
    "Præsteårsværk inkl. LOFI": "Præsteårsværk inkl. LOFI",
    "Præster i alt": "Præster i alt",
    "Sognepræster": "Sognepræster",
    "Overenskomstansatte sognepræster": "Overenskomstansatte sognepræster",
}

DEFAULT_METRICS = [
    "Indbyggertal",
    "Folkekirkemedlemmer",
    "Ikke-medlemmer",
    "Medlemsprocent",
    "Befolkning 2040 (fordelt)",
    "Befolkningsændring til 2040 (fordelt)",
    "Præster i alt",
    "Menighedsråd",
    "Pastorater",
    "Sogne",
    "Kirker",
    "Maks. stiftsbidrag 1 % (t.kr.)",
]

DISPLAY_COLUMN_NAMES = {
    "Ny stift": "Stift",
    "Provstier": "Provstier",
    "Indbyggertal": "Indbyggere",
    "Folkekirkemedlemmer": "Medlemmer",
    "Ikke-medlemmer": "Ikke-medl.",
    "Medlemsprocent": "Medlems-%",
    "Befolkning 2040, fordelt": "Bef. 2040",
    "Befolkningsændring til 2040, fordelt": "Bef.ændr.",
    "Befolkningsændring til 2040 %, fordelt": "Bef.ændr. %",
    "Befolkning 2040, original": "Bef. 2040 orig.",
    "Befolkningsændring til 2040, original": "Bef.ændr. orig.",
    "Befolkning 2040": "Bef. 2040 v24",
    "Befolkningsændring til 2040": "Bef.ændr. v24",
    "Lokal ligning t.kr.": "Lokal ligning",
    "Maks. stiftsbidrag 1 % (t.kr.)": "Stiftsbid. (max)",
    "Menighedsråd": "MR",
    "Pastorater": "Pastorater",
    "Sogne": "Sogne",
    "Kirker": "Kirker",
    "Præster inkl. LOFI": "Præster LOFI",
    "Præsteårsværk inkl. LOFI": "Årsv. LOFI",
    "Præster i alt": "Præster",
    "Sognepræster": "Sognepr.",
    "Overenskomstansatte sognepræster": "OK-præster",
}

PERCENT_COLUMNS = {
    "Medlemsprocent",
    "Befolkningsændring til 2040 %",
    "Befolkningsændring til 2040 %, fordelt",
}

NUMBER_COLUMNS = set(METRIC_MAP.values()) - PERCENT_COLUMNS

def available_metrics(df: pd.DataFrame) -> list[str]:
    return [name for name, col in METRIC_MAP.items() if col in df.columns]

def default_metrics(df: pd.DataFrame) -> list[str]:
    available = set(available_metrics(df))
    return [name for name in DEFAULT_METRICS if name in available]

def summarize_by_stift(work: pd.DataFrame, selected_metrics: list[str]) -> pd.DataFrame:
    """Summer udvalgte nøgletal pr. ny stift.

    Procenttal beregnes som aggregerede rater:
    - Medlemsprocent = folkekirkemedlemmer / indbyggertal
    - Befolkningsændring til 2040 % (fordelt) = fordelt ændring / indbyggertal
    - Befolkningsændring til 2040 % (v24) = v24-ændring / indbyggertal
    """
    rows = []
    for stift_name, group in work.groupby("Ny stift", dropna=False):
        row = {"Ny stift": stift_name, "Provstier": int(group["Provsti"].count())}
        for metric in selected_metrics:
            col = METRIC_MAP[metric]
            if col == "Medlemsprocent":
                indb = pd.to_numeric(group.get("Indbyggertal"), errors="coerce").sum(skipna=True)
                medl = pd.to_numeric(group.get("Folkekirkemedlemmer"), errors="coerce").sum(skipna=True)
                row[col] = medl / indb if indb else pd.NA
            elif col == "Befolkningsændring til 2040 %, fordelt":
                indb = pd.to_numeric(group.get("Indbyggertal"), errors="coerce").sum(skipna=True)
                change = pd.to_numeric(group.get("Befolkningsændring til 2040, fordelt"), errors="coerce").sum(skipna=True)
                row[col] = change / indb if indb else pd.NA
            elif col == "Befolkningsændring til 2040 %":
                indb = pd.to_numeric(group.get("Indbyggertal"), errors="coerce").sum(skipna=True)
                change = pd.to_numeric(group.get("Befolkningsændring til 2040"), errors="coerce").sum(skipna=True)
                row[col] = change / indb if indb else pd.NA
            elif col in group.columns:
                vals = pd.to_numeric(group[col], errors="coerce")
                row[col] = vals.sum(skipna=True) if vals.notna().any() else pd.NA
        rows.append(row)

    summary = pd.DataFrame(rows)
    ordered_cols = ["Ny stift", "Provstier"]
    for metric in selected_metrics:
        col = METRIC_MAP[metric]
        if col in summary.columns and col not in ordered_cols:
            ordered_cols.append(col)
    return summary[ordered_cols]

def format_number(value, col: str) -> str:
    if pd.isna(value):
        return ""
    if col in PERCENT_COLUMNS:
        return f"{float(value) * 100:.1f} %"
    if col in NUMBER_COLUMNS or col == "Provstier":
        if col in {"Lokal ligning t.kr.", "Maks. stiftsbidrag 1 % (t.kr.)", "Præsteårsværk inkl. LOFI"}:
            return f"{float(value):,.1f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"{float(value):,.0f}".replace(",", ".")
    return str(value)

def formatted_summary(summary: pd.DataFrame) -> pd.DataFrame:
    show = summary.copy()
    for col in show.columns:
        if col != "Ny stift":
            show[col] = [format_number(v, col) for v in show[col]]
    return show.rename(columns=DISPLAY_COLUMN_NAMES)
