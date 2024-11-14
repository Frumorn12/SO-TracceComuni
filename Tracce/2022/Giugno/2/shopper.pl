#!/usr/bin/perl
use strict;
use warnings;

# Verifica dei parametri
if (@ARGV < 2 || @ARGV > 3) {
    die "Utilizzo: ./shopper.pl OPZIONI path [prezzo_massimo]\n";
}

my ($option, $path, $price_limit) = @ARGV;

# Verifica opzione e validità dei parametri
if ($option eq '-a' && defined $price_limit) {
    die "Errore: prezzo_massimo non deve essere specificato con l'opzione -a\n";
}
if (($option eq '-c' || $option eq '-cd') && !defined $price_limit) {
    die "Errore: prezzo_massimo deve essere specificato con l'opzione $option\n";
}

# Funzione per caricare i prodotti da un file
sub load_products {
    my ($file) = @_;
    open my $fh, '<', $file or die "Errore nell'apertura del file $file\n";
    <$fh>; # Salta la prima riga di intestazione 
    my %products;
    while (my $line = <$fh>) {
        chomp $line;
        my ($product, $price) = split /\|/, $line;
        $products{$product} = $price;
    }
    close $fh;
    return %products;
}

# Funzione per stampare i prodotti in base alle categorie
sub print_products_by_category {
    my ($path) = @_;
    opendir(my $dir, $path) or die "Errore nell'apertura della cartella $path\n";
    my @files = sort grep { /\.txt$/ } readdir($dir);
    closedir($dir);
    
    foreach my $file (@files) {
        my ($category) = $file =~ /(.+)\.txt$/;
        print "$category\n";
        
        my %products = load_products("$path/$file");
        foreach my $product (sort keys %products) {
            print "- $product\n";
        }
    }
}

# Funzione per filtrare e ordinare i prodotti per prezzo crescente
sub filter_and_print_products_ascending {
    my ($file, $price_limit) = @_;
    my %products = load_products($file);
    
    my @filtered = sort { $products{$a} <=> $products{$b} || $a cmp $b }
                   grep { $products{$_} < $price_limit } keys %products;
    
    foreach my $product (@filtered) {
        printf "%s : %.2f\n", $product, $products{$product};
    }
}

# Funzione per filtrare e ordinare i prodotti per prezzo decrescente e salvarli su file
sub filter_and_save_products_descending {
    my ($file, $price_limit) = @_;
    my %products = load_products($file);
    
    my @filtered = sort { $products{$b} <=> $products{$a} || $a cmp $b }
                   grep { $products{$_} < $price_limit } keys %products;
    
    open my $out, '>', 'out.log' or die "Errore nella creazione del file out.log\n";
    foreach my $product (@filtered) {
        printf $out "%s : %.2f\n", $product, $products{$product};
    }
    close $out;
    print "File out.log creato\n";
}

# Gestione delle opzioni
if ($option eq '-a') {
    print_products_by_category($path);
} elsif ($option eq '-c') {
    filter_and_print_products_ascending($path, $price_limit);
} elsif ($option eq '-cd') {
    filter_and_save_products_descending($path, $price_limit);
} else {
    die "Opzione non valida\n";
}
