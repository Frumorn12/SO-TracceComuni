#! /usr/bin/perl


# Scrivi uno script folder_stats.pl che si occupi di ricavare alcune proprietà di una data cartella. In particolare,
# lo script deve poter essere invocato nel seguente modo:
# ./folder_stat.pl PATH
# dove PATH è obbligatorio ed è il path ad una cartella.
# Lo script dovrà stampare su STDOUT:
# 1. il numero e il nome delle sottocartelle della cartella indicata da PATH
# 2. la dimensione ed il nome del file più grande
# A questo punto lo script rimarrà in attesa di ricevere in input dall’utente il nome di una sottocartella o del file più voluminoso.
# Stampa una stringa di errore se il nome indicato non è nell’elenco stampato in precedenza. Se si riceve in input:
# ● il nome del file, lo script stamperà su STDOUT la data di ultima modifica
# ● il nome di una delle sottocartelle, lo script stamperà su STDOUT il contenuto della sottocartella stessa
# Esempio:
# ● Se lo script fosse invocato come
# ./folder_stat.pl /usr
# e il contenuto di /usr fosse il seguente
# drwxr-xr-x 2 root root 36864 Mar 13 11:51 bin
# drwxr-xr-x 2 root root 4096 Apr 15 2020 games
# drwxr-xr-x 36 root root 4096 May 10 2022 include
# drwxr-xr-x 82 root root 4096 May 10 2022 lib
# -rw-r--r-- 1 angilica angilica 3769 Jul 18 2022 file.txt
# -rw-r--r-- 1 angilica angilica 1677957 May 10 2022 output
# Lo script dovrebbe stampare
# 4
# bin
# games
# include
# lib
# output: 1677957
# ● se si ricevesse a questo punto in input bin
# bisognerebbe stampare il nome delle cartelle e dei file contenuti in /usr/bin;
# se si ricevesse invece in input output
# bisognerebbe stampare May 10 2022

$path = $ARGV[0] || die "Usage: $0 PATH\n"; 
die "Troppi argomenti\n" if @ARGV > 1;   

@contenuto_cartelle = qx(ls -l $path);
chomp @contenuto_cartelle;
$dimensione_max = 0;

for (@contenuto_cartelle){
    @splittata = split " "; # splitta la stringa in base agli spazi 
    # drwxr-xr-x  2 frumorn frumorn     4096  5 mag 20.59  Desktop
    # se faccio split " "
    # @splittata = ("drwxr-xr-x", "2", "frumorn", "frumorn", "4096", "5", "mag", "20.59", "Desktop"); 
    if (/^d/){ # controlla se la stringa inizia con la d allora è una cartella
        push @cartelle, $splittata[8]; # aggiunge il nome della cartella all'array @cartelle  
    } else{
        # se non inizia per d allora è un file
        # dobbiamo controllare se la dimensione è maggiore della dimensione massima
        if ($splittata[4] > $dimensione_max){
            $dimensione_max = $splittata[4]; # aggiorna la dimensione massima
            $file_max = $splittata[8]; # aggiorna il nome del file
            $ultima_modifica = $splittata[5]." ".$splittata[6]." ".$splittata[7]; # aggiorna la data di ultima modifica
        }

    }                               
}
print scalar @cartelle, "\n"; # stampa il numero di cartelle (len di Perl)
foreach $cartella(@cartelle){
    print "$cartella\n"; # stampa il nome della cartella
} 
print "$file_max: $dimensione_max\n"; # stampa il nome del file e la dimensione massima 

while (<STDIN>){ #Rimane in attesa con il while finche non scriviamo qua
    chomp; # rimuove il carattere Chompati il cazzo #se sei autistico suca 
    if ($file_max eq $_){ # $_ è un carattere speciale che contiene la stringa corrente in input (Concatenzaione con il punto)
        print "$ultima_modifica\n"; # stampa la data di ultima modifica 
        $done = 1; # setta la variabile done a 1
        last; # esci dal ciclo while
    
    }
    else{
        for $f (@cartelle){
            if ($f eq $_){
                print qx (ls $path/$f);
                $done = 1; # setta la variabile done a 1
                last; # esci dal ciclo for
            }
        }
    }
    if ($done==1){ # se la variabile done è settata a 1
        last; # esci dal ciclo while nel caso siamo usciti dal for
    }

    print "Stringa non trovata\n"; # stampa la stringa non trovata 

    
}
