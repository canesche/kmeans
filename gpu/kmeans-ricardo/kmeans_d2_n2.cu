#include "common.h"
#include <cuda_runtime.h>
#include <stdio.h>

/*
 * kmeans example 2D
*/

__global__ void kmeans (int *input, int*centroids, int*newcentroids, int *counter, const int n)
{
   int Dim = 2;
   int i = (blockIdx.x * blockDim.x + threadIdx.x)*Dim;
 	if ( i < n ) {
		// map
		int point_d0 = input[i+0];
		int point_d1 = input[i+1];
		int k0_d0 = point_d0 - centroids[0];
		int k0_d1 = point_d1 - centroids[1];
		int k1_d0 = point_d0 - centroids[2];
		int k1_d1 = point_d1 - centroids[3];
		k0_d0 *= k0_d0;
		k0_d1 *= k0_d1;
		k1_d0 *= k1_d0;
		k1_d1 *= k1_d1;
		// reduce sum
		k0_d0 = k0_d0 + k0_d1;
		k1_d0 = k1_d0 + k1_d1;
		// reduce min 
		int k = (k0_d0 < k1_d0 ) ? 0 : 1;
		// add current point to new centroids sum
		atomicAdd(&(newcentroids[Dim*k]), point_d0);
		atomicAdd(&(newcentroids[Dim*k+1]),point_d1);
		atomicAdd(&(counter[k]),1);
 	} // if
}


int main(int argc, char **argv)
{
    printf("%s Starting...\n", argv[0]);	

	int r;
	int qtde_points, qtde_centroides, qtde_dim, max_iterations, format_data;
 
	r = scanf ("%i",&qtde_points);
	r = scanf ("%i",&qtde_centroides);
	r = scanf ("%i",&qtde_dim);
	r = scanf ("%i",&max_iterations);
	r = scanf ("%i",&format_data);
	
	/*printf("%i\n", qtde_points);
	printf("%i\n", qtde_centroides);
	printf("%i\n", qtde_dim);
	printf("%i\n", max_iterations);
	printf("%i\n", format_data);*/

    // set up device
    int dev = 0;
    cudaDeviceProp deviceProp;
    CHECK(cudaGetDeviceProperties(&deviceProp, dev));
    printf("Using Device %d: %s\n", dev, deviceProp.name);
    CHECK(cudaSetDevice(dev));

    // set up data size of vectors
    int Dim  = qtde_dim;
    int k = qtde_centroides;
    int nElem = qtde_dim * qtde_points;
    printf("Vector Size %d\n", nElem);

    // malloc host memory
    size_t nBytes = nElem * sizeof(int);
    size_t cBytes = Dim * k * sizeof(int);
    size_t sBytes = Dim * k * sizeof(int);
    size_t tBytes = k * sizeof(int);

    int *h_data, *h_centroids;
    h_data = (int *)malloc(nBytes);
    h_centroids = (int *)malloc(cBytes);
    
    // insercao de centroides
    // printf("%s\n", "centroides");
    for(int i = 0; i < 2*qtde_centroides; i++){
    	r = scanf ("%i",&h_centroids[i]);
    	//printf("i = %i %i\n", i, h_centroids[i]);
    }
    
    // insercao dos dados
    // printf("%s\n", "dados");
    for(int i = 0; i < 2*qtde_points; i++){
    	r = scanf ("%i",&h_data[i]);
    	//printf("i = %i %i\n", i, h_data[i]);
    }
    
    int *h_newcentroids;
    h_newcentroids = (int *)malloc(sBytes);
    int *h_counter;
    h_counter = (int *)malloc(tBytes);

    memset(h_newcentroids, 0, sBytes);
    memset(h_counter,  0, tBytes);

    // malloc device global memory
    int *d_data, *d_centroids;
    CHECK(cudaMalloc((int**)&d_data, nBytes));
    CHECK(cudaMalloc((int**)&d_centroids, cBytes));
    int *d_newcentroids;
    CHECK(cudaMalloc((int**)&d_newcentroids, sBytes));
    int *d_counter;
    CHECK(cudaMalloc((int**)&d_counter, tBytes));

    // transfer data from host to device
    CHECK(cudaMemcpy(d_data, h_data, nBytes, cudaMemcpyHostToDevice));
    CHECK(cudaMemcpy(d_centroids, h_centroids, cBytes, cudaMemcpyHostToDevice));
    CHECK(cudaMemcpy(d_newcentroids, h_newcentroids, sBytes, cudaMemcpyHostToDevice));
    CHECK(cudaMemcpy(d_counter, h_counter, tBytes, cudaMemcpyHostToDevice));

    // invoke kernel at host side
    int iLen = 256;
    dim3 block (iLen);
    dim3 grid  (((nElem/Dim + block.x - 1) / block.x));
	for (int i=0;i < 20; i++) {
		kmeans<<<grid, block>>>(d_data, d_centroids, d_newcentroids, d_counter, nElem);
		CHECK(cudaDeviceSynchronize());
		printf("kmeans <<<  %d, %d  >>>  \n", grid.x,
			   block.x);
		// check kernel error
		CHECK(cudaGetLastError()) ;
		// copy kernel result back to host side
		CHECK(cudaMemcpy(h_newcentroids, d_newcentroids, sBytes, cudaMemcpyDeviceToHost));
		CHECK(cudaMemcpy(h_counter, d_counter, tBytes, cudaMemcpyDeviceToHost));
		
		for (int j=0; j < k*Dim; j++) {
		   printf(" centroids dim %d value %d  \n", j, h_centroids[j]);    
		   h_centroids[j] = (int) (h_newcentroids[j]/h_counter[j/2]);
		   if (j % 2) printf(" counter j %d =  %d  \n", j/2, h_counter[j/2]);
		}
		
		memset(h_newcentroids, 0, sBytes);
		memset(h_counter,  0, tBytes);
		CHECK(cudaMemcpy(d_centroids, h_centroids, cBytes, cudaMemcpyHostToDevice));
		CHECK(cudaMemcpy(d_newcentroids, h_newcentroids, sBytes, cudaMemcpyHostToDevice));
		CHECK(cudaMemcpy(d_counter, h_counter, tBytes, cudaMemcpyHostToDevice));
  }
    // check device results

    // free device global memory
    CHECK(cudaFree(d_data));
    CHECK(cudaFree(d_centroids));
    CHECK(cudaFree(d_newcentroids));
    CHECK(cudaFree(d_counter));

    // free host memory
    free(h_data);
    free(h_centroids);
    free(h_newcentroids);
    free(h_counter);

	r = r + 1;
    return(0);
}
