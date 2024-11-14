#!/usr/bin/perl
use strict;
use warnings;
use Archive::Tar;
use IO::File;

# Controlla se è stato passato un argomento PATH
if (@ARGV != 1) {
    die "Utilizzo: ./booking.pl PATH\n";
}

my $path = $ARGV[0];
my $tar_file = "$path/Book.tar.gz";



# Verifica se il file tar.gz esiste
unless (-e $tar_file) {
    die "Errore: file Book.tar.gz non trovato nel percorso specificato\n";
}

# Estrai l'archivio tar.gz
my $tar = Archive::Tar->new;
$tar->read($tar_file);
$tar->extract();

# Funzione per analizzare i file del mese e memorizzare i dati
my %month_data;
foreach my $file ($tar->list_files()) {
    if ($file =~ /(\w+)_(\d+)\.txt$/) {
        my ($month, $year) = ($1, $2);
        open my $fh, '<', $file or die "Errore nell'apertura del file $file\n";
        
        # Salta la prima riga di intestazione (giorni della settimana)
        <$fh>;

        # Leggi giorni e disponibilità alternati
        while (my $days = <$fh>) {
            my $availability = <$fh>;
            my @days = split ' ', $days;
            my @availability = split ' ', $availability;
            
            for my $i (0..$#days) {
                if ($days[$i] ne '-') {
                    push @{$month_data{$month}->{$i}}, $availability[$i];
                }
            }
        }
        close $fh;
    }
}

# Funzione per calcolare la disponibilità per ogni giorno della settimana
sub calculate_availability {
    my ($month) = @_;
    my %day_totals;

    foreach my $day_index (keys %{$month_data{$month}}) {
        my $total = 0;
        foreach my $value (@{$month_data{$month}->{$day_index}}) {
            $total += $value;
        }
        $day_totals{$day_index} = $total;
    }

    return %day_totals;
}

# Funzione per contare i giorni con 0 camere disponibili
sub count_zero_days {
    my $zero_days = 0;

    foreach my $month (keys %month_data) {
        foreach my $day_index (keys %{$month_data{$month}}) {
            foreach my $value (@{$month_data{$month}->{$day_index}}) {
                if ($value == 0) {
                    $zero_days++;
                }
            }
        }
    }

    return $zero_days;
}

# Gestione delle richieste da STDIN
while (1) {
    print "Inserisci una richiesta (-n mese, -m o END): ";
    my $input = <STDIN>;
    chomp $input;
    
    if ($input eq 'END') {
        last;
    } elsif ($input =~ /^-n (\w+)$/) {
        my $month = $1;
        if (exists $month_data{$month}) {
            my %day_totals = calculate_availability($month);

            # Ordina in base alla disponibilità e poi per giorno della settimana in ordine inverso alfabetico
            my @sorted = sort {
                $day_totals{$a} <=> $day_totals{$b} || $b cmp $a
            } keys %day_totals;

            # Giorni della settimana per output
            my @days_of_week = qw(Lunedì Martedì Mercoledì Giovedì Venerdì Sabato Domenica);

            # Stampa i risultati
            foreach my $day_index (@sorted) {
                print "$days_of_week[$day_index] $day_totals{$day_index}\n";
            }
        } else {
            print "Mese non trovato\n";
        }
    } elsif ($input eq '-m') {
        my $zero_days = count_zero_days();
        
        # Scrivi il file log.txt
        open my $log, '>', 'log.txt' or die "Errore nella creazione del file log.txt\n";
        print $log "Nei mesi analizzati, ci sono stati $zero_days giorni con 0 camere disponibili\n";
        close $log;
        
        print "File log.txt creato\n";
    } else {
        print "Richiesta non valida\n";
    }
}
