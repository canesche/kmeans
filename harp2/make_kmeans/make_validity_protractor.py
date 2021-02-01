from math import ceil, log2

from veriloggen import *


def make_validity_protractor(external_data_width, data_width, k, dimensions):
    m = Module('validity_protractor')

    # ceil(log2(k)) = reduce min
    # +1 = quad
    #+1 = sub
    # ceil(log2(dimensions)) = reduce ADD
    # (0 if k < 3 else ceil(log2(k)) - 1) = regs
    dfg_depth = ceil(log2(k)) + 2 + ceil(log2(dimensions)) + (0 if k < 3 else ceil(log2(k)) - 1)

    clk = m.Input('clk')
    rst = m.Input('rst')

    validity_protractor_input_valid = m.Input('validity_protractor_input_valid', 2)
    validity_protractor_output_valid = m.OutputReg('validity_protractor_output_valid', 2)

    m.EmbeddedCode(' ')
    m.EmbeddedCode('//Transfer of data validity control signals.')
    valid = m.Reg('valid', dfg_depth * 2)
    # validity_protractor_output_valid.assign(valid[0:2]),

    m.Always(Posedge(clk))(
        If(rst)(
            valid(Int(0, valid.width, 10)),
            validity_protractor_output_valid(Int(0, validity_protractor_output_valid.width, 10)),
        ).Else(
            valid(Cat(validity_protractor_input_valid, valid[2:valid.width])),
            validity_protractor_output_valid(valid[0:2]),
        )
    )

    return m
