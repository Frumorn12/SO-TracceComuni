$comando=$ARGV[1];
$stringa=$ARGV[2];
$linee=$ARGV[3];

@ris = qx($comando | grep -C  $stringa)
$cont=0;
$max_cont=0;
for(@ris){
    if(/\s*--\s*/){
        if($cont==$max_cont){
            @da_stampare=@temp;
            $cont=$max_cont;
        }
        @temp=();
        $cont=0;
    }
    else{
        $cont+=1;
        push $_,@temp;
    }
}
if($cont==$max_cont){
    $cont=0;
}
print @da_stampare;