#!/bin/bash

g++ "main.cpp" -std=c++11 -O3

K=2

while [ $K -lt 65 ]; do
    DIM=2
    while [ $DIM -lt 65 ]; do
        echo "kmeans_k"$K"_d"$DIM
        ./a.out 2000000 $K 100 $DIM ~/Documentos/kmeans/USCensus1990.data.txt
        let DIM=DIM*2
    done
    let K=K*2
done
rm a.out

