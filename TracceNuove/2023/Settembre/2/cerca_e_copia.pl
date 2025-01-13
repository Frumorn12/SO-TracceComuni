$matricola = "123456";
qx(mkdir $matricola);
if($#ARGV==0){
    qx(cp $ARGV[0]/*.pl $matricola);
}else{
    qx(cp ../*/*.pl $matricola);
}