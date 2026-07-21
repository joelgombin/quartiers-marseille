# Anomalies relevées

Constats issus de la confrontation du jeu source à deux références externes :
l'export Etalab du cadastre (géométries) et le tableau Wikipédia des quartiers
(noms).

Les cinq écarts de libellé sont **corrigés** dans le champ `nom` : la graphie
officielle fait foi. Le libellé d'origine reste disponible dans `NOM_QUA`, et la
colonne `correction` du CSV signale les lignes concernées.

La correction passe par la table `CORRECTIONS` de `build.py`, qui énumère les
cinq cas avec les deux libellés attendus. Ce n'est pas un « Wikipédia gagne
toujours » : si l'une des deux sources changeait, la correction cesserait de
s'appliquer et le cas repasserait en alerte, plutôt que de renommer un quartier
en silence.

## 1. Deux entités nommées `ENDOUME` — le rang 31 est « Les Îles »

> **Corrigé** : `nom` = « Les Îles » pour le préfixe 831.

Le jeu compte **110 noms distincts pour 111 quartiers** : `ENDOUME` apparaît aux
rangs 30 et 31.

| | Rang 30 (préfixe 830) | Rang 31 (préfixe 831) |
|---|---|---|
| Composition | 4 polygones | 27 polygones |
| Part dominante | 5,3530 / 43,2829 | 5,3033 / 43,2764 |
| Territoire | quartier terrestre | **archipel du Frioul** |

Le préfixe cadastral 830 tombe exactement sur le rang 30 (5,3531 / 43,2829) :
celui-là est bien Endoume. Le rang 31, lui, est insulaire.

Le 7ᵉ arrondissement compte officiellement sept quartiers : Bompard, Endoume,
**Les Îles**, Le Pharo, Le Roucas Blanc, Saint-Lambert, Saint-Victor. Le rang 31
occupe la 3ᵉ position — celle des Îles, qui est aussi la place alphabétique
attendue entre Endoume et Le Pharo.

**Périmètre.** Le préfixe *cadastral* 831 est plus large que le *quartier* : ses
trois parts couvrent le Frioul (5,3047 / 43,2738), l'archipel de **Riou**
(5,3854 / 43,1794) et l'île de **Planier** (5,2299 / 43,1986). Or Riou relève
des Goudes, et seul le Frioul constitue un quartier. Le polygone du rang 31 est
donc correct pour le quartier — c'est le nom, pas la géométrie, qui est en
cause. C'est aussi ce qui explique le seul recouvrement faible de toute la
validation (0,08 au lieu de 0,99 en médiane).

## 2. Trois coquilles dans les libellés

> **Corrigées** : `nom` suit la graphie officielle.

| Préfixe | `code_qua` | Jeu source | Graphie officielle |
|---|---|---|---|
| 813 | 1320303 | `SAINT MAURON` | Saint-Mauron**t** |
| 814 | 1320304 | `LA VILETTE` | La Vi**ll**ette |
| 845 | 1320810 | `VIELLE CHAPELLE` | Vie**i**lle Chapelle |

## 3. Une variante d'usage

> **Alignée** sur la graphie officielle.

| Préfixe | `code_qua` | Jeu source | Retenu |
|---|---|---|---|
| 898 | 1321502 | `LES BORELS` | Borel |

Les deux formes circulent : ce n'est pas une coquille mais un choix éditorial,
tranché ici en faveur de la forme officielle. `NOM_QUA` conserve « LES BORELS ».

## 4. Une coquille côté Wikipédia (sans incidence sur ce jeu)

Dans le tableau de [Quartiers de Marseille](https://fr.wikipedia.org/wiki/Quartiers_de_Marseille),
**Sainte-Marthe porte le code `13 214 06`**, déjà attribué à Saint-Joseph : elle
devrait être `13 214 07`. C'est la raison pour laquelle `build.py` apparie les
noms sur le **rang** dans l'arrondissement et non sur le code affiché.

## 5. Le 9ᵉ arrondissement n'est pas dans l'ordre alphabétique

Ce n'est pas une anomalie mais un signal de provenance, noté ici pour mémoire :
l'ordre des entités est alphabétique dans 15 arrondissements sur 16. Dans le
**9ᵉ**, Sormiou (852) précède Sainte-Marguerite (853). Les deux rattachements
sont confirmés géométriquement (recouvrements 0,95 et 0,99).

L'ordre du fichier suit donc la numérotation **cadastrale** réelle, et non un
tri alphabétique appliqué après coup — ce qui conforte la déduction
`préfixe = 800 + rang`.
