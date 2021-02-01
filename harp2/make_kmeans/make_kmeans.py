from veriloggen import *

from make_kmeans_core import make_kmeans_core
from make_validity_protractor import make_validity_protractor


def make_kmeans(external_data_width, data_width, k, sumK, dimensions, components_array):
    m = Module('kmeans_%d' % k)

    controller_data_width = 8
    kmeans_cores = (external_data_width // data_width) // dimensions
    params = []

    # sinais básicos para o funcionamento do circuito
    clk = m.Input('clk')
    rst = m.Input('rst')

    kmeans_centroids_configurations_in = m.Input('kmeans_centroids_configurations_in', 64)
    kmeans_data_in = m.Input('kmeans_data_in', external_data_width)
    kmeans_input_valid = m.Input('kmeans_input_valid', 2)
    kmeans_data_out = m.Output('kmeans_data_out', kmeans_cores * controller_data_width)
    kmeans_output_valid = m.OutputReg('kmeans_output_valid', 2)

    m.EmbeddedCode(' ')
    m.EmbeddedCode('//Validity_protractor instantiation.')

    validity_protractor = make_validity_protractor(external_data_width, data_width, k, dimensions)
    con = [('clk', clk), ('rst', rst),
           ('validity_protractor_input_valid', kmeans_input_valid),
           ('validity_protractor_output_valid', kmeans_output_valid)]
    m.Instance(validity_protractor, 'validity_protractor', params, con)

    kmeans_core = make_kmeans_core(data_width, k,sumK, dimensions, components_array)
    for i in range(0, kmeans_cores):
        m.EmbeddedCode(' ')
        m.EmbeddedCode('//kmeans_core core %d Instantiation' % i)

        con = [('clk', clk), ('rst', rst),
               ('kmeans_core_centroids_configurations_in', kmeans_centroids_configurations_in),
               ('kmeans_core_data_in', kmeans_data_in[(i * data_width * dimensions):(i * data_width * dimensions) + (
                       data_width * dimensions)]),
               ('kmeans_core_data_out',
                kmeans_data_out[(i * controller_data_width):(i * controller_data_width) + controller_data_width])]
        m.Instance(kmeans_core, 'kmeans_core_%d' % i, params, con)

    return m
