# /// script
# requires-python = ">=3.10"
# dependencies = ["geopandas>=1.0", "pyarrow>=15"]
# ///
"""Enrichit le jeu « Quartiers de Marseille » et l'exporte en quatre formats.

    uv run build.py                 # génère dist/ (télécharge ses sources)
    uv run build.py --verifier      # + revalide le préfixe cadastral géométriquement
    uv run build.py --help

Sans uv :  pip install -r requirements.txt && python build.py

---------------------------------------------------------------------------
CE QUE LE SCRIPT AJOUTE

Le jeu source décrit les 111 quartiers de Marseille (découpage du décret
46-2285 du 18 octobre 1946) mais ne porte aucun identifiant : ni le code
officiel du quartier, ni le préfixe de section cadastral. On les ajoute, ainsi
que le nom en graphie officielle.

    prefixe    "801"        préfixe de section cadastral (DGFiP)
    code_qua   "1320101"    code officiel du quartier : arrondissement + rang
    num_qua    1            rang du quartier dans son arrondissement
    nom        "Belsunce"   nom officiel, accentué, en casse de titre

Les champs d'origine (DEPCO, NOM_CO, NOM_QUA) et les géométries sont conservés
tels quels : l'enrichissement est purement additif.

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
D'OÙ VIENT LE PRÉFIXE — ET COMMENT IL A ÉTÉ VÉRIFIÉ

Il n'est écrit nulle part dans le jeu source : il se déduit de l'ORDRE des
entités, `préfixe = 800 + rang`. Fonder une donnée publiée sur un ordre de
fichier serait imprudent sans contrôle, d'où deux vérifications indépendantes.

1. RECOUVREMENT GÉOMÉTRIQUE (--verifier) — chaque polygone de quartier est
   confronté à la couche `prefixes_sections` de l'export Etalab du cadastre :
   111 / 111 rattachements confirmés, recouvrement médian 0,99.

   Le minimum, 0,08, est le préfixe 831 (les îles) : il pointe bien vers le même
   quartier, mais le préfixe *cadastral* déborde le *quartier*. Ses trois parts
   couvrent le Frioul, l'archipel de Riou et l'île de Planier, alors que Riou
   relève des Goudes et que seul le Frioul constitue un quartier.

2. ORDRE ALPHABÉTIQUE — l'ordre est alphabétique dans 15 arrondissements sur
   16. L'exception est le 9ᵉ, où Sormiou (852) précède Sainte-Marguerite (853),
   tous deux confirmés géométriquement (0,95 et 0,99). L'ordre du fichier suit
   donc la numérotation cadastrale réelle, et non un tri alphabétique.

Une fois `prefixe` publié, cette déduction n'a plus lieu d'être : les
réutilisateurs lisent la colonne.

---------------------------------------------------------------------------
D'OÙ VIENNENT LES NOMS

Du wikitexte de fr.wikipedia.org/wiki/Quartiers_de_Marseille, PARSÉ et non
recopié — une liste de 111 lignes transcrite à la main se dégrade.

Un nom officiel est retenu s'il correspond au NOM_QUA du jeu source une fois
accents, casse, traits d'union et articles neutralisés — un appariement ne peut
donc pas glisser d'un quartier à l'autre, il ne fait que restituer la graphie.

Restent cinq quartiers dont les deux libellés diffèrent vraiment (coquilles du
jeu source, et une entité mal étiquetée). Ils sont corrigés, mais via la table
CORRECTIONS, qui les énumère un à un avec les deux libellés attendus. Une
divergence qui n'y figure pas — parce qu'une des sources aurait changé — est
signalée sans être appliquée : le libellé source est alors conservé. Voir
ANOMALIES.md.

L'appariement se fait sur le RANG dans l'arrondissement, et non sur le code
publié par Wikipédia. Ce choix a été dicté par une coquille (Sainte-Marthe
codée 13 214 06, déjà attribué à Saint-Joseph), depuis corrigée en amont ; il
est conservé parce qu'il ne dépend pas de l'exactitude d'un champ éditable.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import json
import re
import sys
import unicodedata
import urllib.request
from pathlib import Path

RACINE = Path(__file__).parent
CACHE = RACINE / ".cache"
DIST = RACINE / "dist"

# Ressource GeoJSON publiée sur data.gouv.fr (jeu « Quartiers de Marseille »).
SOURCE = ("https://static.data.gouv.fr/resources/quartiers-de-marseille-1/"
          "20210308-145904/quartiers-marseille.geojson")
WIKIPEDIA = ("https://fr.wikipedia.org/w/api.php?action=parse"
             "&page=Quartiers%20de%20Marseille&prop=wikitext&format=json&formatversion=2")
# Couche des préfixes de section de l'export Etalab du cadastre, par commune.
CADASTRE = ("https://cadastre.data.gouv.fr/data/etalab-cadastre/latest/geojson/communes/13/"
            "{commune}/cadastre-{commune}-prefixes_sections.json.gz")

ARRONDISSEMENTS = [f"132{n:02d}" for n in range(1, 17)]
NB_QUARTIERS = 111
PREFIXE_INITIAL = 801  # le rang 1 (Belsunce) porte le préfixe 801

# Le tableau Wikipédia donne, par ligne, un code <code>13 2XX YY</code> puis une
# cellule de nom, sous forme de lien [[Cible|Libellé]] ou [[Libellé]].
LIGNE_WIKI = re.compile(
    r"<code>13\s*(2\d{2})\s*\d{2}</code>.*?\n\|(?:data-sort-value=\"[^\"]*\"\|)?\s*(.+?)\n",
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
# Noms officiels
# --------------------------------------------------------------------------
def libelle_wiki(cellule: str) -> str:
    """Libellé affiché d'une cellule wikitexte ([[Cible|Libellé]] → Libellé)."""
    texte = cellule.strip()
    if lien := re.search(r"\[\[([^\]]+)\]\]", texte):
        cible = lien.group(1)
        texte = cible.split("|")[-1] if "|" in cible else cible
    return re.sub(r"''+", "", texte).strip()


def noms_officiels() -> dict[str, list[str]]:
    """{code arrondissement: [noms dans l'ordre du tableau]}."""
    brut = json.loads(telecharger(WIKIPEDIA, "wikipedia.json"))["parse"]["wikitext"]
    par_arrondissement: dict[str, list[str]] = {}
    for arrondissement, cellule in LIGNE_WIKI.findall(brut):
        par_arrondissement.setdefault(f"13{arrondissement}", []).append(libelle_wiki(cellule))
    return par_arrondissement


def cle_comparaison(nom: str) -> str:
    """Forme neutralisée : sans accents, sans ponctuation, sans article initial.

    Sert UNIQUEMENT à vérifier que deux graphies désignent le même quartier
    avant de substituer l'une à l'autre — jamais à apparier des quartiers entre
    eux, ce qui se fait par le rang.
    """
    sans_accents = unicodedata.normalize("NFD", nom).encode("ascii", "ignore").decode()
    normalise = re.sub(r"[^A-Za-z0-9 ]", " ", sans_accents).upper()
    normalise = re.sub(r"\s+", " ", normalise).strip()
    return re.sub(r"^(LES|LE|LA|L|DU|DE)\s+", "", normalise)


# --------------------------------------------------------------------------
# Corrections de libellé, examinées une à une
# --------------------------------------------------------------------------
# Cas où le libellé du jeu source et la graphie officielle désignent le même
# quartier sans se ressembler assez pour être appariés automatiquement. Chacun a
# été vérifié individuellement (cf. ANOMALIES.md) et est inscrit ici de façon
# EXPLICITE : c'est ce qui permet d'appliquer la correction sans renoncer au
# garde-fou. Toute divergence qui n'est PAS dans cette table — parce que le
# tableau Wikipédia aurait été réordonné, par exemple — reste signalée et NON
# appliquée, plutôt que de renommer un quartier en silence.
#
#   préfixe: (libellé source attendu, graphie officielle attendue)
CORRECTIONS = {
    "813": ("SAINT MAURON", "Saint-Mauront"),      # coquille : t final manquant
    "814": ("LA VILETTE", "La Villette"),          # coquille : double l
    "831": ("ENDOUME", "Les Îles"),                # 2e entité « ENDOUME » = quartier des Îles
    "845": ("VIELLE CHAPELLE", "Vieille Chapelle"),  # coquille : Vielle → Vieille
    "898": ("LES BORELS", "Borel"),                # variante d'usage, alignée sur l'officiel
}


def correction_applicable(prefixe: str, nom_source: str, nom_officiel: str | None) -> bool:
    """Vrai si cette divergence précise a été examinée et validée.

    On exige que les DEUX libellés soient ceux attendus : si l'une des sources
    change, la correction ne s'applique plus et le cas repasse en alerte.
    """
    attendu = CORRECTIONS.get(prefixe)
    return attendu is not None and attendu == (nom_source, nom_officiel)


# --------------------------------------------------------------------------
# Enrichissement
# --------------------------------------------------------------------------
def enrichir(geojson: dict, officiels: dict[str, list[str]]) -> list[dict]:
    """Ajoute les 4 propriétés en place et renvoie la table de relecture."""
    entites = geojson["features"]
    if len(entites) != NB_QUARTIERS:
        raise SystemExit(
            f"Le jeu source compte {len(entites)} entités au lieu de {NB_QUARTIERS} : "
            "la correspondance rang → préfixe n'est plus fiable, revérifier d'abord."
        )

    table, rang_dans_arrondissement = [], {}
    for rang, entite in enumerate(entites):
        proprietes = entite["properties"]
        arrondissement = proprietes["DEPCO"]
        numero = rang_dans_arrondissement[arrondissement] = (
            rang_dans_arrondissement.get(arrondissement, 0) + 1
        )
        prefixe = str(PREFIXE_INITIAL + rang)
        nom_source = proprietes["NOM_QUA"]

        liste = officiels.get(arrondissement, [])
        nom_officiel = liste[numero - 1] if numero <= len(liste) else None
        concordant = bool(nom_officiel) and cle_comparaison(nom_officiel) == cle_comparaison(nom_source)
        corrige = not concordant and correction_applicable(prefixe, nom_source, nom_officiel)
        # Le nom officiel s'applique quand les deux libellés se correspondent, ou
        # quand la divergence figure dans CORRECTIONS. Sinon on garde le libellé
        # source : une divergence inconnue est un signal, pas une correction.
        nom = nom_officiel if (concordant or corrige) else nom_source.title()

        proprietes.update({
            "prefixe": prefixe,
            "num_qua": numero,
            "code_qua": f"{arrondissement}{numero:02d}",
            "nom": nom,
        })
        table.append({
            "prefixe": prefixe,
            "code_qua": f"{arrondissement}{numero:02d}",
            "arrondissement": arrondissement,
            "num_qua": numero,
            "nom": nom,
            "nom_source": nom_source,
            "correction": "OUI" if corrige else "",
            "alerte": "" if (concordant or corrige) else "DIVERGENCE NON EXAMINÉE",
        })
    return table


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


def verifier_prefixes(geojson: dict) -> int:
    """Confronte chaque préfixe déduit au cadastre. Renvoie le nombre d'écarts."""
    from shapely.strtree import STRtree

    print("\n▸ Vérification géométrique contre l'export cadastre Etalab")
    quartiers = [geometrie_sure(e["geometry"]) for e in geojson["features"]]
    proprietes = [e["properties"] for e in geojson["features"]]
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
                (i for i, p in enumerate(proprietes)
                 if p["prefixe"] == prefixe and p["DEPCO"] == commune), None
            )
            if meilleur is None or meilleur != attendu:
                ecarts.append((commune, prefixe, part,
                               proprietes[meilleur]["nom"] if meilleur is not None else "—"))
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
def exporter(geojson: dict, table: list[dict]) -> None:
    import geopandas

    DIST.mkdir(exist_ok=True)
    base = DIST / "quartiers-marseille"

    couche = geopandas.GeoDataFrame.from_features(geojson["features"], crs="EPSG:4326")
    # Ordre de colonnes stable : identifiants, puis libellés, puis géométrie.
    colonnes = ["prefixe", "code_qua", "num_qua", "nom", "DEPCO", "NOM_CO", "NOM_QUA"]
    couche = couche[colonnes + ["geometry"]]

    couche.to_file(f"{base}.geojson", driver="GeoJSON")
    couche.to_file(f"{base}.gpkg", layer="quartiers", driver="GPKG")
    # GeoParquet : géométrie en WKB + métadonnées « geo » conformes à la spec,
    # écrites par geopandas. Compression zstd, nettement plus efficace que snappy
    # sur des polygones.
    #
    # Sans bbox de couverture (`write_covering_bbox`) : sur 111 polygones, cet
    # index de filtrage spatial n'apporte rien, et geopandas l'écrit sous une clé
    # `covering` de la spec 1.1 tout en déclarant le fichier en 1.0.0 — une
    # incohérence qu'on évite plutôt que de la publier.
    couche.to_parquet(f"{base}.parquet", compression="zstd")

    with open(f"{base}.csv", "w", encoding="utf-8", newline="") as fichier:
        redacteur = csv.DictWriter(fichier, fieldnames=list(table[0]))
        redacteur.writeheader()
        redacteur.writerows(table)

    for chemin in sorted(DIST.iterdir()):
        print(f"  {chemin.name:<34} {chemin.stat().st_size / 1024:>8.0f} Ko")


def main() -> int:
    analyseur = argparse.ArgumentParser(
        description="Enrichit le jeu « Quartiers de Marseille » (identifiants + noms officiels).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    analyseur.add_argument(
        "--source", metavar="CHEMIN",
        help="GeoJSON source local (par défaut : la ressource publiée sur data.gouv.fr)",
    )
    analyseur.add_argument(
        "--verifier", action="store_true",
        help="revalide le préfixe cadastral contre l'export Etalab (télécharge ~16 fichiers)",
    )
    arguments = analyseur.parse_args()

    print("▸ Sources")
    brut = (Path(arguments.source).read_bytes() if arguments.source
            else telecharger(SOURCE, "quartiers-marseille.geojson"))
    geojson = json.loads(brut)
    officiels = noms_officiels()

    print("\n▸ Enrichissement")
    table = enrichir(geojson, officiels)
    corrections = [ligne for ligne in table if ligne["correction"]]
    alertes = [ligne for ligne in table if ligne["alerte"]]
    print(f"  {len(table)} quartiers · {len(table) - len(corrections)} noms appariés · "
          f"{len(corrections)} corrigés")
    for ligne in corrections:
        print(f"    {ligne['prefixe']} ({ligne['code_qua']}) : "
              f"« {ligne['nom_source']} » → « {ligne['nom']} »")
    for ligne in alertes:
        print(f"  ⚠ préfixe {ligne['prefixe']} ({ligne['code_qua']}) : « {ligne['nom_source']} » "
              f"diverge du nom officiel sans figurer dans CORRECTIONS — libellé source conservé.")

    ecarts = verifier_prefixes(geojson) if arguments.verifier else 0

    print("\n▸ Exports")
    exporter(geojson, table)
    return 1 if ecarts else 0


if __name__ == "__main__":
    raise SystemExit(main())
