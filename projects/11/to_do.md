## To-Do

### Symbol Tables
Scopes:

- class
    * Static (as static)
    * Field (as this)

    * bleiben immer gleich

- subroutine:
    * parameter (as argument)
    * local (as local)

    * nach jedem Aufruf muss die Symbol Table wieder gelöscht werden

**Table structure:**
| name | type | kind | # |
|------|------|------|---|
|      |      |      |   |
- *name*: Variablen Name 
- *type*: alle types von Jack (int, char, boolean) und Class types
- *kind*: Segment name (static/this für class, argument/local für subroutines) 
- *#*: counter for the memory segments in that table, separate counter for each segment


Script
- parse all symbols into the table
- compile statements using the table by replacing the system 
  
## Vorgehen:
1. SymbolTable Implementation
2. Extend syntax analysier with our fancy markup tags
3. Test it.

* XML Parser erstmal umschreiben, dass er nicht XML, sondern Informationen aus der Tabelle printet

1. Identifier Category (var, argument, static, field, class, subroutine)
2. Ob der Identifier gerade declared (hinter var declaration) oder genutzt wird (in einer expression)
3. zu welcher Kategorie er gehört mit der jeweiligen Nummer dazu (Type / Number)


[https://peps.python.org/pep-0636/](https://peps.python.org/pep-0636/)
```python
match cmd.split():
    case []:
        continue
    case [("push" | "pop") as action, segment, index]:
        # handle memory command
    case [("add" | "sub" | "neg" | "and" | "or" | "not") as command]:
        # handle arithmetic / logical command
    # more cases here
    case _:
        # invalid command, raise error
```
