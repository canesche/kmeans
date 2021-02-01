from veriloggen import *


def make_output_controller(external_data_width, data_width, dimensions):
    m = Module('output_controller')

    controller_data_width = 8
    num_inputs = (external_data_width // data_width) // dimensions

    # basic signals BEGIN
    clk = m.Input('clk')
    rst = m.Input('rst')
    start = m.Input('start')
    # basic signals END

    # fifo_out control BEGIN [1-1:0] acc_user_wr_en,
    output_controller_available_write = m.Input('output_controller_available_write')
    output_controller_request_write = m.OutputReg('output_controller_request_write')
    output_controller_write_data = m.OutputReg('output_controller_write_data', external_data_width)
    # fifo_out control END

    # inputdata BEGIN
    output_controller_input_valid = m.Input('output_controller_input_valid', 2)
    output_controller_data_in = m.Input('output_controller_data_in', controller_data_width * num_inputs)
    # inputdata END

    # DONE signal
    output_controller_done = m.OutputReg('output_controller_done')

    if (external_data_width == controller_data_width * num_inputs):
        m.Always(Posedge(clk))(
            If(rst)(
                output_controller_request_write(Int(0, 1, 2)),
                output_controller_done(Int(0, 1, 2)),
            ).Elif(AndList(start, Not(output_controller_done)))(
                EmbeddedCode('//Stop = 00, Done = 10, Valid = 01'),
                output_controller_request_write(Int(0, 1, 10)),
                If(output_controller_available_write)(
                    Case(output_controller_input_valid)(
                        When(Int(2, output_controller_input_valid.width, 10))(  # Done = 2
                            output_controller_done(Int(1, 1, 10)),
                        ),
                        When(Int(1, output_controller_input_valid.width, 10))(  # Valid = 1
                            output_controller_write_data(output_controller_data_in),
                            output_controller_request_write(Int(1, 1, 10)),
                        )
                    )
                )
            )
        )
    else:
        m.EmbeddedCode(" ")
        data = m.Reg('data', external_data_width)
        counter = m.Reg('counter', 10)
        wr_flag = m.Reg("wr_flag")

        m.Always(Posedge(clk))(
            If(rst)(
                output_controller_request_write(Int(0, 1, 10)),
                counter(Int(0, counter.width, 10)),
                data(Int(0, data.width, 10)),
                output_controller_write_data(Int(0, output_controller_write_data.width, 10)),
                wr_flag(Int(0, 1, 10)),
                output_controller_done(Int(0, 1, 10)),
            ).Elif(AndList(start, Not(output_controller_done)))(
                EmbeddedCode('//Stop = 00, Done = 10, Valid = 01'),
                output_controller_request_write(Int(0, 1, 10)),
                If(output_controller_available_write)(
                    Case(output_controller_input_valid)(
                        When(Int(2, 2, 10))(  # Done = 2
                            If(counter >= Int((external_data_width // (controller_data_width * num_inputs)) - 1,
                                              counter.width,
                                              10))(
                                counter(Int(0, counter.width, 10)),
                                output_controller_write_data(
                                    Cat(output_controller_data_in,
                                        data[controller_data_width * num_inputs:external_data_width])),
                                output_controller_request_write(Int(1, 1, 10)),
                                wr_flag(Int(1, 1, 10)),
                            ).Elif(OrList(wr_flag, counter == Int(0, counter.width, 10)))(
                                output_controller_done(Int(1, 1, 10)),
                            ).Else(
                                counter(counter + Int(1, counter.width, 10)),
                                data(Cat(Int(0, controller_data_width * num_inputs, 10),
                                         data[controller_data_width * num_inputs:external_data_width])),
                            ),
                        ),
                        When(Int(1, 2, 10))(  # Valid = 1
                            If(counter >= Int((external_data_width // (controller_data_width * num_inputs)) - 1,
                                              counter.width,
                                              10))(
                                counter(Int(0, counter.width, 10)),
                                output_controller_write_data(
                                    Cat(output_controller_data_in,
                                        data[controller_data_width * num_inputs:external_data_width])),
                                data(Int(0, data.width, 10)),
                                output_controller_request_write(Int(1, 1, 10)),
                            ).Else(
                                counter(counter + Int(1, counter.width, 10)),
                                data(Cat(output_controller_data_in,
                                         data[controller_data_width * num_inputs:external_data_width])),
                            ),
                        )
                    )
                )
            )
        )

    return m
