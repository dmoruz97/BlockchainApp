#!/usr/bin/gnuplot -persist
set terminal epslatex color lw 2
set output 'confronto.tex'
set ylabel "$\\bar R$"
set xlabel "N" 
set title "Expected response time"
#set lmargin 0
#set title "Class $1$ stationary distribution"
set size 0.8,0.8
set xrange [0:10]
set yrange [0:20]
#set xtics  rotate by -45
set key top left
Db = 2.95
Z = 10
f(x) = x*Db - Z

D = 5.03
g(x) = D

plot f(x) title "Bound large $\N$" w lines lc "blue",\
    g(x) title "Bound small $\N$" w lines lc "red"
    

