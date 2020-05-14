#!/usr/bin/gnuplot -persist
set terminal epslatex color lw 2
set output 'confronto.tex'
set ylabel "$\\bar R$"
set xlabel "$Intensity$" 
set title "Confronto"
#set lmargin 0
#set title "Class $1$ stationary distribution"
set size 0.8,0.8
#set xrange [1:5000]
#set xtics  rotate by -45
set key bottom right
plot "confronto.txt" using 1:4 title "$M/G/1/PS$" w lines lc "blue",\
    "confronto.txt" using 1:3 title "$M/G/1$" w lines lc "red" dt 2,\
    "confronto.txt" using 1:2 title "$tsung$" w lines lc "black" dt 3
#    EOF

 
