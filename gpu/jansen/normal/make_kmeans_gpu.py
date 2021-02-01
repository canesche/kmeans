def ident(level):
    qtde_spaces = 4
    spaces = ""
    for i in range(level * qtde_spaces):
        spaces = spaces + " "
    return spaces


def update_string(string_base, ident_level, insert_string):
    string_base = string_base + "\n" + ident(ident_level) + insert_string
    return string_base


def insert_blank_line(string_base):
    return string_base + "\n"


def generate_initial_part():
    ident_level = 0
    string_base = ""
    string_base = update_string(string_base, ident_level, "#include \"common.h\"")
    string_base = update_string(string_base, ident_level, "#include <cuda_runtime.h>")
    string_base = update_string(string_base, ident_level, "#include <stdio.h>")
    string_base = update_string(string_base, ident_level, "#include <iostream>")
    string_base = update_string(string_base, ident_level, "#include <vector>")
    string_base = update_string(string_base, ident_level, "#include <fstream>")
    string_base = update_string(string_base, ident_level, "#include <sstream>")
    string_base = update_string(string_base, ident_level, "#include <chrono>")
    string_base = insert_blank_line(string_base)
    string_base = update_string(string_base, ident_level, "//this define cam be changed.")
    string_base = update_string(string_base, ident_level, "#define THREAD_PER_BLOCK 256")
    return string_base


def generate_defines(string_base, dim, k):
    ident_level = 0
    string_base = insert_blank_line(string_base)
    string_base = update_string(string_base, ident_level, "//these defines should not be changed")
    string_base = update_string(string_base, ident_level, "#define DIM " + str(dim))
    string_base = update_string(string_base, ident_level, "#define CENT " + str(k))
    return string_base


def generate_kernel_head(string_base):
    ident_level = 0
    string_base = insert_blank_line(string_base)
    string_base = update_string(string_base, ident_level, "using namespace std;")
    string_base = update_string(string_base, ident_level, "using namespace std::chrono;")
    string_base = insert_blank_line(string_base)
    string_base = update_string(string_base, ident_level,
                                "__global__ void kmeans(int *input, int *centroids, int *newcentroids, int *counter, const int n) {")
    ident_level = ident_level + 1
    string_base = update_string(string_base, ident_level, "int i = (blockIdx.x * blockDim.x + threadIdx.x) * DIM;")
    string_base = update_string(string_base, ident_level, "if (i < n) {")

    return string_base


def generate_map(string_base, dim, k):
    ident_level = 2
    string_base = update_string(string_base, ident_level, "//MAP")

    # points
    for i in range(dim):
        string_base = update_string(string_base, ident_level, "int point_d" + str(i) + " = input[i + " + str(i) + "];")
    for c in range(k):
        for i in range(dim):
            string_base = update_string(string_base, ident_level, "int k" + str(c) + "_d" + str(i) + " = point_d" + str(
                i) + " - centroids[" + str((c * dim) + i) + "];")
    for c in range(k):
        for i in range(dim):
            string_base = update_string(string_base, ident_level,
                                        "k" + str(c) + "_d" + str(i) + " *= k" + str(c) + "_d" + str(i) + ";")
    return string_base


def generate_reduce_sum(string_base, dim, k):
    ident_level = 2
    string_base = update_string(string_base, ident_level, "//REDUCE_SUM")

    for c in range(k):
        str_tmp = ""
        for i in range(dim):
            if i == dim - 1:
                str_tmp = str_tmp + " k" + str(c) + "_d" + str(i) + ";"
            else:
                str_tmp = str_tmp + " k" + str(c) + "_d" + str(i) + " +"
        str_tmp = "k" + str(c) + "_d0 = " + str_tmp
        string_base = update_string(string_base, ident_level, str_tmp)

    return string_base


def generate_reduce_min(string_base, dim, k):
    ident_level = 2
    string_base = update_string(string_base, ident_level, "//REDUCE_MIN")
    string_base = update_string(string_base, ident_level, "int min_id = 0;")
    string_base = update_string(string_base, ident_level, "int min = k0_d0;")
    if (k > 1):
        string_base = update_string(string_base, ident_level, "min_id = (k1_d0 < k0_d0) ? 1 : 0;")
        string_base = update_string(string_base, ident_level, "min = (k1_d0 < k0_d0)? k1_d0 : k0_d0;")
        for c in range(2, k):
            string_base = update_string(string_base, ident_level,
                                        "min_id = (k" + str(c) + "_d0 < min)? " + str(c) + " : min_id;")
            if (c < k - 1):
                string_base = update_string(string_base, ident_level,
                                            "min = (k" + str(c) + "_d0 < min)? k" + str(c) + "_d0 : min;")

    return string_base


def generate_kernel_foot(string_base, dim):
    ident_level = 2
    string_base = update_string(string_base, ident_level, "//ADD CURRENT POINT TO NEW CENTROIDS SUM")
    for i in range(dim):
        string_base = update_string(string_base, ident_level,
                                    "atomicAdd(&(newcentroids[DIM * min_id + " + str(i) + "]), point_d" + str(i) + ");")
    string_base = update_string(string_base, ident_level, "atomicAdd(&(counter[min_id]), 1);")
    ident_level = 1
    string_base = update_string(string_base, ident_level, "}")
    ident_level = 0
    string_base = update_string(string_base, ident_level, "}")
    string_base = insert_blank_line(string_base)
    string_base = insert_blank_line(string_base)
    return string_base


def concatenate_main(string_base):
    open_file = open("main_base.inc", "r")
    for line in open_file:
        string_base = string_base + line
    return string_base


def save_gpu_code(string_base, k, dim):
    save_file = open("kmeans_gpu_k" + str(k) + "_d" + str(dim) + ".normal.cu", "w")
    save_file.write(string_base)


def make_kmeans_gpu(k, dim):
    if (k == 0 or dim == 0):
        print("Error: K and DIM needs to be greater than 0.")
        exit(1)

    ident_level = 0
    gpu = generate_initial_part()
    gpu = generate_defines(gpu, dim, k)
    gpu = generate_kernel_head(gpu)
    gpu = generate_map(gpu, dim, k)
    gpu = generate_reduce_sum(gpu, dim, k)
    gpu = generate_reduce_min(gpu, dim, k)
    gpu = generate_kernel_foot(gpu, dim)
    gpu = concatenate_main(gpu)
    save_gpu_code(gpu, k, dim)
    # print(gpu)
