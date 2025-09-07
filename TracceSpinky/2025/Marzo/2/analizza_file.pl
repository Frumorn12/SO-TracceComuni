#!/usr/bin/perl 
@file_txt = qx (ls -l *.txt); 
$piugrande = 0; 
for $f (@file_txt) {
    @splitted = split(" ", $f); 
    $frase = $splitted[8];
    
    $num_righe = qx (wc -l $f); 
    
    if ($num_righe >= 20){
        # stampo il nome del file 
        push (@fileventi, $frase);   
        if ($splitted[4] > $piugrande){
            $piugrande = $splitted[4];
            $filegrande = $frase; 
        } 
        
    }
}

# stampo tutti i file con più di 20 righe
print "I file con più di 20 righe sono:\n";
foreach $f (@fileventi) {
    print "$f\n";
} 

$numerorighegrande = qx (wc -l $filegrande);
$numeroparolegrande = qx (wc -w $filegrande); 
print "Il file più grande è $filegrande con $numerorighegrande righe e $numeroparolegrande parole.\n";

# creo un file righe random.txt che contiene 10 righe random da tutti i file .txt nella cartella. Se ci
# sono meno di 10 righe, prendo tutte le righe.  uso il comando shuf per randomizzare le righe
@files_txt = qx (ls *.txt);
$righe = 0;

# per ogni file .txt lo apro e prendo le righe
# le shufo e le metto in un file righe_random.txt

for $f (@files_txt){
    open (FILE, $f) or die "Non riesco ad aprire il file $f: $!"; 
    @righe = <FILE>;
    close (FILE);
    # shuffo le righe
    @righe = qx (shuf -n 10 $f); 
    for $riga (@righe){
        push (@righe_random, $riga);    
    }
}

# ora creo il file righe_random.txt
open (FILE, ">righe_random.txt") or die "Non riesco a creare il file righe_random.txt: $!"; 
print FILE @righe_random;
close (FILE); 
