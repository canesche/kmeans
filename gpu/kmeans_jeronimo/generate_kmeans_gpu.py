from make_kmeans_gpu import make_kmeans_gpu

if __name__ == '__main__':

    k = 2

    while k < 65:
        dim = 2
        while dim < 65:
            make_kmeans_gpu(k, dim)
            dim = dim * 2
        k = k * 2

