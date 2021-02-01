from veriloggen import *


def make_component_sub():
    m = Module('m_sub')
    data_width = m.Parameter('DATA_WIDTH', 16)
    centroid_id_width = m.Parameter('CENTROID_ID_WIDTH', 8)
    clk = m.Input('clk')
    data_in_0 = m.Input('data_in_0', data_width)
    data_in_1 = m.Input('data_in_1', data_width)
    data_out = m.OutputReg('data_out', data_width)

    m.EmbeddedCode('//Separation of the centroid ID values from the data to be processed')
    data_0 = m.Wire('data_0', data_width - centroid_id_width)
    data_1 = m.Wire('data_1', data_width - centroid_id_width)
    centroid_id = m.Wire('centroid_id', centroid_id_width)

    m.EmbeddedCode(' ')
    m.EmbeddedCode('//Assigns')
    data_0.assign(data_in_0[0:data_width - centroid_id_width])
    data_1.assign(data_in_1[0:data_width - centroid_id_width])
    centroid_id.assign(
        data_in_0[data_width - centroid_id_width:data_width] | data_in_1[data_width - centroid_id_width:data_width])

    m.Always(Posedge(clk))(
        data_out(Cat(centroid_id, (data_0 - data_1)))
    )
    return m
