import streamlit as st
import pandas as pd

from core.config import (
    APP_VERSION,
    APP_TITLE,
    OPHAVSTEKST,
    CURRENT_KBH,
    CURRENT_HEL,
    CURRENT_ROS,
    CURRENT_LOF,
    BISHOP_SOUTH,
    OSTDANMARK_STIFTER,
)
from core.data_loader import load_data, source_summary
from core.filenames import export_filename
from core.map_rendering import render_map
from core.metrics import available_metrics, default_metrics, summarize_by_stift, formatted_summary
from core.pdf_export import REPORTLAB_AVAILABLE, make_pdf
from core.scenarios import current_assignment, bishops_assignment, label_mapping, visible_assignment

st.set_page_config(page_title=APP_TITLE, layout="wide")

@st.cache_data(show_spinner="Indlæser data...")
def cached_load_data():
    return load_data()

df_all, geo_all, validation_report = cached_load_data()

st.title(APP_TITLE)
st.caption(
    "Analyse- og scenarieværktøj til sammenligning af stifter og provstier. "
    "Indbygger- og medlemstal er pr. 1. januar 2026, hvor de er registreret."
)
st.markdown(f"**{OPHAVSTEKST}**")
st.caption(f"App-version: {APP_VERSION}")

if validation_report.errors:
    st.error("Kritisk dataproblem ved opstart. Se detaljer nedenfor.")
    with st.expander("Teknisk datakontrol", expanded=True):
        for error in validation_report.errors:
            st.error(error)
        for warning in validation_report.warnings:
            st.warning(warning)
        for info in validation_report.info:
            st.info(info)
    st.stop()

with st.sidebar.expander("Teknisk datakontrol", expanded=False):
    if validation_report.warnings:
        for warning in validation_report.warnings:
            st.warning(warning)
    else:
        st.success("Ingen kritiske dataproblemer.")
    for info in validation_report.info:
        st.caption(info)

st.sidebar.header("Område")
area_choice = st.sidebar.radio(
    "Vælg geografisk område",
    ["Østdanmark", "Jylland og Fyn", "Hele Danmark"],
    index=0,
)

jylland_fyn_stifter = [
    stift for stift in sorted(df_all["Stift"].dropna().astype(str).unique())
    if stift not in OSTDANMARK_STIFTER
]

if area_choice == "Østdanmark":
    area_stifts = OSTDANMARK_STIFTER
elif area_choice == "Jylland og Fyn":
    area_stifts = jylland_fyn_stifter
else:
    area_stifts = sorted(df_all["Stift"].dropna().astype(str).unique())

df = df_all[df_all["Stift"].isin(area_stifts)].copy()
geo = geo_all[geo_all["provsti"].isin(df["Provsti"].dropna().astype(str).str.strip().tolist())].copy()
provsti_liste = sorted(df["Provsti"].dropna().astype(str).str.strip().unique().tolist())

st.sidebar.header("Scenarie")

def reset_to_current():
    st.session_state.assignment = current_assignment(df)
    st.session_state.active_scenario = "Nuværende forhold"
    st.session_state.scenario_name = "Nuværende forhold"
    st.session_state.name_syd = CURRENT_LOF

# Vigtigt i landsmodellen: Når områdevalg skifter, skal baseline genberegnes.
if st.session_state.get("area_choice") != area_choice:
    st.session_state.area_choice = area_choice
    reset_to_current()

if "assignment" not in st.session_state:
    reset_to_current()
if "active_scenario" not in st.session_state:
    st.session_state.active_scenario = "Nuværende forhold"
if "scenario_name" not in st.session_state:
    st.session_state.scenario_name = "Nuværende forhold"
if "name_syd" not in st.session_state:
    st.session_state.name_syd = CURRENT_LOF

# Sørg for, at alle provstier i det valgte område altid har en baselineværdi.
for provsti, stift in current_assignment(df).items():
    if provsti not in st.session_state.assignment:
        st.session_state.assignment[provsti] = stift

if st.sidebar.button("Indlæs nuværende forhold"):
    reset_to_current()
    st.rerun()

if area_choice == "Østdanmark":
    if st.sidebar.button("Indlæs biskoppernes forslag"):
        st.session_state.assignment = bishops_assignment(df)
        st.session_state.active_scenario = "Biskoppernes forslag"
        st.session_state.scenario_name = "Biskoppernes forslag"
        st.session_state.name_syd = BISHOP_SOUTH
        st.rerun()
else:
    st.sidebar.caption("Biskoppernes Storstrøms-scenarie vises kun i Østdanmark.")

scenario_name = st.sidebar.text_input("Scenarienavn", st.session_state.scenario_name)
st.session_state.scenario_name = scenario_name

# Stiftsnavne kan kun ændres i Østdanmarksmodellen.
if area_choice == "Østdanmark":
    st.sidebar.header("Stiftsnavne")
    name_kbh = st.sidebar.text_input("Københavns stift", CURRENT_KBH)
    name_hel = st.sidebar.text_input("Helsingør stift", CURRENT_HEL)
    name_ros = st.sidebar.text_input("Roskilde stift", CURRENT_ROS)
    name_syd = st.sidebar.text_input(
        "Sydligt stift",
        key="name_syd",
    )
else:
    name_kbh = CURRENT_KBH
    name_hel = CURRENT_HEL
    name_ros = CURRENT_ROS
    name_syd = CURRENT_LOF
    st.sidebar.caption("Stiftsnavne er faste officielle navne uden for Østdanmark.")

base_stift_options = [name_kbh, name_hel, name_ros, name_syd]
extra_stifts = [
    stift for stift in sorted(df["Stift"].dropna().astype(str).unique())
    if stift not in [CURRENT_KBH, CURRENT_HEL, CURRENT_ROS, CURRENT_LOF, BISHOP_SOUTH]
]
stift_options = list(dict.fromkeys(base_stift_options + extra_stifts))

label_map = label_mapping(name_kbh, name_hel, name_ros, name_syd)
display_assignment = visible_assignment(st.session_state.assignment, label_map)

st.sidebar.header("Nøgletal")
metric_options = available_metrics(df)
selected_metrics = st.sidebar.multiselect(
    "Vælg nøgletal",
    metric_options,
    default=default_metrics(df),
)

st.sidebar.header("Kort")
show_provsti_names = st.sidebar.checkbox("Vis provstinavne på kortet", value=False)
st.sidebar.caption("Navne udelades automatisk i det tætte hovedstadsområde, hvor de ellers bliver ulæselige.")

st.subheader(f"Aktivt scenarie: {st.session_state.scenario_name}")
if area_choice == "Østdanmark":
    st.write(
        "Appen starter i **nuværende stiftsstruktur**. "
        "Biskoppernes forslag flytter Næstved, Stege-Vordingborg og Tryggevælde fra Roskilde Stift "
        "sammen med de fire nuværende Lolland-Falster-provstier til et nyt **Storstrøms Stift**."
    )
else:
    st.write(
        "Appen viser den aktuelle provsti- og stiftsstruktur for det valgte område. "
        "Nøgletal læses fra det konsoliderede v24-masterdatasæt."
    )
st.caption(
    "Bemærk: v25.0 bruger provstifordelte 2040-tal som standard. "
    "De originale Kirkeministeriet-tal er bevaret i datasættet, mens de fordelte felter er dokumenterede estimater."
)

current = current_assignment(df)
changed = [
    provsti for provsti in provsti_liste
    if st.session_state.assignment.get(provsti, current.get(provsti)) != current.get(provsti)
]
if changed:
    st.info("Ændret fra nuværende forhold: " + ", ".join(changed))
else:
    st.success("Ingen provstier er ændret i forhold til nuværende stiftsstruktur.")

st.header("Ændr stiftstilknytning")

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Hurtig ændring")
    chosen_provsti = st.selectbox("Vælg provsti", provsti_liste)
    current_stift = display_assignment.get(chosen_provsti, name_ros)
    if current_stift not in stift_options:
        current_stift = stift_options[0]
    chosen_stift = st.selectbox("Vælg stift", stift_options, index=stift_options.index(current_stift))
    if st.button("Flyt provsti"):
        st.session_state.assignment[chosen_provsti] = chosen_stift
        st.session_state.active_scenario = "Brugerdefineret scenarie"
        st.session_state.scenario_name = (
            scenario_name
            if scenario_name not in ["Nuværende forhold", "Biskoppernes forslag"]
            else "Brugerdefineret scenarie"
        )
        st.rerun()

with col2:
    st.subheader("Alle provstier")
    edit_df = pd.DataFrame({"Provsti": provsti_liste})
    edit_df["Ny stift"] = edit_df["Provsti"].map(display_assignment).fillna(name_ros)
    edit_df["Nuværende stift"] = edit_df["Provsti"].map(current)
    edit_df["Ændret"] = edit_df.apply(
        lambda row: "Ja"
        if st.session_state.assignment.get(row["Provsti"], current.get(row["Provsti"])) != current.get(row["Provsti"])
        else "",
        axis=1,
    )
    edited = st.data_editor(
        edit_df,
        hide_index=True,
        use_container_width=True,
        column_config={
            "Ny stift": st.column_config.SelectboxColumn("Ny stift", options=stift_options, required=True),
            "Nuværende stift": st.column_config.TextColumn("Nuværende stift", disabled=True),
            "Ændret": st.column_config.TextColumn("Ændret", disabled=True),
        },
    )
    new_map = dict(zip(edited["Provsti"], edited["Ny stift"]))
    if new_map != display_assignment:
        st.session_state.assignment.update(new_map)
        st.session_state.active_scenario = "Brugerdefineret scenarie"

work = df.copy()
work["Ny stift"] = work["Provsti"].map(
    {provsti: label_map.get(stift, stift) for provsti, stift in st.session_state.assignment.items()}
).fillna(name_ros)

st.header("Nøgletal")
st.caption(
    "Forkortede kolonneoverskrifter for en mere kompakt oversigt. "
    "Stiftsbidrag og lokal ligning angives i t.kr. Procenter beregnes på aggregerede summer. "
    "2040-tal er som standard provstifordelte estimater fra v25.0."
)

summary = summarize_by_stift(work, selected_metrics)
show_display = formatted_summary(summary)
st.dataframe(show_display, hide_index=True, use_container_width=True)

st.header("Kort")
fig, map_png = render_map(geo, work, area_choice, show_provsti_names, name_kbh, name_hel, name_ros, name_syd)
st.pyplot(fig, use_container_width=True)

csv = work.to_csv(index=False).encode("utf-8-sig")
st.download_button(
    "Download provstiliste som CSV",
    data=csv,
    file_name=export_filename("stiftsmodel_provstier", "csv", area_choice, st.session_state.get("scenario_name")),
    mime="text/csv",
)

st.download_button(
    "Download kort som PNG",
    data=map_png,
    file_name=export_filename("stiftsmodel_kort", "png", area_choice, st.session_state.get("scenario_name")),
    mime="image/png",
)

st.header("Eksport")

if REPORTLAB_AVAILABLE:
    pdf_data = make_pdf(
        APP_TITLE,
        st.session_state.scenario_name,
        OPHAVSTEKST,
        show_display,
        map_png,
        changed,
    )
    st.download_button(
        "Download scenarie som PDF",
        data=pdf_data,
        file_name=export_filename("Folkekirken_Scenarie", "pdf", area_choice, st.session_state.get("scenario_name")),
        mime="application/pdf",
    )
else:
    st.warning(
        "PDF-eksport kræver Python-pakken reportlab. "
        "Appen virker stadig. Installer med: python -m pip install reportlab"
    )

with st.expander("Datakilder og teknisk dokumentation", expanded=False):
    st.markdown(
        """
        **Aktive app-filer**
        - `data/provstidata.xlsx`
        - `data/provstier.geojson`

        **Master- og dokumentationsfiler**
        - `data/provstidata_master_v25.xlsx`
        - `data/2040_fordelingsdokumentation.xlsx`

        **Bilag og historik**
        - `data/bilag/`
        """
    )
    sources = source_summary(df)
    if not sources.empty:
        st.dataframe(sources, hide_index=True, use_container_width=True)
    else:
        st.info("Der er ikke registreret kildekolonner i det aktive datasæt.")

st.markdown("---")
st.markdown(f"**{OPHAVSTEKST}**")
st.caption(f"App-version: {APP_VERSION}")
