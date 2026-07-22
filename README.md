# Quartiers de Marseille

Les **111 quartiers de Marseille** au sens du décret 46-2285 du 18 octobre 1946,
avec leurs identifiants officiels et leur **préfixe de section cadastral**.

Diffusé sur data.gouv.fr : [Quartiers de Marseille](https://www.data.gouv.fr/datasets/quartiers-de-marseille-1).

## Ce que contient le jeu

| Champ | Exemple | Description |
|---|---|---|
| `prefixe` | `"801"` | **Préfixe de section cadastral** (DGFiP) |
| `code_qua` | `"1320101"` | Code officiel du grand quartier (INSEE) |
| `num_qua` | `1` | Rang du quartier dans son arrondissement |
| `nom` | `"Belsunce"` | Nom officiel, en graphie accentuée |
| `DEPCO` | `"13201"` | Code INSEE de l'arrondissement |
| `NOM_CO` | `"Marseille 1er Arrondissement"` | Libellé de l'arrondissement |

`code_qua`, `DEPCO`, `num_qua` et `NOM_CO` viennent directement du code IRIS et
de ses métadonnées ; `nom` du tableau officiel des quartiers ; `prefixe` est
déduit et vérifié contre le cadastre (voir plus bas).

## Télécharger

Les données sont diffusées sur **[data.gouv.fr](https://www.data.gouv.fr/datasets/quartiers-de-marseille-1)**.
Les liens ci-dessous sont stables — ils pointent toujours vers la dernière
version, quel que soit son millésime.

| Format | Lien | Usage |
|---|---|---|
| **GeoParquet** | [télécharger](https://www.data.gouv.fr/fr/datasets/r/786874c2-d61a-4099-9703-7bbda7ff20ed) | analyse, DuckDB, Python |
| GeoPackage | [télécharger](https://www.data.gouv.fr/fr/datasets/r/1d4fbc3a-3dff-4633-a4e6-052064c38f4a) | QGIS, ArcGIS |
| GeoJSON | [télécharger](https://www.data.gouv.fr/fr/datasets/r/8a8f7f54-7f91-482c-a78c-dd09d893d1b6) | web, échange |
| Shapefile (zip) | [télécharger](https://www.data.gouv.fr/fr/datasets/r/a7104f3c-e487-4af3-82ad-6197cedfaeb1) | SIG hérités |

Coordonnées en **EPSG:4326** (WGS 84). Ce dépôt versionne le **code** ; les
fichiers de données vivent sur data.gouv.fr. `uv run build.py` les régénère
localement dans `dist/`.

```python
import geopandas
url = "https://www.data.gouv.fr/fr/datasets/r/786874c2-d61a-4099-9703-7bbda7ff20ed"
quartiers = geopandas.read_parquet(url)
quartiers.loc[quartiers["prefixe"] == "801", "nom"]   # → Belsunce
```

```sql
-- DuckDB, en lisant directement le fichier distant
INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;
SELECT prefixe, nom
FROM 'https://www.data.gouv.fr/fr/datasets/r/786874c2-d61a-4099-9703-7bbda7ff20ed'
WHERE DEPCO = '13201';
```

Le **shapefile** a deux particularités inhérentes au format, sans perte
d'information : l'encodage est déclaré en UTF-8 par un fichier `.cpg` (sans quoi
« Les Îles » et « Opéra » ressortent illisibles), et les entités d'un seul tenant
y sont des `Polygon` là où les autres formats portent des `MultiPolygon` — le
format ne distingue pas les deux. Les noms de champs tiennent tous dans la limite
de 10 caractères, donc identiques d'un format à l'autre, sans troncature.

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

## D'où vient la géométrie

Des **IRIS de l'INSEE, agrégés** — la méthode d'origine du jeu. Les quartiers de
Marseille sont exactement les *grands quartiers* de l'INSEE, et le code d'un
grand quartier est le préfixe à 7 caractères du code IRIS :

```
393 IRIS  →  regroupés par code_iris[:7]  →  111 quartiers
```

`code_qua`, et avec lui `DEPCO`, `num_qua` et le nom de l'arrondissement, ne sont
donc pas déduits d'une position dans un fichier : ils sont **portés par la
donnée**. La géométrie suit le millésime courant des IRIS de l'IGN.

La source est **IRIS-GE**, la version grande échelle, et non `contours_iris`, qui
est généralisé : à découpage identique, ce dernier ne porte qu'un quart des
sommets.

## D'où vient le nom

Du [tableau des quartiers sur Wikipédia](https://fr.wikipedia.org/wiki/Quartiers_de_Marseille),
qui donne pour chaque quartier son code officiel et son nom en graphie accentuée.
Le nom est joint au quartier **par le code** (`code_qua`) — jointure exacte, sans
appariement approximatif de libellés. On exige qu'elle soit bijective (111 codes
IRIS ↔ 111 codes Wikipédia) : un code en double ou manquant arrête le script
plutôt que de nommer un quartier au hasard.

## Comment le préfixe a été établi

Le préfixe cadastral, lui, n'est écrit dans aucune source : il se déduit du rang
du quartier, `préfixe = 800 + rang des code_qua triés`. La déduction porte donc
sur la numérotation officielle de l'INSEE, lisible dans la donnée. Deux contrôles
la confirment.

**Recouvrement géométrique** — chaque quartier est confronté à la couche
`prefixes_sections` de l'export Etalab du cadastre :

- **111 / 111** rattachements confirmés ;
- recouvrement **médian 0,99**.

Le minimum, 0,08, concerne le préfixe 831 (les îles) : il désigne bien le même
quartier, mais le préfixe *cadastral* déborde le *quartier* — il couvre aussi
l'archipel de Riou et l'île de Planier, qui n'en font pas partie.

**Ordre alphabétique** — vérifié dans 15 arrondissements sur 16. L'exception, le
9ᵉ, est confirmée géométriquement : la numérotation INSEE suit l'ordre
cadastral, pas un tri alphabétique.

Reproduire : `uv run build.py --verifier`.

## Régénérer

Ce dépôt versionne le **code** (`build.py`), pas les données : les fichiers de
`dist/` sont entièrement régénérables et diffusés sur data.gouv.fr.

Le script est autoportant : il reconstruit tout depuis trois sources vivantes —
IRIS-GE, Wikipédia, cadastre — et déclare ses dépendances
([PEP 723](https://peps.python.org/pep-0723/)).

```sh
uv run build.py               # (re)génère dist/
uv run build.py --verifier    # + revalide le préfixe contre le cadastre
uv run build.py --help
```

Sans [uv](https://docs.astral.sh/uv/) :

```sh
pip install -r requirements.txt
python build.py
```

Le script produit aussi `dist/quartiers-marseille.csv`, une table de relecture
sans géométrie. Les sources téléchargées sont mises en cache dans `.cache/` (non
versionné) ; supprimer ce dossier force un rafraîchissement.

## Sources

| Source | Apport |
|---|---|
| [IRIS-GE (IGN, Géoplateforme)](https://geoservices.ign.fr/irisge) | géométrie, `code_qua`, `DEPCO`, `NOM_CO` |
| [Quartiers de Marseille (Wikipédia)](https://fr.wikipedia.org/wiki/Quartiers_de_Marseille) | noms officiels, joints par code |
| [Export Etalab du cadastre](https://cadastre.data.gouv.fr/datasets/cadastre-etalab) | vérification des préfixes |

## Licence

**[Licence Ouverte 2.0](https://www.etalab.gouv.fr/licence-ouverte-open-licence)**
(Etalab) — réutilisation libre, y compris commerciale, sous réserve de mentionner
la paternité et la date de dernière mise à jour. Texte intégral :
[`LICENSE.md`](LICENSE.md).

Les données dérivent de sources publiques sous la même licence ou compatibles
(cf. *Sources*).

## Reproductibilité

À sources inchangées, la régénération est reproductible **bit à bit** — CSV,
GeoJSON, GeoParquet, shapefile et son archive, dont l'horodatage est figé pour
cette raison — **sauf le GeoPackage**. SQLite y inscrit des identifiants propres
à chaque écriture, si bien que le fichier change à chaque exécution alors que son
contenu, attributs et géométries, reste rigoureusement identique. Deux builds ne
diffèrent donc que par ce fichier, sans changement de donnée.

## Notes

Quelques points de méthode et de vigilance — préfixe 831 qui déborde le quartier
des Îles, dépendance à l'exactitude des codes Wikipédia, ordre du 9ᵉ — sont
consignés dans [`NOTES.md`](NOTES.md).
