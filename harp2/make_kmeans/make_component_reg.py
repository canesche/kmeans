from veriloggen import *


def make_component_reg():
    m = Module('m_reg')
    data_width = m.Parameter('DATA_WIDTH', 16)
    clk = m.Input('clk')
    data_in_0 = m.Input('data_in_0', data_width)
    data_out = m.OutputReg('data_out', data_width)

    m.Always(Posedge(clk))(
        data_out(data_in_0)
    )

    return m
