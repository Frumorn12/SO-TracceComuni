#!/usr/bin/perl
if(@ARGV!=3){
    die "invocazione errata, previsto controlla_file.pl PATH -g|-c S";
}
$path = @ARGV[0];
$tipo = @ARGV[1];
$s = @ARGV[2];
if($tipo cmp "-g"){
    $col = 4;
}
elsif($tipo cmp "-u"){
    $col=3;
}
@res = qx(ls -l | grep -P \'$s\\S*\$\' | sort -k -b);
for($res){
    @file = chomp " ";
    if($precedente ne $file[$col-1]){
        $somma=0;
        $precedente = $file[$col-1];
    }
    $somma=$file[4];
}
if($somma>0){
    qx(echo "$precedente: $somma">results.out);
}