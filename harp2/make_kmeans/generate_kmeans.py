from make_kmeans_acc import make_kmeans_acc
from util import generate_kmeans_core

external_data_width = 512
data_width = 16
dim = 2
c= 2
k = [c]

#output_path = '/home/jeronimo/GIT/kmeans_examples/kmeans_k' + str(c) + '_d' + str(dim) + '/hw/rtl/acc0/'
output_path = 'verilog'

make_kmeans_acc(external_data_width, data_width, k, dim, output_path)

#generate_kmeans_core(c, dim)