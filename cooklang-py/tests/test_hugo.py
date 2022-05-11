import unittest

from cooklang.hugo import transform

cake = """>> title: Cake aux olives
>> time: 50m
>> servings: 6


Préchauffer le four à 180°C (Th 6)


Dans un saladier, mélanger le @yaourt{1}, la @farine{150%g (environ 3 pots de yaourt)}, la @levure{1/2%sachet} et les @œufs{3}.
Ajouter l'@huile d'olive{1/2%pot (environ 50 ml)}. Bien mélanger.


Ajouter le @gruyère râpé{100%g}, le @basilic et les @olives{Environ 20 dénoyautées de chaque couleur (noires, vertes)} coupées en petits morceaux.

Verser dans un #moule à cake{} préalablement beurré et fariné. Cuire ~{40%minutes} au four à 180° C (thermostat 6).

Retirer le cake du four quand il est doré. Le servir tiède ou froid.

>> steps: Facultatif
Incorporer éventuellement le @jambon{100%g} (coupé en dés), les @tomates séchées{40%g} et le @fromage de chèvre{100%g}.


"""

croque = """>> title: Croque-monsieur
>> time: 10m
>> servings: 6
>> source: https://www.academiedugout.fr/recettes/croque-monsieur_981_2

>> steps: crème à l'emmental et parmesan
Dans un bol mélanger la @crème fraîche{16%cl}, râper l'@emmental{120%g} et le @parmesan{200%g}. Ajouter les jaunes d'@œuf{4}. Assaisonner de @poivre du moulin.

>> steps: croque
Beurrer une face d'une tranche de @pain de mie{8}, y disposer 1 tranche de @jambon{600%g} 1 tranche d'@emmental{600%g}, 1 tranche de jambon, 1 tranche d'emmental. Tartiner les 2 côtés de la deuxième tranche de pain avec la crème à l'emmental et parmesan.
Faire dorer le croque-monsieur sous le gril du four pendant 2 minutes ou sous la salamandre. Le déposer sur une assiette.
"""


class TestHugo(unittest.TestCase):
    def test_cake(self) -> None:
        out = transform(croque)
        print(out)
