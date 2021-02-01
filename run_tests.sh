#!/bin/bash

K=16

while [ $K -lt 17 ]; do
    DIM=2
    while [ $DIM -lt 33 ]; do
	echo "/upb/departments/pc2/users/h/h2jpenha/Documentos/kmeans_examples/kmeans_k"$K"_d"$DIM"/hw/synth/fdam_afu.gbs"
	#echo "kmeans_k"$K"_d"$DIM
        fpgaconf "/upb/departments/pc2/users/h/h2jpenha/Documentos/kmeans_examples/kmeans_k"$K"_d"$DIM"/hw/synth/fdam_afu.gbs"
	./main  100000 $K 100 $DIM ~/USCensus1990.data.txt
        let DIM=DIM*2
    done
    let K=K*2

done
