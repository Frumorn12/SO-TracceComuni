# Inizializzare un array associativo in perl

%studenti = ("Marco" => 82, "Giulia" => 90, "Luca" => 78); 

$studenti{"Sara"} = 95; 

for $nome (keys %studenti) {
    print "$nome: $studenti{$nome}\n";
} 