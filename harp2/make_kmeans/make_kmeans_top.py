from veriloggen import *

from make_accumulator import make_accumulator
from make_component_add import make_component_add
from make_component_cmp import make_component_cmp
from make_component_imm import make_component_imm
from make_component_quad import make_component_quad
from make_component_reg import make_component_reg
from make_component_sub import make_component_sub
from make_config_centroids import make_config_centroids
from make_input_controller import make_input_controller
from make_kmeans import make_kmeans
from make_memory import make_memory
from make_output_controller import make_output_controller


def make_kmeans_top(external_data_width, data_width, k_array, dimensions):
    id_width = 32
    conf_width = 32
    output_controller_num_inputs = (external_data_width // data_width) // dimensions
    params = []
    con = []

    m = Module('kmeans_top')

    # sinais básicos para o funcionamento do circuito
    clk = m.Input('clk')
    rst = m.Input('rst')
    start = m.Input('start')

    nKmeans = len(k_array)

    kmeans_top_done_rd_data = m.Input('kmeans_top_done_rd_data', 1)
    kmeans_top_done_wr_data = m.Input('kmeans_top_done_wr_data', 1)
    kmeans_top_available_read = m.Input('kmeans_top_available_read', 1)
    kmeans_top_read_data = m.Input('kmeans_top_read_data', external_data_width)
    kmeans_top_request_read = m.Output('kmeans_top_request_read', 1)
    kmeans_top_read_data_valid = m.Input('kmeans_top_read_data_valid', 1)

    kmeans_top_available_write = m.Input('kmeans_top_available_write', nKmeans)
    kmeans_top_write_data = m.Output('kmeans_top_write_data', nKmeans * external_data_width)
    kmeans_top_request_write = m.Output('kmeans_top_request_write', nKmeans)
    kmeans_top_done = m.Output('kmeans_top_done', nKmeans)

    m.EmbeddedCode('//Basic wires for initial configuration and circuit execution')
    request_read = m.Wire('request_read')
    kmeans_top_request_read[0].assign(request_read)
    start_circuit = m.Wire('start_circuit')

    m.EmbeddedCode(' ')
    m.EmbeddedCode('//config_centroids wires')
    config_centroids_request_read = m.Wire('config_centroids_request_read')
    config_centroids_start_circuit = m.Wire('config_centroids_start_circuit')
    config_centroids_configurations_out = m.Wire('config_centroids_configurations_out', 64)

    m.EmbeddedCode(' ')
    m.EmbeddedCode('//input controller wires')
    input_controller_request_read = m.Wire('input_controller_request_read')
    input_controller_data_out = m.Wire('input_controller_data_out', external_data_width)
    input_controller_output_valid = m.Wire('input_controller_output_valid', 2)

    m.EmbeddedCode(' ')
    m.EmbeddedCode('//output controller wires')
    output_controller_input_valid = m.Wire('output_controller_input_valid', 2, nKmeans)
    output_controller_data_in = m.Wire('output_controller_data_in', output_controller_num_inputs * 8, nKmeans)

    m.EmbeddedCode(' ')
    m.EmbeddedCode('//assigns')
    request_read.assign(config_centroids_request_read | input_controller_request_read)
    start_circuit.assign(config_centroids_start_circuit)

    m.EmbeddedCode(' ')
    m.EmbeddedCode('//Config Centroid Instantiation')
    config_centroids = make_config_centroids(external_data_width)
    con = [('clk', clk), ('rst', rst), ('start', start),
           ('config_centroids_available_read', kmeans_top_available_read[0]),
           ('config_centroids_read_data', kmeans_top_read_data),
           ('config_centroids_request_read', config_centroids_request_read),
           ('config_centroids_read_data_valid', kmeans_top_read_data_valid[0]),
           ('config_centroids_start_circuit', config_centroids_start_circuit),
           ('config_centroids_configurations_out', config_centroids_configurations_out)]
    m.Instance(config_centroids, 'config_centroids', params, con)

    m.EmbeddedCode(' ')
    m.EmbeddedCode('//Input Controller Instantiation')

    input_controller = make_input_controller(external_data_width)
    con = [('clk', clk), ('rst', rst), ('start', start_circuit), ('done_rd_data', kmeans_top_done_rd_data[0]),
           ('input_controller_available_read', kmeans_top_available_read[0]),
           ('input_controller_read_data', kmeans_top_read_data),
           ('input_controller_read_data_valid', kmeans_top_read_data_valid[0]),
           ('input_controller_request_read', input_controller_request_read),
           ('input_controller_data_out', input_controller_data_out),
           ('input_controller_output_valid', input_controller_output_valid)]
    m.Instance(input_controller, 'input_controller', params, con)

    m.EmbeddedCode(' ')
    m.EmbeddedCode('//Kmeans Cores Instantiation')

    components_array = {}
    components_array['ADD'] = make_component_add()
    components_array['CMP'] = make_component_cmp()
    components_array['IMM'] = make_component_imm()
    components_array['QUAD'] = make_component_quad()
    components_array['SUB'] = make_component_sub()
    components_array['REG'] = make_component_reg()
    components_array['MEM'] = make_memory(k_array[0])
    components_array['ACC'] = make_accumulator(k_array[0], dimensions)

    count = 0
    kmeans_array = {}
    for k in k_array:
        if (k not in kmeans_array.keys()):
            kmeans_array[k] = make_kmeans(external_data_width, data_width, k, sum(k_array), dimensions, components_array)
        kmeans = kmeans_array[k]

        con = [('clk', clk), ('rst', rst),
               ('kmeans_centroids_configurations_in', config_centroids_configurations_out),
               ('kmeans_data_in', input_controller_data_out),
               ('kmeans_input_valid', input_controller_output_valid),
               ('kmeans_data_out', output_controller_data_in[count]),
               ('kmeans_output_valid', output_controller_input_valid[count])]
        m.Instance(kmeans, 'kmeans_%d_%d' % (count, k), params, con)

        m.EmbeddedCode(' ')
        m.EmbeddedCode('//Output Controller Instantiation')

        '''output_controller = make_output_controller(external_data_width, data_width, dimensions)
        con = [('clk', clk), ('rst', rst), ('start', start_circuit),
               ('output_controller_available_write', kmeans_top_available_write[count]),
               ('output_controller_request_write', kmeans_top_request_write[count]),
               ('output_controller_write_data',
                kmeans_top_write_data[count * external_data_width:(count + 1) * external_data_width]),
               ('output_controller_input_valid', output_controller_input_valid[count]),
               ('output_controller_data_in', output_controller_data_in[count]),
               ('output_controller_done', kmeans_top_done[count])]
        m.Instance(output_controller, 'output_controller_%d_%d' % (count, k), params, con)
        '''
        count = count + 1

    return m
