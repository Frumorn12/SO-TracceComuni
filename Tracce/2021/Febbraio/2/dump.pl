#!/usr/bin/perl
use strict;
use warnings;

# Verifica degli argomenti
if (@ARGV != 3) {
    die "Uso: ./dump.pl <nome_file_log> <indirizzo_ip_destinazione> <porta_destinazione>\n";
}

# Parametri di input
my ($file_log, $ip_dest, $porta_dest) = @ARGV;

# Variabile per contare le connessioni da ogni IP sorgente
my %connessioni;

# Apri il file di log per la lettura
open(my $fh, '<', $file_log) or die "Impossibile aprire il file '$file_log': $!\n";

while (my $line = <$fh>) {
    # Match delle righe che corrispondono al formato richiesto
    if ($line =~ /\bIP\s+([\d\.]+)\.\d+\s+>\s+$ip_dest\.$porta_dest\b/) {
        my $ip_sorgente = $1;
        $connessioni{$ip_sorgente}++;
    }
}

# Chiude il file di log
close($fh);

# Ordina gli IP sorgenti in base al numero di connessioni (decrescente)
my @ordinati = sort { $connessioni{$b} <=> $connessioni{$a} } keys %connessioni;

# Scrivi l'output su file
open(my $out_fh, '>', 'output.log') or die "Impossibile creare il file 'output.log': $!\n";

foreach my $ip_sorgente (@ordinati) {
    print $out_fh "$ip_sorgente > $ip_dest.$porta_dest    ---> $connessioni{$ip_sorgente}\n";
}

# Chiude il file di output
close($out_fh);

print "Il file output.log è stato creato con successo.\n";
