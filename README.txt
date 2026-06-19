Nøgletal Folkekirken
Stiftsmodellen - version v25.0

AKTUEL BASELINE
v25.0 bygger på v24.1 og indfører en ny dokumenteret metode for 2040-fremskrivninger på provstiniveau.

NYT I v25.0
- Kommunebaserede befolkningsfremskrivninger fra Kirkeministeriets ark "Befolkning" er fordelt til provstier.
- Fordelingen sker proportionalt efter provstiernes aktive indbyggertal 2026.
- Originale v24-tal er bevaret i særskilte originalkolonner.
- Nye standardfelter:
  * Befolkningsændring til 2040, fordelt
  * Befolkning 2040, fordelt
  * Befolkningsændring til 2040 %, fordelt
  * 2040-fordelingsmetode
  * 2040-fordelingsgruppe
  * 2040-fordelingsstatus
  * 2040-kilde
- Appen bruger de fordelte 2040-tal som standard.
- Datakontrol er flyttet ud af hovedvisningen og vises kun tydeligt ved kritiske problemer.
- Datakilder er flyttet til en diskret sektion nederst i appen.

METODE FOR 2040-FORDELING
Kirkeministeriets fremskrivning foreligger i flere tilfælde på kommuneniveau og dækker ét eller flere provstier.
I v25.0 fordeles kommunens vækst sådan:

Fordelt ændring for provsti =
kommunal befolkningsændring x provstiets indbyggertal 2026 /
samlet indbyggertal 2026 for provstierne i fordelingsgruppen.

Afrunding sker pr. kommunerække, så den fordelte vækst summerer til Kirkeministeriets kommunale vækst.

FORBEHOLD
Metoden er et estimat. Den er særligt relevant for kommuner med flere provstier og for tværkommunale provstier.
Grene Provsti er markeret som tværkommunalt estimat, fordi provstiet ligger i både Billund Kommune og Vejle Kommune.
Originale kildetal er bevaret, så beregningen kan kontrolleres.

AKTIVE FILER
- app.py
- core/
- data/provstidata.xlsx
- data/provstidata_master_v25.xlsx
- data/provstier.geojson
- data/2040_fordelingsdokumentation.xlsx

HISTORIK
- data/bilag/gamle_data/provstidata_master_v24.xlsx
- data/bilag/kilder/Kopi af Tabel vedr. stifter og provstier slut torsdag.xlsx

INSTALLATION
1. Pak zip-filen ud.
2. Installer afhængigheder:
   python -m pip install -r requirements.txt
3. Start appen:
   streamlit run app.py

VERSIONERING
- v24.x: nye funktioner uden ændret datamodel
- v24.x.y: fejlrettelser
- v25.0: større ændring af datamodel/analysemetode
