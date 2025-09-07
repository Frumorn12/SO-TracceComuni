#!/usr/bin/perl
use strict;
use warnings;

# Ottieni il path della directory dai parametri dello script
# Se non viene specificato, usa la directory corrente
my $directory = $ARGV[0] // '.';

# Variabile per contare i file vuoti rinominati
my $count = 0;

# Funzione per cercare ricorsivamente i file vuoti
sub process_directory {
    my ($dir) = @_;

    # Apri la directory
    opendir(my $dh, $dir) or die "Impossibile aprire la directory $dir: $!";

    # Leggi i contenuti della directory
    while (my $entry = readdir($dh)) {
        # Ignora '.' e '..'
        next if $entry eq '.' or $entry eq '..';

        # Costruisci il percorso completo
        my $path = "$dir/$entry";

        if (-d $path) {
            # Se è una directory, chiamala ricorsivamente
            process_directory($path);
        } elsif (-f $path) {
            # Se è un file, verifica se è vuoto
            if (-s $path == 0) {
                my $new_name = $path . "_vuoto";
                # Rinomina il file
                rename($path, $new_name) or warn "Impossibile rinominare $path: $!";
                $count++;
            }
        }
    }

    # Chiudi la directory
    closedir($dh);
}

# Avvia la scansione della directory
process_directory($directory);

# Stampa il numero totale di file rinominati
print "Rinominati $count file vuoti nella directory $directory\n";
