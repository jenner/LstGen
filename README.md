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
