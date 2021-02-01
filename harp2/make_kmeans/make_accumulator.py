from veriloggen import *
from math import ceil, log2

from make_memory import make_memory
from util import split_modules


def make_accumulator(k, dimensions, data_width, memory):
    con = []
    param = []

    memory_data_width = 48 * (dimensions + 1)

    m = Module('accumulator_k%d_d%d' % (k, dimensions))

    clk = m.Input('clk')
    rst = m.Input('rst')
    centroide = m.Input('centroide', ceil(log2(k)))
    data_in_valid = m.Input('data_in_valid', 2)
    data_in = m.Input('data_in', 48 * dimensions)
    data_out_valid = m.OutputReg('data_out_valid', 2)
    data_out = m.OutputReg('data_out', 64 )

    # regs for memories
    m.EmbeddedCode('//REGs e WIRES for memory manipulation')
    wr_en = m.Reg('wr_en')
    rd_addr = m.Wire('rd_addr', ceil(log2(k + 1)))
    wr_addr = m.Reg('wr_addr', ceil(log2(k + 1)))
    mem_input_data = m.Reg('mem_input_data', memory_data_width)
    mem_sum_data = m.Wire('mem_sum_data', memory_data_width)
    mem_output_data = m.Reg('mem_output_data', memory_data_width)
    mem_output_frag_data = m.Reg('mem_output_frag_data', memory_data_width)
    rd_reg = m.Reg('rd_reg', ceil(log2(k + 1)))
    auto_rd = m.Reg('auto_rd')

    # parameters for FSM
    m.EmbeddedCode('')
    m.EmbeddedCode('//FSM_MAIN')
    fsm_main = m.Reg('fsm_main', 4)

    m.EmbeddedCode('')
    m.EmbeddedCode('//Counters for reset memory, reduce memory values and fragment mwmory output word')
    rst_counter = m.Reg('rst_counter', ceil(log2(k + 1)))
    reduce_counter = m.Reg('reduce_counter', ceil(log2(k + 1)))
    word_counter = m.Reg('word_counter', ceil(log2(dimensions + 1)))

    m.EmbeddedCode('')
    m.EmbeddedCode('//FSM possible states')
    FSM_RESETING = m.Localparam('FSM_RESETING', Int(0, fsm_main.width, 10))
    FSM_ACCUMULATING = m.Localparam('FSM_ACCUMULATING', Int(1, fsm_main.width, 10))
    FSM_REDUCING_0 = m.Localparam('FSM_REDUCING_0', Int(2, fsm_main.width, 10))
    FSM_REDUCING_1 = m.Localparam('FSM_REDUCING_1', Int(3, fsm_main.width, 10))
    FSM_REDUCING_2 = m.Localparam('FSM_REDUCING_2', Int(4, fsm_main.width, 10))
    FSM_DONE = m.Localparam('FSM_DONE', Int(5, fsm_main.width, 10))

    m.EmbeddedCode('')
    m.EmbeddedCode('//Memory read controller ')
    rd_addr.assign(Mux(auto_rd, centroide, rd_reg))

    m.EmbeddedCode('')
    m.EmbeddedCode('//Incrementation of memory values')
    for i in range(dimensions + 1):
        if(i <dimensions):
            mem_sum_data[i * 48:(i * 48) + 48].assign(mem_output_data[i * 48:(i * 48) + 48] + data_in[i * 48:(i * 48) + 48])
        else:
            mem_sum_data[i * 48:(i * 48) + 48].assign(mem_output_data[i * 48:(i * 48) + 48] + Int(1,48,10))

    # memories for the dimmensions accumulators
    m.EmbeddedCode('')
    m.EmbeddedCode('//Memory instanciation')
    con = [('clk', clk), ('wr_en', wr_en), ('rd_addr', rd_addr), ('wr_addr', wr_addr),
           ('input_data', mem_input_data), ('output_data', mem_output_data)]
    m.Instance(memory, 'mem', param, con)

    # FSMs
    m.EmbeddedCode('')
    m.EmbeddedCode('//Main State Machine')
    m.Always(Posedge(clk))(
        If(rst)(
            fsm_main(FSM_RESETING),
            auto_rd(Int(1, 0, 10)),
            rd_reg(Int(1, rd_reg.width, 10)),
            wr_en(Int(0, 1, 10)),
            rst_counter(Int(0, rst_counter.width, 10)),
            reduce_counter(Int(0, rst_counter.width, 10)),
            data_out_valid(Int(0,data_out_valid.width,10)),
            data_out(Int(0, data_out.width, 10)),
        ).Else(
            wr_en(Int(0, 1, 10)),
            data_out_valid(Int(0, data_out_valid.width, 10)),
            Case(fsm_main)(
                When(FSM_RESETING)(
                    If(rst_counter < Int(k, ceil(log2(k + 1)), 10))(
                        wr_addr(rst_counter),
                        wr_en(Int(1, 1, 10)),
                        mem_input_data(Int(0, mem_input_data.width, 10)),
                        rst_counter(rst_counter + Int(1, rst_counter.width, 10)),
                    ).Else(
                        fsm_main(FSM_ACCUMULATING)
                    )
                ),
                When(FSM_ACCUMULATING)(
                    Case(data_in_valid)(
                        When(Int(1, 2, 10))(  # Valid
                            wr_addr(centroide),
                            wr_en(Int(1, 1, 10)),
                            mem_input_data(mem_sum_data),
                        ),
                        When((Int(2, 2, 10)))(  # DONE
                            fsm_main(FSM_REDUCING_0),
                            auto_rd(Int(0,2,10)),
                        ),
                    ),
                ),
                When(FSM_REDUCING_0)(
                    If(reduce_counter < Int(k,reduce_counter.width,10))(
                        rd_reg(reduce_counter),
                        reduce_counter(reduce_counter + Int(1,reduce_counter.width,10)),
                        fsm_main(FSM_REDUCING_1),
                    ).Else(
                        data_out_valid(Int(2, data_out_valid.width, 10)),
                        fsm_main(FSM_DONE)
                    ),
                ),
                When(FSM_REDUCING_1)(
                    mem_output_frag_data(mem_output_data),
                    word_counter(Int(0, word_counter.width, 10)),
                    fsm_main(FSM_REDUCING_2),
                ),
                When(FSM_REDUCING_2)(
                    data_out_valid(Int(1, data_out_valid.width, 10)),
                    data_out(Cat(Int(0,64-48,10),mem_output_frag_data[0:48])),
                    mem_output_frag_data(mem_output_frag_data >> 48),
                    word_counter(word_counter + Int(1,word_counter.width,10)),
                    fsm_main(FSM_REDUCING_2),
                    If(word_counter == Int(dimensions,word_counter.width,10))(
                        fsm_main(FSM_REDUCING_0)
                    ),
                ),
                When(FSM_DONE)(
                    data_out_valid(Int(2, data_out_valid.width, 10)),
                    fsm_main(FSM_DONE)
                ),
            )
        )
    )

    return m


split_modules(make_accumulator(2, 2, 16, make_memory(2, 48 * (2 + 1))).to_verilog(), 'verilog')
