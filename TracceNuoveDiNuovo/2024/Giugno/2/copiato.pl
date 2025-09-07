for ($i=0; $i<2; $i++)) {
    $file = $ARGV[$i];
    print $file."\n";
    print "linee:". qx(cat ~/Desktop/$file | sort -u | wc -l)."\n";
    print "caratteri:".  qx(cat ~/Desktop/$file | sort -u | wc -m)."\n";

}
print "linee in comune: ".qx(cat ~/Desktop/$ARGV[0] ~/Desktop/$ARGV[1] | sort | uniq -d | wc -l);