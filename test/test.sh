#!/usr/bin/bash

function calculate_result(){    
    output_file=result_sample3.txt
        
    sed 's/[()|,]/ /g; s/\[s\]//g' ${output_file}

    n1=1
    n2=1
    n=$((n1+n2))

    sed 's/[()|, ]/ /g; s/\[s\]//g' ${output_file} | awk -v n="$n" '{cn+=$3; cn1+=$4; cn2+=$5; ct+=$6; ct1+=$7; ct2+=$8} 
        END {printf "commit:  %d (%d %d)   %.2f (%.2f %.2f)[s]\n", cn, cn1, cn2, ct/n, ct1/n, ct2/n}' | tee -a ${output_file}
        
    sed 's/[()|, ]/ /g; s/\[s\]//g' ${output_file} | awk -v n="$n" '{an+=$10; an1+=$11; an2+=$12; at+=$13; at1+=$14; at2+=$15} 
        END {printf "abort:  %d (%d %d)   %.2f (%.2f %.2f)[s]\n", an, an1, an2, at/n, at1/n, at2/n}' | tee -a ${output_file}
}

# a=1
function test(){
    echo "a = $1"
}
a=2
test $a


