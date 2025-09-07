
use strict;
use warnings;

# si deve partire da 0 invece che da 1
# inoltre essendo che deve ricevere 3 argomenti è buona norma controllare che li riceva 
# $comando=$ARGV[1];
# $stringa=$ARGV[2];
# $linee=$ARGV[3];


if (@ARGV!=3){
    die "usage: perl $0 comando stringa linee\n";
} 
else {
    $comando=$ARGV[0];
    $stringa=$ARGV[1];
    $linee=$ARGV[2];
} 

@ris = qx($comando | grep -C  $stringa)
$cont=0;
$max_cont=0;
for(@ris){
    if(/\s*--\s*/){
        if($cont==$max_cont){
            @da_stampare=@temp;
            $cont=$max_cont;
        }
        @temp=();
        $cont=0;
    }
    else{
        $cont+=1;
        #pusho in temp $_, quindi il contrario

        #push $_,@temp;

        push @temp,$_; 
    }
    # lo metto qui 
    if($cont>=$max_cont){
       $cont=0;
       $max_cont=$cont; 
    }
}
# qui non va bene perchè se l'ultimo blocco è il più grande non lo stampa 
# 
print @da_stampare;