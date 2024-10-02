=pod 
Scrivi uno script Perl dal nome merge_dirs.pl che riceve come parametri sulla linea di comando i percorsi di due
directory. Lo script deve svolgere le seguenti operazioni:
1. Unire il contenuto delle due directory in una terza directory chiamata merged, che deve essere creata nella
directory corrente.
2. Durante la copia dei file, evitare duplicati: se due file con lo stesso nome esistono in entrambe le directory,
mantenere solo il file più recente (in termini di data di modifica).
3. Dopo aver creato la directory merged con i file uniti, lo script deve creare un file di log chiamato merge.log
nella directory corrente. Questo file di log deve contenere:
a. Il nome di ciascun file copiato nella directory merged.
b. Il percorso originale del file (prima della copia).
c. Un'indicazione se il file è stato sovrascritto perché duplicato.

=cut 

# Qui devo creare una cartella. Sempre meglio fare tutti i controlli del caso per evitare errori.
# In questo caso dico : se creo qualcosa prima vedo se non esiste, in caso se esiste la svuoto
qx(mkdir -p merged); # -p crea la directory se non esiste, altrimenti non fa nulla 
qx(rm -rf merged/*); # svuoto la cartella merged 

# Copio il contenuto della prima cartella nella cartella merged
# @ARGV è un array che contiene i parametri passati allo script
# in questo caso @ARGV contiene i percorsi delle due cartelle

qx(cp -p $ARGV[0]/* merged 2>/dev/null); #se si passa una cartella a cp, viene dato un errore, quindi facciamo il redirect di STDERR in /dev/null. cp -p consente di copiare il file senza alterare la data di ultima modifica

# Copio il contenuto della seconda cartella nella cartella merged
@to_copy = qx(ls $ARGV[1]); # metto in un array i file presenti nella seconda cartella 
chomp @to_copy; # rimuovo il carattere di newline da ogni elemento dell'array 
for $file (@to_copy){ # per ogni file nella seconda cartella 
    if(qx(ls merged/$file 2>/dev/null) eq "merged/$file\n"){ #se in merged Ã¨ giÃ  stato copiato il file che voglio copiare dalla seconda cartella...
        if(qx(cp -vup $ARGV[1]/$file merged 2>/dev/null) ne ""){#lancio cp con: -u sovrascrive il file SOLO se la data di modifica Ã¨ piÃ¹ recente; -v stampa il path del file se la copia va a buon fine, non stampa nulla altrimenti 
            $owner{$file}=$ARGV[1]; #se ha stampato il path del file, vuol dire che Ã¨ stata tenuta la copia presente nella seconda cartella
        }
        $overwritten{$file}=1;#in ogni caso, visto che il file Ã¨ giÃ  presente in merged, lo contrassegno come SOVRASCRITTO
    }else{
        qx(cp -p $ARGV[1]/$file merged 2>/dev/null); #il file non Ã¨ duplicato, lo copio e basta
        $owner{$file}=$ARGV[1];#tengo traccia che si tratta di un file che si trovava nella seconda cartella
    }
}
@all = qx(ls merged);
chomp @all;
qx(echo "">merged.log); #se merged.log non esiste lo creo, altrimenti lo svuoto.
for $f (@all){#per ogni file in merged
    $new_line=$f." "; # inizio a costruire la riga da appendere nel file di log  
    if(defined $owner{$f}){#se ho tenuto traccia di chi Ã¨ il proprietario (vuol dire che potrebbe essere duplicato o comunque presente nella seconda cartella)
        $new_line.=": $owner{$f}/$f  ";
        if(defined $overwritten{$f}){#controllo se Ã¨ un duplicato
            $new_line.=": SOVRASCRITTO";
        }
    }
    else{
        $new_line.=": $ARGV[0]/$f";#altrimenti si tratta di un file che arriva dalla prima cartella
    }
    qx(echo "$new_line" >> merged.log)#appendo nel file di log
}