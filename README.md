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
easy_install install lstgen
```
Danach ist das Program `lstgen` (für gewöhnlich)  unter `/usr/local/bin/lstgen`
verfügbar.

## Beispiel: Erzeugen einer PHP-Datei zur Berechnung der Lohnsteuer für das Jahr 2016:
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

