#!/bin/bash

python generate_kmeans_gpu.py

K=2

while [ $K -le 64 ]; do
    DIM=2
    while [ $DIM -le 64 ]; do
	echo "kmeans_k"$K"_d"$DIM
        nvcc "kmeans_gpu_k"$K"_d"$DIM".shared.cu" -std=c++11 -O3
	    nvprof --unified-memory-profiling off --log-file "kmeans_gpu_k"$K"_d"$DIM".shared.nvprof.txt" ./a.out 2000000 100 ../../USCensus1990.data.txt
        let DIM=DIM*2
    done
    let K=K*2
done
rm a.out
rm *.cu