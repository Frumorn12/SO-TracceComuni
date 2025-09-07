

$stringa_cercata="report"; 

@array = qx(cat "filetest.txt" | grep -P '$stringa_cercata\\S*\$' | sort -k 4 -b ); 

for(@array){
    print "$_\n";
} 
