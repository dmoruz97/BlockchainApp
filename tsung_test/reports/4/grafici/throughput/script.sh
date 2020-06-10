#!/usr/bin/gnuplot -persist
set terminal epslatex color lw 2
set output 'confronto.tex'
set ylabel "X"
set xlabel "N" 
set title "Throughput"
#set lmargin 0
#set title "Class $1$ stationary distribution"
set size 0.8,0.8
set xrange [0:10]
set yrange [0:0.45]
#set xtics  rotate by -45
set key bottom right
Db = 2.95
f(x) = 1/Db

D = 5.03
Z = 10
g(x) = x/(D+Z)

plot f(x) title "Bound large $\N$" w lines lc "blue",\
    g(x) title "Bound small $\N$" w lines lc "red"
    

