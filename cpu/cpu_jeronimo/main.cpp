#include <stdio.h>
#include <iostream>
#include <vector>
#include <fstream>
#include <sstream>
#include <chrono>
#include <cstring>

using namespace std;
using namespace std::chrono;

int kmeans(int *input, int *centroids, int *centroids_old, int max_it, int k, int dim, int num_points, bool debug,
           std::string *output_text) {
    double timeExec;
    high_resolution_clock::time_point s;
    duration<double> diff{};

    int k_sum[k * dim];
    int k_qtde[k];
    int it;

    for (it = 0; it < max_it; it++) {

        memset(k_sum, 0, sizeof(int) * (k * dim));
        memset(k_qtde, 0, sizeof(int) * (k));
        if (debug) {
            s = high_resolution_clock::now();
        }

        for (int i = 0; i < num_points; i++) {//pra cada ponto
            int min, min_id = 0;
            for (int c = 0; c < k; c++) {//pra cada centroide
                int sum = 0;
                for (int j = 0; j < dim; j++) {//pra cada dimensão
                    int tmp;
                    tmp = centroids[c * dim + j] - input[i * dim + j];
                    tmp *= tmp;
                    sum += tmp;
                }
                if (c > 0) {
                    if (sum < min) {
                        min = sum;
                        min_id = c;
                    }
                } else {
                    min = sum;
                    min_id = c;
                }
            }

            for (int j = 0; j < dim; j++) {
                k_sum[min_id * dim + j] += input[i * dim + j];
            }
            k_qtde[min_id] += 1;
        }

        if (debug) {
            diff = high_resolution_clock::now() - s;
            timeExec = diff.count();

            (*output_text) += "\n1 Iteration Execution Time: " + std::to_string(timeExec * 1000) + "ms";
            return 0;
        }

        int different = 0;
        //atualização dos centroides
        for (int c = 0; c < k; c++) {
            for (int j = 0; j < dim; j++) {
                if (k_qtde[c] > 0) {
                    centroids[c * dim + j] = k_sum[c * dim + j] / k_qtde[c];
                }
                if (centroids[c * dim + j] != centroids_old[c * dim + j]) {
                    different = 1;
                }
                centroids_old[c * dim + j] = centroids[c * dim + j];
            }
        }

        if (different == 0) {
            break;
        }
    }
    return it + 1;
}

int main(int argc, char **argv) {

    int num_points = 10;
    int max_iterations = 10;
    int num_clusters = 2;
    int num_dim = 2;
    std::string data_in_file_path, output_file;
    std::string line;

    if (argc > 5) {
        num_points = atoi(argv[1]);
        num_clusters = atoi(argv[2]);
        max_iterations = atoi(argv[3]);
        num_dim = atoi(argv[4]);
        data_in_file_path = argv[5];
        output_file = "./kmeans_" + std::to_string(num_points) + "_" + std::to_string(num_clusters) +
                      "_" + std::to_string(num_dim) + "_out_cpu" + ".txt";
    } else {
        std::cout << "invalid args!!!\n";
        std::cout << "usage: <num_points> <num_clusters>  <max_iterations> <num_dim> <data_file>\n";
        exit(255);
    }

    //starting
    printf("%s Starting...\n", argv[0]);

    std::ifstream data_in(data_in_file_path);

    // set up data size of vectors
    int nElem = num_dim * num_points;
    size_t cBytes = num_dim * num_clusters * sizeof(int);
    size_t nBytes = nElem * sizeof(int);

    //host vectors alloc
    int *data;
    int *centroids;
    int *centroids_old;

    data = (int *) malloc(nBytes);
    centroids = (int *) malloc(cBytes);
    centroids_old = (int *) malloc(cBytes);

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
            data[data_idx] = a;
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

    double time_sum = 0;
    std::string output_text = "";
    for (int times = 0; times < 11; times++) {

        // adding the initial clusters
        for (int i = 0; i < num_clusters; i++) {
            for (int j = 0; j < num_dim; j++) {
                int value;
                if (j == 0) {
                    value = i;
                } else {
                    value = 0;
                }
                centroids[(i * num_dim) + j] = value;
                centroids_old[(i * num_dim) + j] = value;
            }
        }

        if (times == 10) {
            kmeans(data, centroids, centroids_old, max_iterations, num_clusters, num_dim, num_points, true,
                   &output_text);
            continue;
        }

        //start time counting
        high_resolution_clock::time_point s;
        duration<double> diff{};
        s = high_resolution_clock::now();

        //start kmeans
        int it = kmeans(data, centroids, centroids_old, max_iterations, num_clusters, num_dim, num_points, false,
                        &output_text);

        //end of time count
        diff = high_resolution_clock::now() - s;
        double timeExec = diff.count();

        if (times == 0) {
            output_text = output_text + "Break in iteration " + std::to_string(it) + "\n\n";
            for (int j = 0; j < num_clusters * num_dim; j++) {
                if (j % num_dim == 0) {
                    output_text += "\n\nCluster values: ";
                }
                output_text += std::to_string(centroids[j]) + " ";
            }
            output_text += "\n\nTimes: ";
        }

        output_text += std::to_string(timeExec * 1000) + "ms ";
        if (times > 2) {
            time_sum += timeExec * 1000;
        }
    }

    output_text += "\n\nTime AVG (3º until 10º): " + std::to_string(time_sum / 7) + "ms ";

    std::ofstream data_out;
    data_out.open(output_file);

    data_out << output_text + "\n";

    // free host memory
    free(data);
    free(centroids);
    free(centroids_old);

    //finishing
    printf("%s Finishing...\n", argv[0]);
}
