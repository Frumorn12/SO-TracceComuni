$home = $ENV{'HOME'};  # $ENV{'HOME'} è una variabile d'ambiente che contiene il percorso della home directory dell'utente 

# Trova tutti i file Python nella home directory dell'utente
# find è un comando Unix che cerca file e directory in una gerarchia di directory 
# -name "*.py" specifica che vogliamo solo file con estensione .py 
# qx è un operatore Perl che esegue un comando di shell e restituisce l'output come una stringa  
@py_files = qx {find $home -name "*.pdf"}; 
chomp @py_files;  # chomp rimuove i caratteri di nuova linea alla fine di ogni stringa nell'array @py_files 

# PUNTO 1
foreach $file (@py_files){
    print "File: $file\n";  # Stampa il nome del file 

}
# PUNTO 2 
@py_files2 = qx{ls $home/*.py};  # Esegue il comando ls -l per elencare i file Python nella home directory
chomp @py_files2;  # Rimuove i caratteri di nuova linea alla fine di ogni stringa nell'array @py_files2

foreach $file (@py_files2){
    qx {chmod u+x $file};  # Esegue il comando chmod per rendere eseguibile il file
}

# PUNTO 3
# Stampi su STDOUT i percorsi dei file, presenti in una qualsiasi sottocartella1 della home dell’utente corrente, per cui
# esiste almeno un altro file con lo stesso nome. Stampare i percorsi di tutti gli omonimi.

@tutti_file = qx {find $home};  # Trova tutti i file nella home directory dell'utente 
chomp @tutti_file;  # Rimuove i caratteri di nuova linea alla fine di ogni stringa nell'array @tutti_file
foreach $file (@tutti_file){
    for $file2 (@tutti_file){
        if ($file ne $file2){
            $file_1 = qx {basename $file};  # Estrae il nome del file senza il percorso
            $file_2 = qx {basename $file2};  # Estrae il nome del file senza il percorso
            chomp $file_1;  # Rimuove i caratteri di nuova linea alla fine della stringa $file_1
            chomp $file_2;  # Rimuove i caratteri di nuova linea alla fine della stringa $file_2
            if ($file_1 eq $file_2){
                push (@file_uguali, $file);  # Aggiunge il file all'array @file_uguali se i nomi sono uguali     
            }
        }
    }
    
}
foreach $file (@file_uguali){
    print "$file\n";  # Stampa il percorso del file
} 