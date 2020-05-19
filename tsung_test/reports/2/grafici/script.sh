#!/usr/bin/gnuplot -persist
set terminal epslatex color lw 2
set output 'confronto.tex'
set ylabel "$\\bar R$"
set xlabel "Workload intensity" 
set title "Comparison with M/G/1 and M/G/1/PS"
#set lmargin 0
#set title "Class $1$ stationary distribution"
set size 0.8,0.8
#set xrange [1:5000]
#set xtics  rotate by -45
set key top left
f(x) = 1/(0.107 - x*0.107)

mu = 0.107
variance = 29.615
lambda(x) = mu*x
p(x) = lambda(x)/mu
W(x) = (p(x) + lambda(x)*mu*variance)/(2*(mu-lambda(x)));
g(x) = W(x) + 1/mu
plot f(x) title "M/G/1/PS" w lines lc "blue",\
    g(x) title "M/G/1" w lines lc "red",\
    "dati.txt" using 1:2 title "application" w lines lc "black" dt 3
#"dati.txt" using 1:3 title "$M/G/1$" w lines lc "red" dt 2,\
#"dati.txt" using 1:4 title "$M/G/1/PS$" w lines lc "blue",\
#    EOF

 
