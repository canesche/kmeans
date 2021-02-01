from veriloggen import *

from make_kmeans_top import make_kmeans_top
from util import validate_configurations, split_modules


def make_kmeans_acc(external_data_width, data_width, k, dimensions, output_path):
    # Verificação do preenchimento total da linha de cache pelo circuito.
    if not validate_configurations(external_data_width, data_width, dimensions):
        print('Erro de geração')
        print('A geração do circuito depende do preenchimento completo da linha de cache fornecida.')
        print('')
        exit(1)

    m = Module('acc_user_0')

    # Paraâmetros para compatibilidade com a interface. Estes não estão sendo utilizados no projeto atual.
    DATA_WIDTH = m.Parameter('DATA_WIDTH', data_width)
    NUM_INPUT_QUEUES = m.Parameter('NUM_INPUT_QUEUES', 1)
    NUM_OUTPUT_QUEUES = m.Parameter('NUM_OUTPUT_QUEUES', 1)

    # sinais básicos para o funcionamento do circuito
    clk = m.Input('clk')
    rst = m.Input('rst')
    start = m.Input('start')

    acc_user_done_rd_data = m.Input('acc_user_done_rd_data', 1)
    acc_user_done_wr_data = m.Input('acc_user_done_wr_data', 1)
    acc_user_available_read = m.Input('acc_user_available_read', 1)
    acc_user_read_data = m.Input('acc_user_read_data', external_data_width)
    acc_user_request_read = m.Output('acc_user_request_read', 1)
    acc_user_read_data_valid = m.Input('acc_user_read_data_valid', 1)
    acc_user_available_write = m.Input('acc_user_available_write', 1)
    acc_user_write_data = m.Output('acc_user_write_data', external_data_width)
    acc_user_request_write = m.Output('acc_user_request_write', 1)
    acc_user_done = m.OutputReg('acc_user_done', 1)

    kmeans = make_kmeans_top(external_data_width, data_width, k, dimensions)
    params = []
    con = [('clk', clk), ('rst', rst), ('start', start), ('kmeans_top_done_rd_data', acc_user_done_rd_data),
           ('kmeans_top_done_wr_data', acc_user_done_wr_data), ('kmeans_top_available_read', acc_user_available_read),
           ('kmeans_top_read_data', acc_user_read_data), ('kmeans_top_request_read', acc_user_request_read),
           ('kmeans_top_read_data_valid', acc_user_read_data_valid),
           ('kmeans_top_available_write', acc_user_available_write),
           ('kmeans_top_write_data', acc_user_write_data), ('kmeans_top_request_write', acc_user_request_write),
           ('kmeans_top_done', acc_user_done)]

    m.Instance(kmeans, 'kmeans_top', params, con)

    split_modules(m.to_verilog(), output_path)
