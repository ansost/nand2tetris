// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/4/Fill.asm

// Runs an infinite loop that listens to the keyboard input. 
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel. When no key is pressed, 
// the screen should be cleared.pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel. When no key is pressed, 
// the screen should be cleared.

(KEYBOARD_CHECK)
//Set incrementer to zero aka the first pixel aka screen
@SCREEN
D=A
@INCREMENTER
M=D

//Check keyboard value
@KBD
D=M

//If Keyboard value is not 0, jump to black
@BLACK
D;JNE 
// Else jump to white
@WHITE
0;JMP 

(BLACK)
@COLOR
M=-1
@CHANGE_COLOR
0;JMP

(WHITE)
@COLOR
M=0
@CHANGE_COLOR
0;JMP

(CHANGE_COLOR)
@COLOR
D=M

@INCREMENTER
A=M
M=D

//Increment
@INCREMENTER
M=M+1
D=M

@KBD
D=A-D

//If yes, leave loop
@KEYBOARD_CHECK
D;JLE

//Else continue loop
@CHANGE_COLOR
0;JMP

