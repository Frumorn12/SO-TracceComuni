$to_print=qx(wc ../*.pl -l | head -n -1 | sort -n | head -n 1);
@splitted = split " ",$to_print;
print $splitted[0]; 
qx(chmod a-x $splitted[1]);


# wc è un comando che conta le righe, le parole e i byte di un file
# ../ è il percorso relativo alla directory padre 
# -l è un'opzione di wc che conta solo le righe    
# *.pl è un carattere jolly che rappresenta tutti i file con estensione .pl 


