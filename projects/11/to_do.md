## To-Do

### Symbol Table
Scopes:

- class
    * Static
    * Field

    * bleiben immer gleich

- subroutine:
    * Argument
    * Var

    * nach jedem Aufruf muss die Symbol Table wieder gelöscht werden

In beiden Tabellen:
* Name
* Type : Darunter ing, String, aber auch selbst definierte
* Kind: static, field / argument, var
* Number: muss immer hochzählen, wenn neuer Eintrag in der Tabelle

## Vorgehen:
* XML Parser erstmal umschreiben, dass er nicht XML, sondern Informationen aus der Tabelle printet

1. Identifier Category (var, argument, static, field, class, subroutine)
2. Ob der Identifier gerade declared (hinter var declaration) oder genutzt wird (in einer expression)
3. zu welcher Kategorie er gehört mit der jeweiligen Nummer dazu (Type / Number)
