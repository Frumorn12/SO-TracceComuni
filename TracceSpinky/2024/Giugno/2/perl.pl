for ($i=0; $i<2; $i++){
    $file = $ARGV[$i]; 
    print $file."\n"; 
    print "linee:". qx(cat ~/Desktop/$file | sort -u | wc -l). "\n";   
    # wc e basta conta tutte l righe parole e byte 
    # wc -l conta solo le righe 
    # sort ordina le righe
    # sort -u ordina e elimina i duplicati 
    print "caratteri:". qx(cat ~/Desktop/$file | sort -u | wc -w). "\n"; 
    # wc -w conta solo i caratteri     
}
# linee in comune
print "linee in comune:". qx(cat ~/Desktop/$ARGV[0] ~/Desktop/$ARGV[1] | sort | uniq -d | wc -l). "\n";
# uniq -d solo i duplicati