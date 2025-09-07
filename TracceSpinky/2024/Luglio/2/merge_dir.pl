# in pratica dobbiamo copiare il contenuto di due cartelle
# passate come argomenti, in una terza cartella cartella chiamata merged
# se ci sono duplicati, dobbiamo tenere solo il piu recente 


# Primo passa creiamo la cartella merged se non esiste
# se esiste la svuotiamo 
qx(mkdir -p merged );
# qx esegue un comando di shell
# mkdir -p crea la directory se non esiste
# -p non da errore se esiste 
qx(rm -rf merged/*);
# qx rm -rf merged/* rimuove tutto il contenuto della directory merged 


# SECONDO PUNTO
# Iniziamo con il secondo punto andando a copiare i file dalla
# prima directory passata a merged 
qx(cp -p ~/$ARGV[0]/* merged); 
# cp copia i file da una directory a un'altra
# -p mantiene i permessi e le date di creazione 
# ~/ è la home directory dell'utente
# e continuamo iniziando a copiare i file dalla seconda directory passata 
# a merged, pero dobbiamo controllare se il file esiste già in merged 
@lista1 = qx(ls $ARGV[1]); 
# ls elenca i file in una directory 
chomp @lista1; 
# chomp rimuove il carattere di fine linea 
# chomp

# usiamo il for per scansionare la lista dei file 
for $file(@lista1){
    # qui andiamo a controllare se il file esiste già in merged 
    if (qx (ls merged/$file) eq "merged/$file\n"){   
    # eq confronta due stringhe
    # qx ls merged/$file elenca i file nella directory merged 
    # se il file esiste nella directory merged 
    # allora lo copia soltanto se è piu recente con l'if giu
        if (qx(cp -vup $ARGV[1]/$file merged) ne ""){
        # cp -up copia il file solo se è più recente
        # -u copia solo se il file di origine è più recente
        # -p mantiene i permessi e le date di creazione 
        # ne "" se il file è stato copiato è diverso da "" 
        # quindi se il file è stato copiato dovra essere diverso da ""
        # il fatto che è diverso è dovuta da -v
        # -v mostra i file copiati, se non ci sono file copiati non mostra niente ""   
            $owner{$file} = $ARGV[1]; 
            # $owner è un hash che contiene il file e la directory di origine 
            # questo serve per il punto 3b perchè ci dice anche ti tenere traccia del percorso originale
        }
        $overwritten{$file} = 1; # creaiamo una lista
                                 # che tiene traccai del file che sono stati sovrascritti 
    }else { # se il file non esiste in merged, lo copiamo tranquillamente
        qx(cp -p $ARGV[1]/$file merged);
        $owner{$file} = $ARGV[1]; 
    }
}

# PUNTO 3 
# Dopo aver creato la directory merged con i file uniti, lo script deve creare un file di log chiamato merge.log
# nella directory corrente. Questo file di log deve contenere

# lista dei file presenti nella directory merged 
@all = qx(ls merged);
chomp @all; # e poi va chompata


# echo crea un file di log, chiamato merged.log 
qx(echo "">merged.log); #se merged.log non esiste lo creo, altrimenti lo svuoto.
for $f (@all){#per ogni file in merged
    $new_line=$f." "; # inizializzo la stringa con il nome del file 
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
