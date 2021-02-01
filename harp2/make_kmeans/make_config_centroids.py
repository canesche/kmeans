from veriloggen import *


def make_config_centroids(external_data_width):
    m = Module('config_centroids')

    # sinais básicos para o funcionamento do circuito
    clk = m.Input('clk')
    rst = m.Input('rst')
    start = m.Input('start')

    config_centroids_available_read = m.Input('config_centroids_available_read')
    config_centroids_read_data = m.Input('config_centroids_read_data', external_data_width)
    config_centroids_request_read = m.OutputReg('config_centroids_request_read')
    config_centroids_read_data_valid = m.Input('config_centroids_read_data_valid')

    config_centroids_start_circuit = m.OutputReg('config_centroids_start_circuit')
    config_centroids_configurations_out = m.OutputReg('config_centroids_configurations_out', 64)

    m.EmbeddedCode('//For Config Control')
    fsm_config = m.Reg('fsm_config', 4)
    FSM_IDLE_CONF = m.Localparam('FSM_IDLE_CONF', Int(0, fsm_config.width, 10))
    FSM_READ_NUM_CONF = m.Localparam('FSM_READ_NUM_CONF', Int(1, fsm_config.width, 10))
    FSM_WAIT_CONF = m.Localparam('FSM_WAIT_CONF', Int(2, fsm_config.width, 10))
    FSM_READ_CONF = m.Localparam('FSM_READ_CONF', Int(3, fsm_config.width, 10))
    FSM_CONFIGURE = m.Localparam('FSM_CONFIGURE', Int(4, fsm_config.width, 10))
    FSM_CONF_FINISHED = m.Localparam('FSM_CONF_FINISHED', Int(5, fsm_config.width, 10))

    m.EmbeddedCode(' ')
    data_received = m.Reg('data_received', external_data_width)
    counter_end_line = m.Reg('counter_end_line', 9)
    counter_configurations = m.Reg('counter_configurations', 32)
    num_configurations = m.Reg('num_configurations', 32)

    # confControl
    m.EmbeddedCode('//confControl')

    m.Always(Posedge(clk))(
        If(rst)(
            config_centroids_start_circuit(Int(0, 1, 10)),
            config_centroids_request_read(Int(0, 1, 10)),
            config_centroids_configurations_out(Int(0, config_centroids_configurations_out.width, 10)),
            data_received(Int(0, data_received.width, 10)),
            counter_end_line(Int(0, counter_end_line.width, 10)),
            counter_configurations(Int(0, counter_configurations.width, 10)),
            num_configurations(Int(0, num_configurations.width, 10)),
            fsm_config(FSM_IDLE_CONF),
        ).Elif(start)(
            config_centroids_request_read(Int(0, 1, 2)),
            Case(fsm_config)(
                When(FSM_IDLE_CONF)(
                    If(config_centroids_available_read[0])(
                        config_centroids_request_read(Int(1, 1, 2)),
                        fsm_config(FSM_READ_NUM_CONF),
                    )
                ),
                When(FSM_READ_NUM_CONF)(
                    If(config_centroids_read_data_valid[0])(
                        num_configurations(config_centroids_read_data[0:num_configurations.width]),
                        fsm_config(FSM_WAIT_CONF)
                    )
                ),
                When(FSM_WAIT_CONF)(
                    If(counter_configurations >= num_configurations)(
                        fsm_config(FSM_CONF_FINISHED)
                    ).Elif(config_centroids_available_read[0])(
                        config_centroids_request_read(Int(1, 1, 2)),
                        fsm_config(FSM_READ_CONF),
                    )
                ),
                When(FSM_READ_CONF)(
                    If(config_centroids_read_data_valid[0])(
                        data_received(config_centroids_read_data),
                        counter_end_line(Int(0, counter_end_line.width, 10)),
                        fsm_config(FSM_CONFIGURE)
                    )
                ),
                When(FSM_CONFIGURE)(
                    config_centroids_configurations_out(data_received[0: 64]),
                    data_received(data_received >> Int(64, 10, 10)),
                    counter_end_line(counter_end_line + Int(1, counter_end_line.width, 2)),
                    counter_configurations(counter_configurations + Int(1, counter_configurations.width, 2)),
                    If(counter_end_line == Int((external_data_width // (64)) - 1, counter_end_line.width, 10))(
                        fsm_config(FSM_WAIT_CONF),
                    ).Else(
                        fsm_config(FSM_CONFIGURE),
                    ),
                ),
                When(FSM_CONF_FINISHED)(
                    config_centroids_configurations_out(Int(0, config_centroids_configurations_out.width, 10)),
                    config_centroids_start_circuit(Int(1, 1, 2)),
                    fsm_config(FSM_CONF_FINISHED),
                ),
            )
        )
    )

    return m
