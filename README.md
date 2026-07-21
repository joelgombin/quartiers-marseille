# Quartiers de Marseille

Les **111 quartiers de Marseille** au sens du décret 46-2285 du 18 octobre 1946,
avec leurs identifiants officiels et leur **préfixe de section cadastral**.

Diffusé sur data.gouv.fr : [Quartiers de Marseille](https://www.data.gouv.fr/datasets/quartiers-de-marseille-1).

## Ce que contient le jeu

| Champ | Exemple | Description |
|---|---|---|
| `prefixe` | `"801"` | **Préfixe de section cadastral** (DGFiP) |
| `code_qua` | `"1320101"` | Code officiel du quartier : arrondissement + rang |
| `num_qua` | `1` | Rang du quartier dans son arrondissement |
| `nom` | `"Belsunce"` | Nom officiel, accentué, en casse de titre |
| `DEPCO` | `"13201"` | Code INSEE de l'arrondissement |
| `NOM_CO` | `"Marseille 1er Arrondissemen"` | Libellé d'arrondissement *(champ d'origine)* |
| `NOM_QUA` | `"BELSUNCE"` | Libellé d'origine, en capitales *(champ d'origine)* |

Les champs d'origine et les géométries sont conservés tels quels :
l'enrichissement est **purement additif**.

## Formats

| Fichier | Taille | Usage |
|---|---|---|
| `dist/quartiers-marseille.parquet` | ~750 Ko | **GeoParquet** 1.0.0, WKB, zstd — analyse, DuckDB, Python |
| `dist/quartiers-marseille.gpkg` | ~1,1 Mo | GeoPackage — QGIS, ArcGIS |
| `dist/quartiers-marseille.geojson` | ~2,5 Mo | GeoJSON — web, échange |
| `dist/quartiers-marseille-shp.zip` | ~650 Ko | Shapefile zippé — SIG hérités |
| `dist/shapefile/` | ~1 Mo | Les mêmes, décompressés |
| `dist/quartiers-marseille.csv` | ~6 Ko | Table de relecture, sans géométrie |

Coordonnées en **EPSG:4326** (WGS 84).

Deux particularités du **shapefile**, inhérentes au format et sans perte
d'information :

- l'encodage est déclaré en UTF-8 par un fichier `.cpg`, sans quoi « Les Îles »
  et « Opéra » ressortent illisibles ;
- les entités d'un seul tenant y sont des `Polygon` là où les autres formats
  portent des `MultiPolygon` — le format ne distingue pas les deux. Géométries
  topologiquement identiques, mêmes sommets, mêmes aires.

Les noms de champs tiennent tous dans les 10 caractères du format : ils sont
identiques d'un format à l'autre, sans troncature.

```python
import geopandas
quartiers = geopandas.read_parquet("dist/quartiers-marseille.parquet")
quartiers.loc[quartiers["prefixe"] == "801", "nom"]   # → Belsunce
```

```sql
-- DuckDB, sans téléchargement préalable
INSTALL spatial; LOAD spatial;
SELECT prefixe, nom FROM 'dist/quartiers-marseille.parquet' WHERE DEPCO = '13201';
```

## À quoi sert le préfixe cadastral

C'est la clé qui relie un quartier au cadastre. Une parcelle marseillaise a pour
identifiant `132018010A0070`, soit :

```
13201    801      0A       0070
arrond.  PRÉFIXE  section  numéro
```

Sans table de correspondance, ce `801` reste un code opaque ; avec, il se lit
« Belsunce ».

Il compte d'autant plus qu'à Marseille le préfixe est **discriminant** : une même
section existe sous plusieurs préfixes, si bien qu'une référence comme
« 13201 0A 0070 » désigne **cinq parcelles distinctes**, une par quartier. C'est
le préfixe, et lui seul, qui les départage.

## Comment le préfixe a été établi

Il n'est écrit nulle part dans le jeu d'origine : il se déduit de l'**ordre** des
entités, `préfixe = 800 + rang`. Fonder une donnée publiée sur un ordre de
fichier appelle une vérification, d'où deux contrôles indépendants.

**Recouvrement géométrique** — chaque polygone de quartier est confronté à la
couche `prefixes_sections` de l'export Etalab du cadastre :

- **111 / 111** rattachements confirmés ;
- recouvrement **médian 0,99**.

Le minimum, 0,08, concerne le préfixe 831 (les îles) : il désigne bien le même
quartier, mais le préfixe *cadastral* déborde le *quartier* — il couvre aussi
l'archipel de Riou et l'île de Planier, qui n'en font pas partie.

**Ordre alphabétique** — vérifié dans 15 arrondissements sur 16. L'exception, le
9ᵉ, est confirmée géométriquement : l'ordre du fichier suit la numérotation
cadastrale réelle, pas un tri appliqué après coup.

Reproduire : `uv run build.py --verifier`.

## Régénérer

Le script est autoportant : il télécharge ses sources et déclare ses
dépendances ([PEP 723](https://peps.python.org/pep-0723/)).

```sh
uv run build.py               # génère dist/
uv run build.py --verifier    # + revalide le préfixe contre le cadastre
uv run build.py --help
```

Sans [uv](https://docs.astral.sh/uv/) :

```sh
pip install -r requirements.txt
python build.py
```

Les sources téléchargées sont mises en cache dans `.cache/` (non versionné) ;
supprimer ce dossier force un rafraîchissement.

## Sources

| Source | Apport |
|---|---|
| [Quartiers de Marseille](https://www.data.gouv.fr/datasets/quartiers-de-marseille-1) | géométries et découpage |
| [Export Etalab du cadastre](https://cadastre.data.gouv.fr/datasets/cadastre-etalab) | vérification des préfixes |
| [Quartiers de Marseille (Wikipédia)](https://fr.wikipedia.org/wiki/Quartiers_de_Marseille) | noms en graphie officielle |

## Licence

**[Licence Ouverte 2.0](https://www.etalab.gouv.fr/licence-ouverte-open-licence)**
(Etalab) — réutilisation libre, y compris commerciale, sous réserve de mentionner
la paternité et la date de dernière mise à jour. Texte intégral :
[`LICENSE.md`](LICENSE.md).

Les données dérivent de sources publiques sous la même licence ou compatibles
(cf. *Sources*).

## Reproductibilité

À sources inchangées, tous les fichiers sont reproductibles **bit à bit** —
CSV, GeoJSON, GeoParquet, shapefile et son archive, dont l'horodatage est figé
pour cette raison — **sauf le GeoPackage**. SQLite y inscrit des identifiants
propres à chaque écriture, si bien que le fichier change à chaque exécution alors
que son contenu, attributs et géométries, reste rigoureusement identique. Un diff
sur ce seul fichier n'indique donc pas un changement de donnée.

## Corrections de libellé

Cinq quartiers portaient dans le jeu d'origine un libellé qui s'écartait de la
graphie officielle — trois coquilles, une variante d'usage, et une entité mal
étiquetée (le rang 31, nommé `ENDOUME`, désigne en réalité le quartier des
**Îles**). Le champ `nom` suit la graphie officielle ; `NOM_QUA` conserve le
libellé d'origine.

| Préfixe | `NOM_QUA` | `nom` |
|---|---|---|
| 813 | `SAINT MAURON` | Saint-Mauront |
| 814 | `LA VILETTE` | La Villette |
| 831 | `ENDOUME` | Les Îles |
| 845 | `VIELLE CHAPELLE` | Vieille Chapelle |
| 898 | `LES BORELS` | Borel |

Le détail et les justifications sont dans [`ANOMALIES.md`](ANOMALIES.md).
