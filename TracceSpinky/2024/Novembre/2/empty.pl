if ($#ARGV == 1) {
    @lista = qx(ls -l $ARGV[0]);

    #Punto 1 Appendo in una lista tutti i file vuoti, Punto 2: rinomino i file vuoti 
    for $stringa(@lista){
        chomp $stringa;
        @splitted = split(" ", $stringa);
        if ($splitted[4] eq "0") {
            @file_vuoti.push($splitted[8]);
            # creo una variabile per il nome del file vuoto con tutto il percorso
            $vecchio = $ARGV[0]."/".$splitted[8]; 
            $nuovo = $ARGV[0]."/".$splitted[8]."_vuoto"; 
            rename($vecchio, $nuovo) or die "Impossibile rinominare il file: $!";
            print "File rinominato con successo.\n";

        }
    }    
} else {
    # non è stato passato il path quindi usero la cartella corrente
    @lista = qx(ls -l);
    #Punto 1 Appendo in una lista tutti i file vuoti, Punto 2: rinomino i file vuoti
    for $stringa(@lista){
        chomp $stringa;
        @splitted = split(" ", $stringa);
        if ($splitted[4] eq "0") {
            @file_vuoti.push($splitted[8]);
            # creo una variabile per il nome del file vuoto con tutto il percorso
            $vecchio = $splitted[8]; 
            $nuovo = $splitted[8]."_vuoto"; 
            rename($vecchio, $nuovo) or die "Impossibile rinominare il file: $!";
            print "File rinominato con successo.\n";

        }
    }
}



