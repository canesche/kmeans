from veriloggen import *


# Component that receives the input buffer BEGIN
def make_input_controller(external_data_width):
    m = Module('input_controller')

    # sinais básicos para o funcionamento do circuito
    clk = m.Input('clk')
    rst = m.Input('rst')
    start = m.Input('start')
    done_rd_data = m.Input('done_rd_data')

    # fifo_in control
    input_controller_available_read = m.Input('input_controller_available_read')
    input_controller_read_data = m.Input('input_controller_read_data', external_data_width)
    input_controller_read_data_valid = m.Input('input_controller_read_data_valid')
    input_controller_request_read = m.OutputReg('input_controller_request_read')

    # output
    input_controller_data_out = m.OutputReg('input_controller_data_out', external_data_width)
    input_controller_output_valid = m.OutputReg('input_controller_output_valid', 2)

    m.EmbeddedCode(' ')
    fsm_main = m.Reg('fsm_main', 3)
    FSM_IDLE = m.Localparam('FSM_IDLE', Int(0, fsm_main.width, 10))
    FSM_READ = m.Localparam('FSM_READ', Int(1, fsm_main.width, 10))
    FSM_DONE = m.Localparam('FSM_DONE', Int(2, fsm_main.width, 10))

    m.EmbeddedCode(' ')
    m.Always(Posedge(clk))(
        If(rst)(
            input_controller_data_out(Int(0, input_controller_data_out.width, 10)),
            input_controller_request_read(Int(0, 1, 2)),
            input_controller_output_valid(Int(0, input_controller_output_valid.width, 10)),
            fsm_main(FSM_IDLE),
        ).Elif(start)(
            input_controller_request_read(Int(0, 1, 2)),
            input_controller_output_valid(Int(0, input_controller_output_valid.width, 10)),
            Case(fsm_main)(
                When(FSM_IDLE)(
                    If(input_controller_available_read)(
                        input_controller_request_read(Int(1, 1, 2)),
                        fsm_main(FSM_READ),
                    ).Elif(AndList(done_rd_data, Not(input_controller_available_read)))(
                        fsm_main(FSM_DONE),
                    )
                ),
                When(FSM_READ)(
                    If(input_controller_read_data_valid)(
                        input_controller_data_out(input_controller_read_data),
                        input_controller_output_valid(Int(1, input_controller_data_out.width, 10)),
                        fsm_main(FSM_IDLE),
                        If(input_controller_available_read)(
                            input_controller_request_read(Int(1, 1, 2)),
                            fsm_main(FSM_READ),
                        ),
                    )
                ),
                When(FSM_DONE)(
                    input_controller_output_valid(Int(2, input_controller_data_out.width, 10)),
                    fsm_main(FSM_DONE),
                ),
            )
        )
    )

    return m
