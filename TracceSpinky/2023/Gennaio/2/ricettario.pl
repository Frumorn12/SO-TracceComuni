if(@ARGV==0){
    die "E' necessario specificare almeno un ingrediente";
}    

@ricette = qx(ls RICETTE);
chomp @ricette; 

foreach $ricetta(@ricette){
    chomp $ricetta; 

    # $nome è il nome della ricetta 
    # $ricetta è il nome del file
    # uc è una funzione che converte la stringa in maiuscolo 
    # $1 è il primo gruppo di cattura della regex 
    # $ricetta =~ "(.*)\.txt" è una regex che cerca il nome del file senza l'estensione .txt 
    # per esempio se il file si chiama pasta.txt, $1 sarà pasta  
    $nome = uc $1 if $ricetta =~ "(.*)\.txt";

    # adesso dobbiamo aprire la ricetta
    # quando dobbiamo aprire un file, dobbiamo controllare che non ci siano errori, se no schiatti
    # FH è un filehandle, è una variabile che contiene il riferimento al file aperto 
    open(FH,"<RICETTE/$ricetta") || die "Impossibile aprire il file RICETTE/$ricetta";

    while (<FH>){
        if (/Ingredienti/){
            $ingredienti = 1; 
        }
        if (/Preparazione/){
            close(FH);
        }
        if ($ingredienti == 1){
            foreach $ingrediente (@ARGV){
                chomp $ingrediente; 
                if (/$ingrediente/){
                    #salvo la ricetta in una nuova lista 
                    # per recuperarla in seguito

                    push @ricette_salvate, $ricetta;
                    # scalar @ricette_salvate, $ricetta;
                    # scalar è una funzione che conta gli elementi in un array 
                    # push aggiunge un elemento alla fine dell'array 
                    # @ricette_salvate è l'array che contiene le ricette salvate 
                    # $ricetta è il nome della ricetta 
                    print scalar @ricette_salvate, " - $nome\n"; 
                    close (FH); 
                }
            }
            
        }

    }
} 

if (@ricette_salvate == 0){
    print "Non sono state trovate ricette con gli ingredienti specificati\n";
}

while (<STDIN>){
    if (/END/){
        last; # esci dal ciclo 
    }
    # qui andiamo a controllare se l'input è un numero 
    # se non è un numero, lo ignora 
    # se è un numero, lo salva in $_ 
    # se sfora l'array, lo ignora 
    if($_<=0 || $_ >@ricette_salvate){
        print "Ricetta non in elenco, scegliere un valore tra 1 e ".scalar @match."\n";
        next;
    }
    open(FH,"<RICETTE/$ricette_salvate[$_-1]");
    while(<FH>){
        if(/Preparazione/){
            $print=1;
            next;
        }
        if($print){
            print $_;
        }
    }
    close(FH);
    print "\n";
    last;


}
