# se è stato passato un argomento
open(my $fh, '<', '/home/frumorn/.bash_history') or die "Impossibile aprire il file: $!"; 
@history = <$fh>; # <> prendo tutto il file 
close($fh); 
chomp(@history); 
if ($#ARGV == 0){
    # deve essere un intero
    if ($ARGV[0] =~ /^\d+$/){
        # è un intero
        $num = $ARGV[0];
        @ultimielementi =reverse @history; # prendo gli ultimi $num elementi
        for ($i = $num-1; $i >= 0; $i--){
            print "$ultimielementi[$i]\n"; 
              
        } 

        
    }
    else{
        print "L'argomento passato non è un intero\n";
        
    }
    
}
else{
    
    $minVolteUtilizzato = 99999999; 
    $maxVolteUtilizzato = 0; 
    $contatore = 0; 
    foreach $comando(@history){
        @comando = split(" ", $comando);
        foreach $comando2(@history){
            @comando2 = split(" ", $comando2);
             

            if ($comando[0] eq $comando2[0]){
                $contatore++;
            }
        }
        if ($contatore < $minVolteUtilizzato){
            $minVolteUtilizzato = $contatore;
            $comandoMin = $comando[0];
        }
        if ($contatore > $maxVolteUtilizzato){
            $maxVolteUtilizzato = $contatore;
            $comandoMax = $comando[0];
        } 
        $contatore = 0; 
    }
    print "$comandoMax  $maxVolteUtilizzato\n"; 
    print "$comandoMin  $minVolteUtilizzato\n";  
}