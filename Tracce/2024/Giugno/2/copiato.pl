=pod
Scrivi uno script Perl dal nome copiato.pl che riceve come parametri sulla linea di comando i soli nomi di due file da
cercare sul Desktop dell’utente corrente. Lo script deve restituire il numero totale di linee e caratteri dei due file dopo aver
rimosso eventuali linee duplicate da ciascun file. Infine deve stampare il numero di linee in comune ai due file già ripuliti
dalle ripetizioni.
=cut 

# Per ottenere il numero di linee e caratteri di un file, possiamo usare il comando wc -l e wc -m rispettivamente.
for ($i=0; $i<2; $i++)) { # per ogni file passato come parametro 
    $file = $ARGV[$i]; # prendo il nome del file
    print $file."\n"; # stampo il nome del file 
    print "linee:". qx(cat ~/Desktop/$file | sort -u | wc -l)."\n"; # stampo il numero di linee del file
    print "caratteri:".  qx(cat ~/Desktop/$file | sort -u | wc -m)."\n"; # stampo il numero di caratteri del file

    # sort -u ordina le linee e rimuove le ripetizioni
    # wc -l conta le linee 
    # wc -m conta i caratteri 
    # | serve per concatenare i comandi 
    # qx() esegue il comando tra parentesi e restituisce l'output 


}
print "linee in comune: ".qx(cat ~/Desktop/$ARGV[0] ~/Desktop/$ARGV[1] | sort | uniq -d | wc -l); # stampo il numero di linee in comune tra i due file
# sort ordina le linee
# uniq -d  
# wc -l conta le linee
# | serve per concatenare i comandi
# qx() esegue il comando tra parentesi e restituisce l'output
