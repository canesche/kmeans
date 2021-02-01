from veriloggen import *


def make_component_quad():
    m = Module('m_quad')

    data_width_in = m.Parameter('DATA_WIDTH_IN', 16)
    data_width_out = m.Parameter('DATA_WIDTH_OUT', 16)
    centroid_id_width = m.Parameter('CENTROID_ID_WIDTH', 8)

    clk = m.Input('clk')
    data_in_0 = m.Input('data_in_0', data_width_in + centroid_id_width)
    data_out = m.OutputReg('data_out', data_width_out)

    m.EmbeddedCode('//Separation of the centroid ID values from the data to be processed')
    data_0 = m.Wire('data_0', data_width_in * 2)
    centroid_id = m.Wire('centroid_id', centroid_id_width)

    m.EmbeddedCode(' ')
    m.EmbeddedCode('//Assigns')

    data_0.assign(Cat(Repeat(data_in_0[data_width_in - 1], data_width_in), data_in_0[0:data_width_in]))

    centroid_id.assign(data_in_0[data_width_in:data_width_in + centroid_id_width])

    m.Always(Posedge(clk))(
        data_out(Cat(centroid_id, Repeat(Int(0, 1, 2), (data_width_out - (data_width_in * 2) - centroid_id_width)),
                     (data_0 * data_0)))
    )
    return m
