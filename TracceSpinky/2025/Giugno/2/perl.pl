#!/usr/bin/perl
if(@ARGV!=3){ # @-> identifica l'array, ARGV -> parametri passati insieme all'invocazione dello script
    die "invocazione errata, previsto controlla_file.pl PATH -g|-u S"; # die -> è buona norma controllare se il numero di parametri è giusto e in caso killare il programma se non rispetta il vincolo
}
$path = $ARGV[0]; # $ -> identifica una variabile, può essere tutto tranne essere una lista
$tipo = $ARGV[1];
$s = $ARGV[2];
if($tipo eq "-g"){ # eq restituisce booleano se vero o no la condizione
    $col = 4;
}
elsif($tipo eq "-u"){
    $col=3;
}
#qx -> esegue comandi terminale
#grep -> filtro cosa prendere
#$ -> controlla fine riga,
#/S -> controlla che non ci siano spazi bianchi
#* -> 0 o più
#\ -> serve a indicare che \S* e $ sono comandi regex usati nel grep e non un comando di perl
# "-k" ti sorta per colonna, in questo caso per la colonna 4
# "-b" non considera gli spazi vuoti
@res = qx(ls -l | grep -P '$s\\S*\$' | sort -k4 -b);
$somma = 0;
$precedente = 0;
for(@res){
    @file = split " ", $_; #split -> splitta per ogni spazio, $_ -> intende che splitta l'ultima riga
    if ($precedente eq 0){
        $precedente = $file[$col-1];
    }
    if($precedente ne $file[$col-1]){
        if($somma>0){
            # >> appende precedente e somma a results.out.
            qx(echo "$precedente: $somma">>results.out);
        }
        $somma=0;
        $precedente = $file[$col-1];
    }
    $somma+=$file[4];

}
if($somma>0){
    qx(echo "$precedente: $somma">>results.out);
}
