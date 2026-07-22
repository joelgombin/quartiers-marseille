# Notes de méthode

Le jeu est reconstruit à chaque build depuis trois sources vivantes (IRIS-GE,
Wikipédia, cadastre Etalab). Ces notes consignent les points où cette
reconstruction demande de la vigilance.

## 1. Le préfixe 831 déborde le quartier des Îles

À la vérification cadastrale (`--verifier`), tous les préfixes se recouvrent avec
leur quartier au-delà de 0,9 — **sauf le 831, à 0,08**. Ce n'est pas une erreur
d'affectation : le rattachement pointe bien vers le bon quartier (Les Îles, code
`1320703`), mais le *préfixe cadastral* couvre un territoire plus large que le
*quartier*.

Les trois parts du préfixe 831 sont le Frioul (5,3047 / 43,2738), l'archipel de
**Riou** (5,3854 / 43,1794) et l'île de **Planier** (5,2299 / 43,1986). Or, au
sens du découpage des quartiers, Riou relève des Goudes et seul le Frioul
constitue le quartier des Îles. Le polygone du quartier est donc correct ; c'est
le préfixe cadastral qui est plus étendu. Le faible recouvrement est attendu et
sans conséquence sur l'affectation.

## 2. La jointure des noms dépend des codes Wikipédia

Le nom de chaque quartier est joint par son code (`code_qua`) au tableau de
Wikipédia. Cette jointure est exacte, mais elle suppose que les codes du tableau
soient justes et sans doublon.

Un antécédent : Sainte-Marthe y portait le code `13 214 06`, déjà attribué à
Saint-Joseph (elle aurait dû être `13 214 07`). **Corrigé en amont le 21 juillet
2026.** Si une erreur de ce genre réapparaissait, la jointure ne serait plus
bijective — et `build.py` s'arrête alors plutôt que de nommer un quartier au
hasard ou d'en laisser un sans nom.

## 3. L'ordre du 9ᵉ arrondissement n'est pas alphabétique

Le préfixe cadastral se déduit du rang du quartier dans la numérotation INSEE
(`préfixe = 800 + rang des code_qua triés`). Cet ordre est alphabétique dans 15
arrondissements sur 16 ; l'exception est le **9ᵉ**, où Sormiou (852) précède
Sainte-Marguerite (853).

Ce n'est pas une anomalie : les deux rattachements sont confirmés
géométriquement (recouvrements 0,95 et 0,99). La numérotation INSEE suit l'ordre
cadastral réel, et non un tri alphabétique appliqué après coup — ce qui conforte
la déduction du préfixe.
