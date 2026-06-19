import io
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from shapely import affinity
import pandas as pd
from .config import OFFICIAL_STIFT_COLORS, FALLBACK_PALETTE, BISHOP_SOUTH

def build_color_map(stift_names, name_kbh, name_hel, name_ros, name_syd):
    colors = {
        name_kbh: OFFICIAL_STIFT_COLORS["Københavns Stift"],
        name_hel: OFFICIAL_STIFT_COLORS["Helsingør Stift"],
        name_ros: OFFICIAL_STIFT_COLORS["Roskilde Stift"],
        name_syd: OFFICIAL_STIFT_COLORS["Lolland-Falsters Stift"],
        BISHOP_SOUTH: OFFICIAL_STIFT_COLORS[BISHOP_SOUTH],
    }
    for i, stift_name in enumerate(sorted([str(x) for x in stift_names if str(x) != "nan"])):
        if stift_name not in colors:
            colors[stift_name] = OFFICIAL_STIFT_COLORS.get(stift_name, FALLBACK_PALETTE[i % len(FALLBACK_PALETTE)])
    return colors

def render_map(geo, work, area_choice, show_provsti_names, name_kbh, name_hel, name_ros, name_syd):
    map_geo = geo.merge(work[["Provsti", "Ny stift"]], left_on="provsti", right_on="Provsti", how="left")
    colors = build_color_map(map_geo["Ny stift"].dropna().astype(str).unique(), name_kbh, name_hel, name_ros, name_syd)

    if area_choice == "Østdanmark":
        main = map_geo[map_geo["provsti"] != "Bornholms Provsti"].copy()
        bornholm = map_geo[map_geo["provsti"] == "Bornholms Provsti"].copy()
    else:
        main = map_geo.copy()
        bornholm = map_geo.iloc[0:0].copy()

    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_facecolor("#dceff7")

    minx, miny, maxx, maxy = main.total_bounds
    width = maxx - minx
    height = maxy - miny

    bornholm_inset = bornholm.copy()
    if len(bornholm_inset):
        bxmin, bymin, bxmax, bymax = bornholm_inset.total_bounds
        target_xmin = maxx + 0.02 * width
        target_ymin = miny - 0.13 * height
        bornholm_inset["geometry"] = bornholm_inset["geometry"].apply(
            lambda geom: affinity.translate(geom, xoff=target_xmin - bxmin, yoff=target_ymin - bymin)
        )
        main = main.copy()
        main["__inset"] = False
        bornholm_inset["__inset"] = True
        plot_geo = pd.concat([main, bornholm_inset], ignore_index=True)
    else:
        plot_geo = main.copy()
        plot_geo["__inset"] = False

    for stift_name, group in plot_geo.groupby("Ny stift", dropna=False):
        color = colors.get(str(stift_name), "#cccccc")
        group.plot(ax=ax, color=color, edgecolor="white", linewidth=0.7)

    plot_geo.boundary.plot(ax=ax, color="#444444", linewidth=0.3)

    if show_provsti_names:
        for _, row in plot_geo.iterrows():
            name = row.get("provsti", "")
            if area_choice == "Østdanmark" and name in [
                "Amagerbro Provsti",
                "Bispebjerg-Brønshøj Provsti",
                "Frederiksberg Provsti",
                "Holmens og Østerbro Provsti",
                "Nørrebro Provsti",
                "Valby-Vanløse Provsti",
                "Vor Frue-Vesterbro Provsti",
            ]:
                continue
            try:
                point = row.geometry.representative_point()
                ax.text(point.x, point.y, str(name).replace(" Provsti", ""), fontsize=7, ha="center", va="center")
            except Exception:
                pass

    handles = [
        mpatches.Patch(color=color, label=label)
        for label, color in sorted(colors.items())
        if label in set(plot_geo["Ny stift"].dropna().astype(str))
    ]
    if handles:
        ax.legend(handles=handles, loc="lower left", fontsize=8, frameon=True)

    ax.set_aspect("equal")
    ax.set_axis_off()
    ax.set_title("Stiftsmodel - provstier fordelt på stifter", fontsize=14)

    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", dpi=200, bbox_inches="tight")
    buffer.seek(0)

    return fig, buffer.getvalue()
