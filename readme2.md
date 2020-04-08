Implementační dokumentace k 2. úloze do IPP 2019/2020
Jméno a příjmení: Šimon Sedláček
Login: xsedla1h

# Interpret XML reprezentace kódu IPPcode20 (interpret.py)
Intepret lze spustit s argumenty --help (vypíše nápovědu), --input (změna standardního
vstupu interpretu za nějaký jiný soubor) a --source (specifikace souboru, ze kterého je
čtena xml reprezentace zdrojového kódu IPPcode20). Interpret také implementuje rozšíření
STACK a FLOAT.

Interpret je složen ze čtyř modulů: interpret.py, xml\_checker.py, execute.py a
operations.py.

## Modul interpret.py
Tento modul je hlavním modulem celého interpretu. Postupně jsou zde prováděny veškeré
operace spojené s interpretací. Nejprve jsou parsovány vstupní argumenty programu,
dále jsou zavolány funkce (modul xml\_checker.py) pro kontrolu formátu a také syntatickou
a lexikální kontrolu vstupního xml. Pokud tyto kontroly uspějí, je řízení předáno modulu
execute.py, který provede program. Po skončení provádění programu je interpret ukončen
s příslušným návratovým kódem.

## Modul xml\checker.py
Tento modul obsahuje veškeré funkce spojené s lexikální a syntaktickou kontrolou vstupního
xml. Tyto kontroly řídí funkce check\_syntax(), která pracuje ve třech fázích: Nejprve
jsou postupně zkontrolovány všechny elementy vstupního xml, jejich atributy.. U každé
instrukce jsou podle operačního kódu zkontrolovány typy a počet argumentů, jejich
lexikální a syntaktická správnost. Statické metody pro kontrolu argumentů jsou
implementovány ve třídě ArgChecks. Argumenty instrukcí jsou také seřazeny, aby jejich
pozice v xml odpovídaly jejich skutečným pozicím při provádění instrukce.

Dále jsou instrukce seřazeny podle atributu order, přičemž každá hodnota atributu order
je přepsána tak, aby výsledná sekvence odpovídala hodnotám indexů instrukcí v seznamu -
tedy hodnotám 0,1,2,...,n (toto nám pak umožní jednodušší provádění skoků v programu).

Jako poslední jsou ze vstupního programu extrahována všechna návěští a jsou uložena do
slovníku spolu s indexem instrukce, na který odkazují.

## Modul execute.py
V modulu execute.py je implementována třída Processor, která je abstrakcí reálného
procesoru - má své registry (instruction pointer), paměť (rámce), prováděný program...
Procesor postupně podle hodnoty instruction pointeru čte příslušné instrukce a volá
statické metody z modulu operations.py, které samotné instrukce implementují. Těmto
metodám předává i sebe sama, aby mohly instrukce číst a zapisovat data do paměti,
případně provádět skoky atd.

## Modul operations.py
V tomto modulu se nachází třída Operations, ve které jsou implementovány jednotlivé
instrukce. Každá instrukce IPPcode20 má vlastní metodu - přestože to vede na mnoho
velice podobných řádek kódu (ač spojených většinou s ošetřováním výjimek), vede to také
na přehlednější strukturu tohoto modulu.

# Testovací rámec (test.php)
Tento skript slouží k testování parse.php a interpret.py. Pracuje v jednom ze tří módů:
Režim "both" testuje oba skripty parse.php a interpret.py zároveň, přičemž je
interpretován výstup skriptu parse.php. Dále je možné pomocí argumentů --parse-only nebo
--int-only testovat buď pouze parser nebo pouze interpretaci. Další argumenty programu
jsou --help (výpis nápovědy), --directory (specifikace adresáře s testy, implicitně
aktuální adresář), --recursive (rekurzivní zanořování do podadresářů), --parse-script
(specifikace skriptu parseru, implicitně ./parse.php), --int-script (specifikace skriptu
interpretu, implicitně ./interpret.py), --jexamxml (specifikace cesty k programu jexamxml,
který je používán pro kontrolu výstupu parse.php).

## Struktura test.php
Skript test.php obsahuje dvě třídy: Test a HTMLgen.

Třída HTMLgen obsahuje několik metod pro generování html dokumentu s výsledy testů,
tento dokument se po skončení procesu testování nachází v souboru index.html.

Třída Test je ústřední strukturou skriptu a má za úkol řídit celý proces testování,
dává pokyny pro generování html.

## Testovací proces
Po spuštění skriptu je vytvořena instance třídy Test, která v konstruktoru provede
parsování argumentů skriptu, podle kterých nastaví své atributy (například cesta k testům,
cesty k testovaným skriptům atd.). Poté je zkontrolována integrita získaných atributů,
otestuje se existence specifikovaných souborů a přístup k nim.

Pokud předchozí proces proběhne bez chyb, je zahájeno samotné testování - postupně je
procházen aktuální adresář a hledají se zdrojové soubory s příponou .src. Pokud skript
narazí na podadresář a byl skriptu předán argument --recursive, je tento adresář odložen
na stack adresářů čekajících adresářů a bude zpracován v další iteraci.

K nalezenému souboru \*.src se skript pokusí najít soubory s příponami .in, .out a .rc,
které jsou použity pro evaluaci skutečného výstupu testovaného skriptu. Pokud něketrý z
těchto souborů chybí, je vytvořen a zapíše se do něj implicitní obsah (pro .rc soubor se
jedná o return code 0).

Dále je pomocí příkazu exec spuštěn testovaný skript a jeho návratový kód je porovnán
s obsahem souboru .rc. Pokud byl návratový kód nula, je také porovnán výstup skritpu se
souborem .out.

Při úspěšném testu je ve výsledném html dokumentu vygenerován řádek s úspěšným testem,
jinak daný řádek indikuje neúspěšný test.
