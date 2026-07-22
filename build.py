# /// script
# requires-python = ">=3.10"
# dependencies = ["geopandas>=1.0", "pyarrow>=15"]
# ///
"""Construit le jeu « Quartiers de Marseille » et l'exporte en cinq formats.

    uv run build.py                 # génère dist/ (télécharge ses sources)
    uv run build.py --verifier      # + revalide le préfixe cadastral géométriquement
    uv run build.py --help

Sans uv :  pip install -r requirements.txt && python build.py

---------------------------------------------------------------------------
CE QUE LE SCRIPT PRODUIT

Les 111 quartiers de Marseille (découpage du décret 46-2285 du 18 octobre 1946),
avec leur géométrie, leurs identifiants officiels et leur préfixe de section
cadastral :

    prefixe    "801"                         préfixe de section cadastral (DGFiP)
    code_qua   "1320101"                      code officiel du grand quartier INSEE
    num_qua    1                              rang du quartier dans l'arrondissement
    nom        "Belsunce"                     nom officiel, en graphie accentuée
    DEPCO      "13201"                         code INSEE de l'arrondissement
    NOM_CO     "Marseille 1er Arrondissement"  libellé de l'arrondissement

Tout est reconstruit depuis des sources vivantes et faisant autorité — IRIS-GE
de l'IGN, tableau de Wikipédia, cadastre Etalab. Aucune dépendance à une édition
figée du jeu.

---------------------------------------------------------------------------
POURQUOI LE PRÉFIXE CADASTRAL COMPTE

C'est la clé qui relie un quartier au cadastre. Une parcelle marseillaise a
pour identifiant `132018010A0070` = arrondissement (13201) + PRÉFIXE (801) +
section (0A) + numéro (0070). Sans table de correspondance, ce 801 reste un
code opaque ; avec, il se lit « Belsunce ».

Il compte d'autant plus qu'à Marseille le préfixe est *discriminant* : une même
section peut exister sous plusieurs préfixes, si bien qu'une référence comme
« 13201 0A 0070 » désigne cinq parcelles différentes, une par quartier.

---------------------------------------------------------------------------
LA GÉOMÉTRIE VIENT DES IRIS, AGRÉGÉS

C'est la méthode d'origine du jeu, en R : les quartiers de Marseille sont
exactement les GRANDS QUARTIERS de l'INSEE, et le code d'un grand quartier est
le préfixe à 7 caractères du code IRIS. Agréger les IRIS par ce préfixe
reconstruit les quartiers — géométrie ET code.

    393 IRIS  →  group by code_iris[:7]  →  111 quartiers

`code_qua`, `DEPCO`, `num_qua` et `NOM_CO` sont donc PORTÉS PAR LA DONNÉE, pas
déduits d'une position dans un fichier. La géométrie suit le millésime courant
des IRIS de l'IGN. Source : IRIS-GE, la version GRANDE ÉCHELLE — `contours_iris`,
généralisé, ne porte qu'un quart des sommets à découpage identique.

---------------------------------------------------------------------------
D'OÙ VIENT LE PRÉFIXE — ET COMMENT IL EST VÉRIFIÉ

Le préfixe cadastral, lui, n'est écrit dans aucune source : il se déduit du rang
du quartier, `préfixe = 800 + rang des code_qua triés`. La déduction porte sur la
numérotation officielle de l'INSEE, stable et lisible dans la donnée. Deux
contrôles la confirment.

1. RECOUVREMENT GÉOMÉTRIQUE (--verifier) — chaque quartier est confronté à la
   couche `prefixes_sections` de l'export Etalab du cadastre : 111 / 111
   rattachements confirmés, recouvrement médian 0,99.

   Le minimum, 0,08, est le préfixe 831 (les îles) : il pointe bien vers le même
   quartier, mais le préfixe *cadastral* déborde le *quartier*. Ses trois parts
   couvrent le Frioul, l'archipel de Riou et l'île de Planier, alors que Riou
   relève des Goudes et que seul le Frioul constitue un quartier.

2. ORDRE ALPHABÉTIQUE — l'ordre est alphabétique dans 15 arrondissements sur
   16 ; l'exception, le 9ᵉ, est confirmée géométriquement. La numérotation INSEE
   suit donc l'ordre cadastral, et non un tri alphabétique.

Une fois `prefixe` publié, cette déduction n'a plus lieu d'être : les
réutilisateurs lisent la colonne.

---------------------------------------------------------------------------
D'OÙ VIENNENT LES NOMS

Du wikitexte de fr.wikipedia.org/wiki/Quartiers_de_Marseille, PARSÉ et non
recopié — une liste de 111 lignes transcrite à la main se dégrade. Chaque nom
est joint à son quartier par le CODE (`code_qua`), pas par un appariement de
libellés ni par un rang : la jointure est donc exacte. On exige qu'elle soit
bijective — 111 codes IRIS ↔ 111 codes Wikipédia — sinon le script s'arrête,
ce qui détecte aussi bien un doublon dans le tableau qu'un changement de
millésime IRIS.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import json
import re
import sys
import urllib.request
import zipfile
from pathlib import Path

RACINE = Path(__file__).parent
CACHE = RACINE / ".cache"
DIST = RACINE / "dist"

WIKIPEDIA = ("https://fr.wikipedia.org/w/api.php?action=parse"
             "&page=Quartiers%20de%20Marseille&prop=wikitext&format=json&formatversion=2")
# IRIS de l'IGN (Géoplateforme), interrogés commune par commune : le fichier
# national pèse plusieurs centaines de Mo, le WFS filtré quelques dizaines de Ko.
# Champs utiles : code_iris (9 car.), code_insee, nom_commune.
#
# On prend IRIS-GE, la version GRANDE ÉCHELLE, et non `contours_iris`, qui est
# généralisé : à découpage identique, celui-ci ne porte qu'un quart des sommets.
IRIS = ("https://data.geopf.fr/wfs/ows?SERVICE=WFS&VERSION=2.0.0&REQUEST=GetFeature"
        "&TYPENAMES=STATISTICALUNITS.IRISGE:iris_ge&OUTPUTFORMAT=application/json"
        "&CQL_FILTER=code_insee%3D%27{commune}%27")
# Couche des préfixes de section de l'export Etalab du cadastre, par commune.
CADASTRE = ("https://cadastre.data.gouv.fr/data/etalab-cadastre/latest/geojson/communes/13/"
            "{commune}/cadastre-{commune}-prefixes_sections.json.gz")

ARRONDISSEMENTS = [f"132{n:02d}" for n in range(1, 17)]
NB_QUARTIERS = 111
PREFIXE_INITIAL = 801  # le rang 1 (Belsunce) porte le préfixe 801

# Le tableau Wikipédia donne, par ligne, un code <code>13 2XX YY</code> — dont on
# capture l'arrondissement (2XX) ET le rang (YY) pour reformer le code à 7
# chiffres — puis une cellule de nom (lien [[Cible|Libellé]] ou [[Libellé]]).
LIGNE_WIKI = re.compile(
    r"<code>13\s*(2\d{2})\s*(\d{2})</code>.*?\n\|(?:data-sort-value=\"[^\"]*\"\|)?\s*(.+?)\n",
    re.DOTALL,
)


# --------------------------------------------------------------------------
# Téléchargement (avec cache disque, pour ne pas retélécharger à chaque essai)
# --------------------------------------------------------------------------
# L'API Wikimedia rejette (403) le User-Agent par défaut d'urllib : sa politique
# impose un agent descriptif, identifiant l'outil et un moyen de contact.
AGENT = ("quartiers-marseille-build/1.0 "
         "(https://github.com/joelgombin/quartiers-marseille)")


def telecharger(url: str, nom_cache: str) -> bytes:
    chemin = CACHE / nom_cache
    if chemin.exists():
        return chemin.read_bytes()
    CACHE.mkdir(exist_ok=True)
    print(f"  ↓ {nom_cache}", file=sys.stderr)
    requete = urllib.request.Request(url, headers={"User-Agent": AGENT})
    with urllib.request.urlopen(requete, timeout=300) as reponse:
        contenu = reponse.read()
    chemin.write_bytes(contenu)
    return contenu


# --------------------------------------------------------------------------
# Noms officiels (Wikipédia), indexés par code de quartier
# --------------------------------------------------------------------------
def libelle_wiki(cellule: str) -> str:
    """Libellé affiché d'une cellule wikitexte ([[Cible|Libellé]] → Libellé)."""
    texte = cellule.strip()
    if lien := re.search(r"\[\[([^\]]+)\]\]", texte):
        cible = lien.group(1)
        texte = cible.split("|")[-1] if "|" in cible else cible
    return re.sub(r"''+", "", texte).strip()


def noms_officiels() -> dict[str, str]:
    """{code_qua: nom officiel}, depuis le tableau de Wikipédia.

    La clé est le code à 7 chiffres du grand quartier, qui joint exactement le
    `code_qua` reconstruit depuis les IRIS. Un code en double rendrait la
    jointure ambiguë : on s'arrête plutôt que de choisir au hasard.
    """
    brut = json.loads(telecharger(WIKIPEDIA, "wikipedia.json"))["parse"]["wikitext"]
    noms: dict[str, str] = {}
    doublons = []
    for arrondissement, rang, cellule in LIGNE_WIKI.findall(brut):
        code = f"13{arrondissement}{rang}"
        if code in noms:
            doublons.append(code)
        noms[code] = libelle_wiki(cellule)
    if doublons:
        raise SystemExit(
            f"Codes de quartier en double dans le tableau Wikipédia : {sorted(set(doublons))}. "
            "La jointure par code serait ambiguë — corriger la source avant de publier."
        )
    return noms


# --------------------------------------------------------------------------
# Reconstruction des quartiers à partir des IRIS
# --------------------------------------------------------------------------
def agreger_iris():
    """Reconstruit les 111 quartiers en agrégeant les IRIS de Marseille.

    Un quartier de Marseille est un GRAND QUARTIER au sens de l'INSEE, dont le
    code est le préfixe à 7 caractères du code IRIS : agréger les IRIS par ce
    préfixe redonne les quartiers, géométrie et code compris.
    """
    import geopandas
    import pandas

    couches = []
    for commune in ARRONDISSEMENTS:
        brut = json.loads(telecharger(IRIS.format(commune=commune), f"iris-{commune}.json"))
        couches.append(geopandas.GeoDataFrame.from_features(brut["features"], crs="EPSG:4326"))
    iris = pandas.concat(couches, ignore_index=True)

    iris["code_qua"] = iris["code_iris"].str[:7]
    # dissolve = union des géométries par quartier. Les IRIS étant jointifs,
    # l'union redonne un contour propre.
    quartiers = iris.dissolve(by="code_qua", as_index=False)[["code_qua", "geometry"]]
    quartiers = quartiers.sort_values("code_qua", ignore_index=True)

    if len(quartiers) != NB_QUARTIERS:
        raise SystemExit(
            f"{len(iris)} IRIS agrégés en {len(quartiers)} quartiers au lieu de {NB_QUARTIERS} : "
            "le découpage IRIS a changé, revérifier avant de publier."
        )
    # nom_commune est constant pour tous les IRIS d'un même arrondissement.
    nom_commune = dict(zip(iris["code_insee"], iris["nom_commune"]))
    quartiers["DEPCO"] = quartiers["code_qua"].str[:5]
    quartiers["num_qua"] = quartiers["code_qua"].str[5:].astype(int)
    quartiers["NOM_CO"] = quartiers["DEPCO"].map(nom_commune)
    # Le préfixe cadastral suit le rang du quartier dans la numérotation INSEE.
    quartiers["prefixe"] = [str(PREFIXE_INITIAL + i) for i in range(len(quartiers))]
    print(f"  {len(iris)} IRIS → {len(quartiers)} quartiers")
    return quartiers


# --------------------------------------------------------------------------
# Jointure des noms
# --------------------------------------------------------------------------
def nommer(quartiers, noms: dict[str, str]) -> list[dict]:
    """Joint le nom officiel à chaque quartier par son code, renvoie la table.

    Jointure EXACTE (code_qua ↔ code Wikipédia) : pas d'appariement approximatif.
    On exige qu'elle soit totale, sinon on s'arrête — un code sans nom signale un
    tableau Wikipédia incomplet ou un millésime IRIS différent.
    """
    manquants = sorted(set(quartiers["code_qua"]) - set(noms))
    if manquants:
        raise SystemExit(
            f"Aucun nom officiel pour {manquants} : le tableau Wikipédia ne couvre pas "
            "tous les quartiers (tableau modifié, ou millésime IRIS différent)."
        )
    return [
        {
            "prefixe": ligne.prefixe,
            "code_qua": ligne.code_qua,
            "arrondissement": ligne.DEPCO,
            "num_qua": ligne.num_qua,
            "nom": noms[ligne.code_qua],
        }
        for ligne in quartiers.itertuples()
    ]


# --------------------------------------------------------------------------
# Vérification géométrique (optionnelle)
# --------------------------------------------------------------------------
def geometrie_sure(geometrie: dict):
    """Charge une géométrie GeoJSON en élidant les anneaux dégénérés.

    L'export cadastre contient quelques anneaux de moins de 4 sommets, que
    shapely refuse net.
    """
    from shapely.geometry import shape

    def anneaux(polygone):
        return [a for a in polygone if len(a) >= 4]

    if geometrie["type"] == "Polygon":
        geometrie = {"type": "Polygon", "coordinates": anneaux(geometrie["coordinates"])}
    elif geometrie["type"] == "MultiPolygon":
        parts = [anneaux(p) for p in geometrie["coordinates"]]
        geometrie = {"type": "MultiPolygon", "coordinates": [p for p in parts if p]}
    return shape(geometrie).buffer(0)


def verifier_prefixes(couche, table: list[dict]) -> int:
    """Confronte chaque préfixe déduit au cadastre. Renvoie le nombre d'écarts."""
    from shapely.strtree import STRtree

    print("\n▸ Vérification géométrique contre l'export cadastre Etalab")
    quartiers = list(couche.geometry)
    index = STRtree(quartiers)

    recouvrements, ecarts = [], []
    for commune in ARRONDISSEMENTS:
        brut = gzip.decompress(telecharger(CADASTRE.format(commune=commune), f"cadastre-{commune}.json.gz"))
        for entite in json.loads(brut)["features"]:
            prefixe = entite["properties"]["prefixe"]
            if prefixe == "000":
                continue
            polygone = geometrie_sure(entite["geometry"])
            meilleur, aire = None, 0.0
            for candidat in index.query(polygone):
                intersection = polygone.intersection(quartiers[candidat]).area
                if intersection > aire:
                    meilleur, aire = int(candidat), intersection
            part = aire / polygone.area if polygone.area else 0.0
            attendu = next(
                (i for i, p in enumerate(table)
                 if p["prefixe"] == prefixe and p["arrondissement"] == commune), None
            )
            if meilleur is None or meilleur != attendu:
                ecarts.append((commune, prefixe, part,
                               table[meilleur]["nom"] if meilleur is not None else "—"))
            else:
                recouvrements.append(part)

    recouvrements.sort()
    if recouvrements:
        mediane = recouvrements[len(recouvrements) // 2]
        print(f"  {len(recouvrements)} préfixes confirmés · recouvrement médian {mediane:.3f} "
              f"(min {recouvrements[0]:.3f})")
    for commune, prefixe, part, trouve in ecarts:
        print(f"  ⚠ {commune} préfixe {prefixe} : meilleur recouvrement {part:.3f} vers « {trouve} »")
    if not ecarts:
        print("  ✓ aucun écart")
    return len(ecarts)


# --------------------------------------------------------------------------
# Exports
# --------------------------------------------------------------------------
def exporter_shapefile(couche, base) -> None:
    """Shapefile UTF-8, livré en dossier ET en archive zip.

    Le format impose des contraintes que les autres n'ont pas :
      - noms de champs limités à 10 caractères. Les six colonnes tiennent
        (`code_qua` est la plus longue, 8) : aucune troncature, donc des noms
        identiques d'un format à l'autre. Une colonne plus longue ajoutée un
        jour serait silencieusement tronquée — d'où le contrôle ci-dessous.
      - encodage à déclarer : sans fichier .cpg en UTF-8, « Les Îles » et
        « Opéra » ressortent illisibles chez le réutilisateur.
    """
    trop_longues = [c for c in couche.columns if c != "geometry" and len(c) > 10]
    if trop_longues:
        raise SystemExit(
            f"Colonnes trop longues pour le format shapefile (max 10 car.) : {trop_longues}. "
            "Elles seraient tronquées en silence — renommer avant d'exporter."
        )

    dossier = DIST / "shapefile"
    dossier.mkdir(exist_ok=True)
    chemin = dossier / "quartiers-marseille.shp"
    couche.to_file(chemin, driver="ESRI Shapefile", encoding="utf-8")

    # Archive : un shapefile ne se transmet qu'accompagné de ses fichiers
    # satellites, d'où le zip — c'est la forme attendue sur data.gouv.fr.
    # Horodatage figé pour que l'archive ne change pas d'une exécution à l'autre.
    with zipfile.ZipFile(f"{base}-shp.zip", "w", zipfile.ZIP_DEFLATED) as archive:
        for fichier in sorted(dossier.iterdir()):
            info = zipfile.ZipInfo(fichier.name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, fichier.read_bytes())


def exporter(couche, table: list[dict]) -> None:
    DIST.mkdir(exist_ok=True)
    base = DIST / "quartiers-marseille"

    couche = couche.assign(nom=[ligne["nom"] for ligne in table])
    # Ordre de colonnes stable : identifiants, puis libellés, puis géométrie.
    colonnes = ["prefixe", "code_qua", "num_qua", "nom", "DEPCO", "NOM_CO"]
    couche = couche[colonnes + ["geometry"]]

    couche.to_file(f"{base}.geojson", driver="GeoJSON")
    couche.to_file(f"{base}.gpkg", layer="quartiers", driver="GPKG")
    exporter_shapefile(couche, base)
    # GeoParquet : géométrie en WKB + métadonnées « geo » conformes à la spec,
    # écrites par geopandas. Compression zstd, nettement plus efficace que snappy
    # sur des polygones.
    #
    # Sans bbox de couverture (`write_covering_bbox`) : sur 111 polygones, cet
    # index de filtrage spatial n'apporte rien, et geopandas l'écrit sous une clé
    # `covering` de la spec 1.1 tout en déclarant le fichier en 1.0.0 — une
    # incohérence qu'on évite plutôt que de la publier.
    couche.to_parquet(f"{base}.parquet", compression="zstd")

    # Table de relecture sans géométrie (pratique pour un diff, un tri, un import).
    with open(f"{base}.csv", "w", encoding="utf-8", newline="") as fichier:
        redacteur = csv.DictWriter(fichier, fieldnames=list(table[0]))
        redacteur.writeheader()
        redacteur.writerows(table)

    for chemin in sorted(DIST.rglob("*")):
        if chemin.is_file():
            nom = chemin.relative_to(DIST)
            print(f"  {str(nom):<34} {chemin.stat().st_size / 1024:>8.0f} Ko")


def main() -> int:
    analyseur = argparse.ArgumentParser(
        description="Construit le jeu « Quartiers de Marseille » (IRIS + Wikipédia + cadastre).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    analyseur.add_argument(
        "--verifier", action="store_true",
        help="revalide le préfixe cadastral contre l'export Etalab (télécharge ~16 fichiers)",
    )
    arguments = analyseur.parse_args()

    print("▸ Reconstruction des quartiers depuis les IRIS")
    quartiers = agreger_iris()

    print("\n▸ Noms officiels (Wikipédia, joints par code)")
    table = nommer(quartiers, noms_officiels())
    print(f"  {len(table)}/{NB_QUARTIERS} quartiers nommés")

    ecarts = verifier_prefixes(quartiers, table) if arguments.verifier else 0

    print("\n▸ Exports")
    exporter(quartiers, table)
    return 1 if ecarts else 0


if __name__ == "__main__":
    raise SystemExit(main())
