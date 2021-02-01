from normal.make_kmeans_gpu import make_kmeans_gpu as normal_make
from shared.make_kmeans_gpu import make_kmeans_gpu as shared_make

if __name__ == '__main__':

    k = 2

    while k <= 64:
        dim = 2
        while dim <= 64:
            normal_make(k, dim)
            dim = dim * 2
        k = k * 2


    k = 2

    while k <= 64:
        dim = 2
        while dim <= 64:
            shared_make(k, dim)
            dim = dim * 2
        k = k * 2
