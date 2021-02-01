CU_APPS=kmeans_v1_original kmeans_v2_original kmeans_d2_n2

all: ${CU_APPS}

%: %.cu
	nvcc -O2 -arch=sm_35 -o $@ $<
%: %.c
	gcc -O2 -std=c99 -o $@ $<
clean:
	rm -f ${CU_APPS}
