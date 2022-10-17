# LstGen

Mittels LstGen kann man aus den sgn. PAP (Programmablaufplan) Dateien, die
unter https://www.bmf-steuerrechner.de zur Verfügung stehen, validen Code
generieren, mit dem man ohne weitere Abhängigkeiten (wie z.B. einem externen
Service) die Lohnsteuer berechnen kann.

Folgende Programmiersprachen werden zur Zeit unterstützt:
* PHP
* Python
* Java
* Javascript
* Go

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
lstgen -p 2016_1 -l php --class-name Lohnsteuer2016 --outfile Lohnsteuer2016.php
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
Form von Kommentaren oder in der PDF Version des PAP unter https://www.bmf-steuerrechner.de/interface/programmablauf.xhtml

## Beispiel 2: Erzeugen einer Python-Datei zur Berechnung der Lohnsteuer für das Jahr 2014 (gleiche Voraussetzungen wie im PHP Beispiel)
```bash
lstgen -p 2014_1 -l python --class-name Lohnsteuer2014 --outfile lst2014.py
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
lst2014.MAIN()
print_lst(lst2014)

```

## Beispiel 3: Erzeugen eines Go-Moduls zur Berechnung der Lohnsteuer für das Jahr 2014

Folgende Dateistruktur wird benötigt:

```
.
├── cmd/
│   ├── main.go
│   └── start
├── go.mod
├── go.sum
└── tax/
    └── 2014.go
```

tax-Modul erzeugen:

```bash
mkdir tax
lstgen -p 2014_1 -l go --go-package-name Lohnsteuer2014 --outfile tax/2014.go
mkdir cmd

alternativ für 2022 via python das gen Verzeichnis:
python cli.py -p 2022_1 -l golang --go-package-name income_tax --outfile ../gen/2022.go
```

Erstellen von main.go:

```go
package main

import (
	"fmt"
	"github.com/shopspring/decimal"
	"yourpackage.com/tax"
)

func main() {
	lst := tax.NewLohnsteuer2014()
	lst.SetRe4(decimal.NewFromInt(50_000_00))  // in cents
	lst.SetPkv(1)
	lst.SetAlter1(0)
	lst.SetAf(0)
	lst.SetF(1)
	lst.SetPvs(0)
	lst.SetR(0)
	lst.SetLzzhinzu(decimal.NewFromInt(0))
	lst.SetPvz(0)
	lst.SetStkl(1)
	lst.SetLzz(2)
	lst.SetKrv(2)
	lst.MAIN()
	steuer := lst.GetLstlzz().Add(lst.GetStv().Add(lst.GetSts()))
	soli := lst.GetSolzlzz().Add(lst.GetSolzs().Add(lst.GetSolzv()))
	res := steuer.Add(soli).Div(decimal.NewFromInt(100))
	fmt.Printf("%v\n", res.StringFixed(2))
}

```

Ausführung:

```bash
go mod init yourpackage.com
go mod download
go build -o cmd/start cmd/main.go
cmd/start
```

## Beispiel 4: Erzeugen einer Javascript Funktion zur Berechnung der Lohnsteuer für das Jahr 2022

```lstgen -p 2022_1 -l javascript --class-name Lohnsteuer2022 --outfile Lohnsteuer2022.js```

Das generierte Node Module erfordert eine BigDecimal Implementierung.

Dafür kann man zum Beispiel folgendes npm installieren: `npm install bigdecimal`

Um eine ordungsgemäße Nutzung der Klasse zu garantieren, muss man das BigDecimal des NPM wie folgt neu definieren

```
const big = require('../node_modules/bigdecimal')
const BigDecimal = big.BigDecimal;
```

Anschliessend kann man das Modul wie folgt nutzen:

```
const Lohnsteuer2022 = require('Lohnsteuer2022');
```
