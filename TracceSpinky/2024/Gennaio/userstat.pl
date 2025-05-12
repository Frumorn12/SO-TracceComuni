
print ($ENV{USER} . "\n");

@processi = qx{ps -u $ENV{USER}}; # lista dei processi dell'utente 

foreach $processo (@processi) {
    @splitted = split(" ", $processo); # splitto la riga in base agli spazi 
    print $splitted[0] . "\n"; # stampo il nome del processo 
} 

# lo spaizo opccupato su disco dalla home dell'utente in maniera ricorsiva
# devo usare il comando du 

$spazio = qx{du -sh $ENV{HOME}}; # spazio occupato su disco dalla home dell'utente 

print $spazio."/n"; # stampo lo spazio occupato su disco dalla home dell'utente 