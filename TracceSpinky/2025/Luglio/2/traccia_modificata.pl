
use warnings; 

# controllo che il numero di argomenti sia corretto


if (@ARGV!= 3){
    die "Numero di argomenti errato"; 
}

# si parte da 0
# $comando=$ARGV[1];
# $stringa=$ARGV[2];
# $linee=$ARGV[3];

$comando=$ARGV[0];
$stringa=$ARGV[1];
$linee=$ARGV[2];
# comando sbagliato. Dobbiamo prendere la documentazione di $comando quindi 
# dobbiamo aggiungiere il flag --help. Inoltre grep ha bisogno con il flag -C di un numero 
# dopo, in questo caso linee

# SBAGLIATO ANGILICA.
# mancava il flag --help, e inoltre il -C vuole un numero dopo .
# @ris = qx($comando | grep -C  $stringa)
# CORRETTO
@ris = qx(man $comando| grep -C $linee $stringa); 


$cont=0;
$max_cont=0;

@temp=(); 
for(@ris){
    # regex: 
    # // indica che è una regex 
    # \s* -> 0 o più spazi bianchi
    # -- -> due trattini
    # \s* -> 0 o più spazi bianchi 
    if(/\s*--\s*$/){
        if($cont>$max_cont){
            @da_stampare=@temp;
            # $cont=$max_cont;
            $max_cont=$cont; 
        }
        @temp=();
        $cont=0;
    }
    else{
        $cont+=1;
        # push $_,@temp;
        
        push @temp,$_; 
    }
}
# negli if ovviamente era sbagliato l'== era maggiore > 
if($cont>$max_cont){
    $max_cont=$cont; 
    @da_stampare=@temp; 
}

for (@da_stampare){
    print $_; 
}
