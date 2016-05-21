# LstGen

Mittels LstGen kann man aus den sgn. PAP (Programmablaufplan) Dateien, die
unter https://www.bmf-steuerrechner.de zur Verfügung stehen, validen Code
generieren, mit dem man ohne weitere Abhängigkeiten (wie z.B. einem externen
Service) die Lohnsteuer berechnen kann.

Zur Zeit werden drei Sprachen unterstützt:
* PHP
* Python
* Java

## Installation
* Mit `pip` oder `easy_install` aus PyPI:
```bash
pip install lstgen
```
oder
```bash
easy_install lstgen
```
Danach ist das Program `lstgen` (für gewöhnlich)  unter `/usr/local/bin/lstgen`
verfügbar.

## Beispiel 1: Erzeugen einer PHP-Datei zur Berechnung der Lohnsteuer für das Jahr 2016
```bash
lstgen 2016 php --class-name Lohnsteuer2016 > Lohnsteuer2016.php
```
Der generierte Code benötigt für die Berechnung die [Brick\Math Bibliothek](https://github.com/brick/math)
und geht davon aus, dass sie mittels [Composer](https://getcomposer.org/) installiert wurde.

Danach kann die generierte Klasse einfach importiert und folgendermassen in eigenem Code verwendet werden:
```php
<?php

require "Lohnsteuer2016.php";

$brutto = 500000; // Brutto in ¢ent
$lst = new Lohnsteuer2015Big();
$lst->setRe4($brutto);
$lst->setPkv(1);
$lst->setAlter1(0);
$lst->setAf(0);
$lst->setF(1);
$lst->setPvs(0);
$lst->setR(0);
$lst->setLzzhinzu(0);
$lst->setPvz(0);
$lst->setStkl(1);
$lst->setLzz(2);
$lst->setKrv(2);
$lst->main();
$steuer = floor($lst->getLstlzz()->toFloat() + $lst->getStv()->toFloat() + $lst->getSts()->toFloat());
$soli = floor($lst->getSolzlzz()->toFloat() + $lst->getSolzs()->toFloat() + $lst->getSolzv()->toFloat()) / 100;
$stges = $steuer + $soli;
echo "steuer: $steuer\nsoli: $soli\nstges: $stges\n";
```
Oberes Beispiel zeigt die Berechnung der Lohnsteuer und Solidaritätszuschlags für einen Arbeitnehmer
mit Steuerklasse 1, monatlichem Brutto von 5000€, privat versichert und ohne Arbeitgeberzuschuss für PKV.

Eine detaillierte Erklärung zu den jeweiligen Eingabeparametern findet man entweder im generierten Code in
Form von Kommentaren oder in der PDF Version des PAP unter https://www.bmf-steuerrechner.de/interface/pap.jsp

## Beispiel 2: Erzeugen einer Python-Datei zur Berechnung der Lohnsteuer für das Jahr 2014 (gleiche Voraussetzungen wie im PHP Beispiel)
```bash
lstgen 2014 python --class-name Lohnsteuer2014 > lst2014.py
```

Der generierte Code kann dann so verwendet werden:
```python
import math
from lst2014 import Lohnsteuer2014

def print_lst(lst):
    steuer = math.floor(float(lst.getLstlzz()) + float(lst.getStv()) + float(lst.getSts())) / 100.0
    soli = math.floor(float(lst.getSolzlzz()) + float(lst.getSolzs()) + float(lst.getSolzv())) / 100
    stges = steuer + soli
    print("steuer: {steuer}\nsoli: {soli}\nstges: {stges}".format(
        steuer=steuer,
        soli=soli,
        stges=stges
    ))

brutto = 500000 # Brutto in ¢ent
# Setzen der Parameter mit Settern
lst2014 = Lohnsteuer2014()
lst2014.setRe4(brutto) # cent
lst2014.setPkv(1)
lst2014.setAlter1(0)
lst2014.setAf(0)
lst2014.setF(1)
lst2014.setPvs(0)
lst2014.setR(0)
lst2014.setLzzhinzu(0)
lst2014.setPvz(0)
lst2014.setStkl(1)
lst2014.setLzz(2)
lst2014.setKrv(2)
lst2014.MAIN()
print_lst(lst2014)

# Setzen der Parameter mittels Konstruktor-Argumente
lst2014 = Lohnsteuer2014(
    RE4=brutto,
    PKV=1,
    ALTER1=0,
    af=0,
    f=1,
    PVS=0,
    R=0,
    LZZHINZU=0,
    PVZ=0,
    STKL=1,
    LZZ=2,
    KRV=2
)
print_lst(lst2014)

```
