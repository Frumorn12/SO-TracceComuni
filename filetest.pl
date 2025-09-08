
use warnings; 

# controllo che il numero di argomenti sia corretto


if (@ARGV!= 3){
    die "Numero di argomenti errato"; 
}

# si parte da 0
# $comando=$ARGV[1];
# $stringa=$ARGV[2];
# $linee=$ARGV[3];

my $comando=$ARGV[0];
my $stringa=$ARGV[1];
my $linee=$ARGV[2];
# comando sbagliato. Dobbiamo prendere la documentazione di $comando quindi 
# dobbiamo aggiungiere il flag --help. Inoltre grep ha bisogno con il flag -C di un numero 
# dopo, in questo caso linee
# @ris = qx($comando | grep -C  $stringa)

@ris = qx(man $comando | grep -C $linee $stringa); 
print "DEBUG: Risultato del comando:\n";
print "Comando: $comando --help | grep -C $linee $stringa\n";

$cont=0;
for (@ris){
    print "Linea $cont: ";
    $cont++; 
    print $_;
}

# my $count =0; 
# for (@ris){
#     chomp;
#     print "BLOCCO $count:  ";
#     print "$_\n";
#     $count++; 
# }