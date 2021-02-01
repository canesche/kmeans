from veriloggen import *


def make_component_imm():
    m = Module('m_imm')

    data_width = m.Parameter('DATA_WIDTH', 16)
    centroid_id_width = m.Parameter('CENTROID_ID_WIDTH', 8)
    centroid_id = m.Parameter('CENTROID_ID', 0)
    imm_id_width = m.Parameter('IMM_ID_WIDTH', 8)
    IMM_ID = m.Parameter('IMM_ID', 0)
    configuration_id_width = m.Parameter('CONF_ID_WIDTH', 32)

    clk = m.Input('clk')
    centroid_configuration_in = m.Input('centroid_configuration_in', 64)
    data_out = m.Output('data_out', data_width)

    immediate = m.Reg('immediate', data_width - centroid_id_width)

    m.EmbeddedCode(' ')
    m.EmbeddedCode('//Output assign')

    data_out.assign(Cat(centroid_id, immediate))

    m.Always(Posedge(clk))(
        If(centroid_configuration_in[0:imm_id_width] == IMM_ID)(
            immediate(centroid_configuration_in[
                      configuration_id_width:configuration_id_width + data_width - centroid_id_width])
        )
    )

    return m
