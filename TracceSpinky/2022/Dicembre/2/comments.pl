#!/usr/bin/perl

if($#ARGV==-1){ # ARGV è quello che viene passato da riga di comando 
                # @ARGV è un array che contiene gli argomenti passati
                # $ARGV è un elemento dell'array @ARGV, $ variabile
                # $#ARGV è l'ultimo indice dell'array @ARGV 
    print qx{ls /usr/include | grep -P "\.h\$"}; # qx è un comando che esegue il comando tra le parentesi
                                                 # ls è un comando che elenca i file in una directory
                                                 # grep è un comando che filtra l'output del comando precedente
                                                 # -P è un'opzione di grep che permette di usare le espressioni regolari
                                                 # il $ è un carattere speciale che indica la fine di una stringa  
}
elsif($#ARGV==0){ # se $#ARGV==0 allora c'è un solo argomento passato
    $cont=0; # cont è una variabile che conta il numero di commenti
    $file = shift @ARGV; # shift è un comando che rimuove il primo elemento dell'array @ARGV e lo restituisce 
    @file = qx(cat /usr/include/$file); # cat è un comando che legge il contenuto di un file e lo restituisce 
    for (@file){ # per ogni riga del file  
        if(/\/\*(.*)/){ # se la riga contiene un commento inizio con /* 
                        # / / è un delimitatore di espressione regolare in perl 
                        # \/\ è un carattere di escape per il carattere /, sto prendendo / 
                        # * dopo lo slash indica che dobbiamo prendere anche *
                        # \/\* vuol dire che stiamo cercando il commento inizio /*
                        # (.*) vuol dire che stiamo cercando qualsiasi cosa dopo il commento inizio /* 
            if(/\/\*(.*)\*\//){  # se la riga contiene un commento inizio e fine con /* e */  
                $comments[$cont]=$1; # $comments è un array che contiene i commenti 
                                     # $1 è una variabile che contiene il primo gruppo di cattura dell'espressione regolare 
                $cont++; # cont è un contatore che conta il numero di commenti 
                next; # next è un comando che salta alla prossima iterazione del ciclo 
            }
            $comments[$cont]=$1; # $comments è un array che contiene i commenti 
            $inComm=1; # inComm è una variabile che indica se siamo dentro un commento 
        }
        elsif($inComm==1){
            if(/(.*)\*\//){ # se la riga contiene un commento fine con */ 
                $inComm=0;
                $comments[$cont] .= $1;
                $cont++;
            }
            else{
               $comments[$cont] .= $_;  # $comments è un array che contiene i commenti 
                # $1 è una variabile che contiene il primo gruppo di cattura dell'espressione regolare 
                # $inComm è una variabile che indica se siamo dentro un commento
            }
        }
    }
    print join "\n",sort({length $b <=> length $a || $a cmp $b} @comments); #
=pod
    for(sort({length $b <=> length $a || $a cmp $b} @comments)){
        print $_."\n";
    }
=cut
}
else{
    die "troppi parametri";
}