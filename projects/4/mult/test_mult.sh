#!/bin/bash

ASIM=/home/gieskanna/sose25/nand2tetris/tools/Assembler.sh
CPUSIM=/home/gieskanna/sose25/nand2tetris/tools/CPUEmulator.sh

rm Mult.hack
sh $ASIM Mult.asm
sh $CPUSIM  Mult.tst
