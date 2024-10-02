#!/usr/bin/perl

if($#ARGV==-1){ # se non ci sono parametri
    print qx{ls /usr/include | grep -P "\.h\$"}; # stampa tutti i file .h in /usr/include 
}
elsif($#ARGV==0){ # se c'è un solo parametro 
    $cont=0; # contatore per l'array dei commenti
    $file = shift @ARGV; # prendo il primo parametro 
    @file = qx(cat /usr/include/$file); # leggo il file 
    for (@file){ # per ogni riga del file
        if(/\/\*(.*)/){ # se trovo un commento multilinea 
            if(/\/\*(.*)\*\//){ # se il commento multilinea è tutto sulla stessa riga 
                $comments[$cont]=$1; # lo metto nell'array dei commenti 
                $cont++; # incremento il contatore
                next; # passo alla prossima riga
            }  
            $comments[$cont]=$1; # metto la parte iniziale del commento multilinea nell'array dei commenti
            $inComm=1; # setto il flag per indicare che sono dentro un commento multilinea
        }
        elsif($inComm==1){ # se sono dentro un commento multilinea
            if(/(.*)\*\//){ # se trovo la fine del commento multilinea 
                $inComm=0; # resetto il flag 
                $comments[$cont] .= $1; # metto la parte finale del commento nell'array dei commenti
                $cont++; # incremento il contatore
            }
            else{ # 
               $comments[$cont] .= $_; #  metto la riga nell'array dei commenti 
            }
        }
    }
    print join "\n",sort({length $b <=> length $a || $a cmp $b} @comments); # stampo i commenti ordinati per lunghezza
=pod
    for(sort({length $b <=> length $a || $a cmp $b} @comments)){
        print $_."\n";
    }
=cut
}
else{ # se ci sono più di un parametro 
    die "troppi parametri"; # stampo un messaggio di errore 
} 