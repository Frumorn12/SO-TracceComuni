
@file_log = qx{ls /var/log/}
chomp(@file_log)
$output_file = "my_log"; 
open(my $out_fh, '>', $output_file) or die "Impossibile aprire $output_file: $!";
for $file(@file_log){
    # se il file inizia per syslog*
    if ($file =~ /^syslog/){
        # devo estrerre i messaggi
        # che non siano del mese corrente
        # ora scrivo
        # il comando per estrarre i messaggi 
        # che non siano del mese corrente
        $data_nostra = qx{date}
        @data_nostra = split(" ", $data_nostra); 
        $date_file = qx(date -r /var/log/$file); 
        @date_file = split(" ", $date_file);

        if (@data_nostra[4] eq @date_file[4] && @data_nostra[5] eq @date_file[5]){ 
            # il file è del mese corrente
            # non lo prendo in considerazione
            print "Il file $file è del mese corrente\n";
        }else{
            if ($file =~ /\.gz$/){ # i file sono compressi finiscono con .gz 
                # il file è compresso
                # lo decomprimo con zgrep
                # apro il file con zgrep e scrivo su output_file
                @righe = qx{zgrep /var/log/$file}; 
                print $out_fh @righe; 
            }
        }
    }
    
}