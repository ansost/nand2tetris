// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/4/Mult.asm

////R0=number, R1=Multiplikator, R2=sum
// Make sure sum starts at 0.
@R2
M=0

// Check if R0 or R1 are zero.
// If yes, go to end.
@R1
D=M
@END
D;JEQ
@R0
D=M
@END
D;JEQ
(LOOP)
    @R0
    D=M
    @R2
    M=M+D // "Multiply"
    @R1
    M=M-1 // Multiplikator abziehen
    D=M
    @END 
    D;JLE // If Multiplikator<=0 go to END
    @LOOP 
    0;JMP // Else go to LOOP and continue
(END)
