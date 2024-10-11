=pod 
Scrivi uno script perl dal nome runner.pl. Lo script dovrà cercare nella cartella superiore a quella in cui è stato lanciato
lo script i file con estensione .pl, stampare il numero di righe contenute in ciascun file e, infine, rimuovere il diritto di
eseguibilità al file con meno righe.
=cut





# Per ottenere il numero di righe di un file, possiamo usare il comando wc -l. 
# Per ottenere il file con meno righe, possiamo usare il comando sort -n per ordinare i file in base al numero di righe e head -n 1 per ottenere il primo file della lista.
# Infine, per rimuovere il diritto di eseguibilità da un file, possiamo usare il comando chmod a-x.


$to_print=qx(wc ../*.pl -l | head -n -1 | sort -n | head -n 1); # wc -l conta le righe di ciascun file, head -n -1 esclude l'ultima riga (che contiene il totale), sort -n ordina i file in base al numero di righe, head -n 1 restituisce il primo file della lista 

@splitted = split " ",$to_print; # split divide la stringa in un array di stringhe, utilizzando lo spazio come separatore 

#print $to_print; # stampo il numero di righe di ciascun file
qx(chmod a-x $splitted[1]); # rimuovo il diritto di eseguibilità dal file con meno righe 

# chmod a-x rimuove il diritto di eseguibilità dal file
# qx() esegue il comando tra parentesi e restituisce l'output
# split divide la stringa in un array di stringhe, utilizzando lo spazio come separatore
# print stampa il numero di righe di ciascun file
# wc -l conta le righe di ciascun file
# head -n -1 esclude l'ultima riga (che contiene il totale), mostrando tutte le altre
# sort -n ordina i file in base al numero di righe
# head -n 1 restituisce il primo file della lista 
# ../*.pl seleziona tutti i file con estensione .pl nella cartella superiore
# $to_print contiene l'output del comando wc -l ... 
# $splitted[1] contiene il nome del file con meno righe
# $splitted[0] contiene il numero di righe del file con meno righe
