## To-Do

### Symbol Tables
Scopes:

- class
    * Static (as static)
    * Field (as this)

    * bleiben immer gleich

- subroutine:
    * `Class className` --> Name: `this`, type = `className` , kind = `argument`, number = `0`
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

# vm translations
**Global symbols**: Square Game
| name       | type       | kind     | # |
|------      |------      |------    |---|
|   Square   |   Square   |   this   | 0 |
| direction  | int        | this     | 1 |
| 

```pyhton
      let square = Square.new(0, 0, 30);
      let direction = 0;  // initial state is no movement
      return this;
```
```
# put arguments onto the stack
+push constant 0
+push constant 0
+push constant 30

# call subroutine
call Square.new 3

# put defined square onto the stack 
pop this 0

# put value of next var declaration onto the stack
push constant 0

# put variable direction onto the stack
pop this 1
```