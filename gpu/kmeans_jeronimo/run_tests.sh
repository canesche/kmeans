#!/bin/bash

python generate_kmeans_gpu.py

K=2

while [ $K -lt 65 ]; do
    DIM=2
    while [ $DIM -lt 65 ]; do
	echo "kmeans_k"$K"_d"$DIM
        nvcc "kmeans_gpu_k"$K"_d"$DIM".cu" -std=c++11 -O3
	./a.out 2000000 100 ~/Documentos/kmeans/USCensus1990.data.txt
        let DIM=DIM*2
    done
    let K=K*2
done
rm a.out
rm *.cu