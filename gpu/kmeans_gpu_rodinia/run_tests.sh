#!/bin/bash

DIM=2
echo "delete data old ..."
rm "results/kmeans_gpu_rodinia.csv"
echo "complete..."
while [ $DIM -lt 65 ]; do
	K=2
	python3 generate_data.py $DIM
	echo "create text.txt new"
	while [ $K -lt 65 ]; do
		echo "kmeans_k"$K"_d"$DIM
    	./kmeans -i "teste.txt" -m $K -n $K >> "results/kmeans_gpu_rodinia.csv"
		let K=K*2
	done
	let DIM=DIM*2
done
