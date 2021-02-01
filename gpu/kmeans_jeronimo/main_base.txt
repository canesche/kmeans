int main(int argc, char **argv) {

    int num_points = 10;
    int max_iterations = 10;
    int num_clusters = CENT;
    int num_dim = DIM;
    int iLen = THREAD_PER_BLOCK;
    std::string data_in_file_path, output_file;
    std::string line;

    if (argc > 3) {
        num_points = atoi(argv[1]);
        max_iterations = atoi(argv[2]);
        data_in_file_path = argv[3];
        output_file = "./kmeans_" + std::to_string(num_points) + "_" + std::to_string(num_clusters) +
                      "_" + std::to_string(num_dim) + "_out_gpu" + ".txt";
    } else {
        std::cout << "invalid args!!!" << endl;
        std::cout << "usage: <num_points> <max_iterations> <data_file>"
             << endl;
        exit(255);
    }

    //starting
    printf("%s Starting...\n", argv[0]);
    // set up device
    int dev = 0;
    cudaDeviceProp deviceProp;
    CHECK(cudaGetDeviceProperties(&deviceProp, dev));
    printf("Using Device %d: %s\n", dev, deviceProp.name);
    CHECK(cudaSetDevice(dev));

    std::ifstream data_in(data_in_file_path);

    // set up data size of vectors
    int nElem = num_dim * num_points;
    size_t cBytes = num_dim * num_clusters * sizeof(int);
    size_t nBytes = nElem * sizeof(int);
    size_t tBytes = num_clusters * sizeof(int);

    //host vectors alloc
    int *h_data;
    int *h_centroids;
    int *h_centroids_old;
    int *h_newcentroids;
    int *h_counter;

    h_data = (int *) malloc(nBytes);
    h_centroids = (int *) malloc(cBytes);
    h_centroids_old = (int *) malloc(cBytes);
    h_newcentroids = (int *) malloc(cBytes);
    h_counter = (int *) malloc(tBytes);

    // device vectors alloc
    int *d_data;
    int *d_centroids;
    int *d_newcentroids;
    int *d_counter;
    CHECK(cudaMalloc((int **) &d_data, nBytes));
    CHECK(cudaMalloc((int **) &d_centroids, cBytes));
    CHECK(cudaMalloc((int **) &d_newcentroids, cBytes));
    CHECK(cudaMalloc((int **) &d_counter, tBytes));

    //reading input data
    int data_idx = 0;
    int counter_points = 0;
    while (std::getline(data_in, line)) {

        //uncoment if data is separated by ','
        for (int i = 0; i < line.length(); i++) {
            if (line[i] == ',') {
                line[i] = ' ';
            }
        }

        std::istringstream iss(line);
        int a;

        //exception - the first data is not desirable
        //comment if it is desireble
        iss >> a;

        for (int j = 0; (iss >> a); j++) {
            h_data[data_idx] = a;
            data_idx++;
            if (j + 1 == num_dim) {
                break;
            }
        }

        counter_points++;

        if (counter_points >= num_points) {
            break;
        }
    }
    data_in.close();

    // adding the initial clusters
    for (int i = 0; i < num_clusters; i++) {
        for (int j = 0; j < num_dim; j++) {
            int value;
            if (j == 0) {
                value = i;
            } else {
                value = 0;
            }
            h_centroids[(i * num_dim) + j] = value;
            h_centroids_old[(i * num_dim) + j] = value;
        }
    }

    //start time counting
    high_resolution_clock::time_point s;
    duration<double> diff{};
    s = high_resolution_clock::now();

    //initializing some vectors
    memset(h_newcentroids, 0, cBytes);
    memset(h_counter, 0, tBytes);
    // transfer data from host to device
    CHECK(cudaMemcpy(d_data, h_data, nBytes, cudaMemcpyHostToDevice));
    CHECK(cudaMemcpy(d_centroids, h_centroids, cBytes, cudaMemcpyHostToDevice));
    CHECK(cudaMemcpy(d_newcentroids, h_newcentroids, cBytes, cudaMemcpyHostToDevice));
    CHECK(cudaMemcpy(d_counter, h_counter, tBytes, cudaMemcpyHostToDevice));


    // invoke kernel at host side
    dim3 block(iLen);
    dim3 grid(((nElem / num_dim) + block.x - 1) / block.x);

    //start kmeans
    int i;
    for (i = 0; i < max_iterations; i++) {

        kmeans <<< grid, block >>> (d_data, d_centroids, d_newcentroids, d_counter,  nElem);

        CHECK(cudaDeviceSynchronize());
        // check kernel error
        CHECK(cudaGetLastError());
        // copy kernel result back to host side
        CHECK(cudaMemcpy(h_newcentroids, d_newcentroids, cBytes, cudaMemcpyDeviceToHost));
        CHECK(cudaMemcpy(h_counter, d_counter, tBytes, cudaMemcpyDeviceToHost));

        int different = 0;
        //update of the new centroids
        for (int j = 0; j < num_clusters * num_dim; j++) {
            if (h_counter[j / num_dim] > 0) {
                h_centroids[j] = (int) (h_newcentroids[j] / h_counter[j / num_dim]);
            }
            if(h_centroids[j] != h_centroids_old[j]){
                different = 1;
            }
            h_centroids_old[j] = h_centroids[j];
        }

        if(different == 0){
            break;
        }

        memset(h_newcentroids, 0, cBytes);
        memset(h_counter, 0, tBytes);

        CHECK(cudaMemcpy(d_centroids, h_centroids, cBytes, cudaMemcpyHostToDevice));
        CHECK(cudaMemcpy(d_newcentroids, h_newcentroids, cBytes, cudaMemcpyHostToDevice));
        CHECK(cudaMemcpy(d_counter, h_counter, tBytes, cudaMemcpyHostToDevice));
    }

    //end of time count
    diff = high_resolution_clock::now() - s;
    double timeExec = diff.count();

    std::ofstream data_out;
    data_out.open(output_file);

    data_out << "Break in iteration " << (i+1) << "\n\n";
    data_out << "Total Time: " << timeExec * 1000 << "ms" ;

    for (int j = 0; j < num_clusters * num_dim; j++) {
        if(j % num_dim == 0){
            data_out << endl << endl << "Cluster values: ";
        }
        data_out << h_centroids[j] << " " ;
    }

    // free device global memory
    CHECK(cudaFree(d_centroids));
    CHECK(cudaFree(d_newcentroids));
    CHECK(cudaFree(d_counter));
    CHECK(cudaFree(d_data));

    // free host memory
    free(h_data);
    free(h_centroids);
    free(h_newcentroids);
    free(h_counter);
    //finishing
    printf("%s Finished...\n", argv[0]);
}