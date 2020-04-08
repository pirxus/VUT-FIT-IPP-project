Implementační dokumentace k 1. úloze do IPP 2019/2020
Jméno a příjmení: Šimon Sedláček
Login: xsedla1h

# Parser zdrojového kódu IPPcode20

## Modulární struktura programu
Parser je rozdělen do dvou zdrojových textů - parse.php a regex.php. Soubor regex.php
obsahuje definice většiny regulárních výrazů využívaných pro lexikálí a syntaktické
kontroly prováděné parserem. Soubor parse.php pak obsahuje hlavní tělo programu a má na
starost kompletní proces lexikální a syntaktické analýzy vstupního kódu.

## Struktura parse.php
V souboru parse.php jsou implementovány tři hlavní třídy - Parser, XMLer a Stats. Účelem
těchto tříd je rozdělení programu na tři základní bloky, z kterých každý má na starosti
specifickou úlohu.

Při spuštění programu je nejdříve provedena kontrola argumetnů programu. Pokud jsou
programu předány argumenty týkající se sbírání statistik o zdrojovém textu, tyto argumenty
zpracujeme do pole flagů, které jsou pak využity při inicializaci objektu třídy Stats.

Poté je vytvořen objekt třídy Parser, který po převezme řízení a provede analýzu vstupního
kódu. Po skončení analýzy jsou z objektu parseru přečteny proměnné indikující výsledek
analýzy a program je ukončen s příslušným návratovým kódem.

### Třída Parser
Tato třída má na starosti řízení a prováděná akcí lexikální a syntaktické analýzy
vstupního programu. V konstruktoru jsou zároveň vytvořeny pomocné objekty tříd XMLer,
která má na starosti tisk xml reprerentace kódu na výstup, a Stats, která má na starosti
sběr statistik o vstupním programu.

Hlavní metodou třídy Parser je metoda parse(), která postupně načítá rádky vstupního
kódu a kontroluje je. Nejprve jsou prováděny kontroly hlavičky vstupu a při potvrzení
korektnosti hlavičky je kontrolováno samotné tělo programu.

Kontroly jednotlivých instrukcí jsou shlukovány do několika specifických případů,
respektive daná kontrola je stejná pro všecny instrukce, které mají stejný počet a typ
argumentů. Tím je počet variant kontrol značně zredukován. Zpracovávaný řádek s instrukcí
je nejprve rozštěpen do pole podle mezer a postupně je zkontrolována integrita operačního
kódu, počet argumentů a integrita argumentů. Integrita argumentů je kontrolována s pomocí
regulárních výrazů definovaných v regex.php.

### Třída XMLer
Tato třída pouze poskytuje abstraktnější rozhraní pro tvorbu xml reprezentace kódu tak,
aby mohl objek parseru pouze volat jednoduché metodu a nemusel se se příliš zabývat režií
tvorby xml. Pro tvobu xml je využita třída XMLWriter.

### Třída Stats
Třída Stats sbírá do svých atributů statistiky o vstupním zdrojovém textu a pokud tak
bylo uživatelem skrze argumenty příkazové řádky specifikováno, tiskne tyto statistiky
po skončení analýzy vstupu do daného výstupního souboru.
