from .config import CURRENT_KBH, CURRENT_HEL, CURRENT_ROS, CURRENT_LOF, BISHOP_SOUTH

# Aktuel østlig stiftsstruktur. Vestdanske provstier falder tilbage til Excel-kolonnen "Stift".
CURRENT_ASSIGNMENT = {
    # København, 9 provstier
    "Amagerbro Provsti": CURRENT_KBH,
    "Amagerland Provsti": CURRENT_KBH,
    "Bispebjerg-Brønshøj Provsti": CURRENT_KBH,
    "Bornholms Provsti": CURRENT_KBH,
    "Frederiksberg Provsti": CURRENT_KBH,
    "Holmens og Østerbro Provsti": CURRENT_KBH,
    "Nørrebro Provsti": CURRENT_KBH,
    "Valby-Vanløse Provsti": CURRENT_KBH,
    "Vor Frue-Vesterbro Provsti": CURRENT_KBH,

    # Helsingør, 13 provstier
    "Ballerup-Furesø Provsti": CURRENT_HEL,
    "Fredensborg Provsti": CURRENT_HEL,
    "Frederikssund Provsti": CURRENT_HEL,
    "Frederiksværk Provsti": CURRENT_HEL,
    "Gentofte Provsti": CURRENT_HEL,
    "Gladsaxe-Herlev Provsti": CURRENT_HEL,
    "Glostrup Provsti": CURRENT_HEL,
    "Helsingør Domprovsti": CURRENT_HEL,
    "Hillerød Provsti": CURRENT_HEL,
    "Høje Taastrup Provsti": CURRENT_HEL,
    "Kongens Lyngby Provsti": CURRENT_HEL,
    "Rudersdal Provsti": CURRENT_HEL,
    "Rødovre-Hvidovre Provsti": CURRENT_HEL,

    # Roskilde, 12 provstier
    "Greve-Solrød Provsti": CURRENT_ROS,
    "Holbæk Provsti": CURRENT_ROS,
    "Kalundborg Provsti": CURRENT_ROS,
    "Køge Provsti": CURRENT_ROS,
    "Lejre Provsti": CURRENT_ROS,
    "Næstved Provsti": CURRENT_ROS,
    "Odsherred Provsti": CURRENT_ROS,
    "Ringsted-Sorø Provsti": CURRENT_ROS,
    "Roskilde Domprovsti": CURRENT_ROS,
    "Slagelse Provsti": CURRENT_ROS,
    "Stege-Vordingborg Provsti": CURRENT_ROS,
    "Tryggevælde Provsti": CURRENT_ROS,

    # Lolland-Falster, 4 provstier
    "Falster Provsti": CURRENT_LOF,
    "Lolland Østre Provsti": CURRENT_LOF,
    "Lolland Vestre Provsti": CURRENT_LOF,
    "Maribo Domprovsti": CURRENT_LOF,
}

def current_assignment(df):
    """Returner baseline for de provstier, som er synlige i det valgte område."""
    assignment = {}
    for _, row in df.iterrows():
        provsti = str(row["Provsti"]).strip()
        stift = str(row["Stift"]).strip()
        assignment[provsti] = CURRENT_ASSIGNMENT.get(provsti, stift)
    return assignment

def bishops_assignment(df):
    """Returner biskoppernes Storstrøms-scenarie for Østdanmark."""
    assignment = current_assignment(df)
    for provsti in ["Næstved Provsti", "Stege-Vordingborg Provsti", "Tryggevælde Provsti"]:
        assignment[provsti] = BISHOP_SOUTH
    for provsti in ["Falster Provsti", "Lolland Østre Provsti", "Lolland Vestre Provsti", "Maribo Domprovsti"]:
        assignment[provsti] = BISHOP_SOUTH
    return assignment

def label_mapping(name_kbh, name_hel, name_ros, name_syd):
    return {
        CURRENT_KBH: name_kbh,
        CURRENT_HEL: name_hel,
        CURRENT_ROS: name_ros,
        CURRENT_LOF: name_syd,
        BISHOP_SOUTH: name_syd,
    }

def visible_assignment(assignment, label_map):
    return {provsti: label_map.get(stift, stift) for provsti, stift in assignment.items()}
