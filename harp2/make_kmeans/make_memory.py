from veriloggen import *
from math import ceil, log2


def make_memory(k,data_width):
    m = Module('memory_k%d_%db' % (k,data_width))

    # sinais básicos para o funcionamento do circuito
    clk = m.Input('clk')
    wr_en = m.Input('wr_en')
    rd_addr = m.Input('rd_addr', ceil(log2(k)))
    wr_addr = m.Input('wr_addr', ceil(log2(k)))
    input_data = m.Input('input_data', data_width)
    output_data = m.Output('output_data', data_width)

    mem = m.Reg('mem', data_width, k)

    output_data.assign(mem[rd_addr])

    m.Always(Posedge(clk))(
        If(wr_en)(
            mem[wr_addr](input_data)
        )
    )

    return m


#print(make_memory(2).to_verilog())
