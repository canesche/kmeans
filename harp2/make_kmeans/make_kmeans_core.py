from math import log2, ceil

from veriloggen import *

from util import generate_kmeans_core


def make_kmeans_core(data_width, k, sumK, dimensions, components_array):
    m = Module('kmeans_core_%d' % k)

    controller_data_width = 8
    centroid_id_width = ceil(log2(sumK))
    imm_id_width = ceil(log2((sumK * dimensions) + 1))

    core = generate_kmeans_core(k, dimensions)

    clk = m.Input('clk')
    rst = m.Input('rst')

    kmeans_core_centroids_configurations_in = m.Input('kmeans_core_centroids_configurations_in', 64)
    kmeans_core_data_in = m.Input('kmeans_core_data_in', data_width * dimensions)
    kmeans_core_data_out = m.Output('kmeans_core_data_out', controller_data_width)

    num_add = 0
    for key, values in core.items():
        if 'ADD' in str(key):
            num_add = num_add + 1

    add_log_width = 0
    if num_add > 0:
        add_log_width = int(log2(num_add))

    bus_width_out = {'ADD': add_log_width + (2 * data_width) + centroid_id_width,
                     'CMP': add_log_width + (2 * data_width) + centroid_id_width,
                     'IN': data_width + centroid_id_width,
                     'IMM': data_width + centroid_id_width,
                     'QUAD': add_log_width + (2 * data_width) + centroid_id_width,
                     'REG': add_log_width + (2 * data_width) + centroid_id_width,
                     'SUB': data_width + centroid_id_width}

    # components list
    components = []
    for key, values in core.items():
        for value in values:
            if str(key) not in components:
                components.append(str(key))
            if str(value) not in components:
                components.append(str(value))
    components.sort()

    m.EmbeddedCode(' ')
    m.EmbeddedCode('//Kmeans wires')

    wires = {}
    for component in components:
        pre = component.split('_')
        wires[component + '_out'] = m.Wire(component + '_out', bus_width_out[pre[0]])

    m.EmbeddedCode(' ')
    m.EmbeddedCode('//Input assigns to Kmeans input wires')

    for key in wires:
        if 'IN' in key:
            str_key = str(key)
            pre = str_key.split('_')
            input_number = int(pre[1])
            wire = wires[key]
            wire.assign(kmeans_core_data_in[input_number * data_width:(input_number * data_width) + data_width])

    m.EmbeddedCode(' ')
    m.EmbeddedCode('//Output assign')
    for component in components:
        if 'CMP' in component:
            last = False
            for dict_key, values in core.items():
                if component == str(dict_key) and len(values) == 0:
                    kmeans_core_data_out.assign(Cat(Int(0, kmeans_core_data_out.width - centroid_id_width, 10),
                                                    wires[component + '_out'][
                                                    bus_width_out['CMP'] - centroid_id_width:bus_width_out['CMP']]))

    # geração dos módulos
    # add = make_component_add(bus_width_out['ADD'], centroid_id_width)
    # cmp = make_component_cmp(bus_width_out['CMP'], centroid_id_width)
    # imm = make_component_imm(bus_width_out['IMM'], imm_id_width, centroid_id_width)
    # quad = make_component_quad(data_width, bus_width_out['QUAD'], centroid_id_width)
    # sub = make_component_sub(bus_width_out['SUB'], centroid_id_width)
    # reg = make_component_reg(bus_width_out['REG'], centroid_id_width)

    add = components_array['ADD']
    cmp = components_array['CMP']
    imm = components_array['IMM']
    quad = components_array['QUAD']
    sub = components_array['SUB']
    reg = components_array['REG']

    # instancialização dos módulos
    for component in components:
        pre = component.split('_')
        number = int(pre[1])
        if 'ADD' in component:
            m.EmbeddedCode(' ')
            m.EmbeddedCode('//ADD_%d Instantiation' % number)

            component_bus = []
            idx = 0
            for dict_key, values in core.items():
                for value in values:
                    if 'ADD_' + str(number) == str(value):
                        component_bus.append(wires[str(dict_key) + '_out'])
                        idx = idx + 1
            params = [('DATA_WIDTH', bus_width_out['ADD']), ('CENTROID_ID_WIDTH', centroid_id_width)]
            con = [('clk', clk),
                   ('data_in_0', component_bus[0]),
                   ('data_in_1', component_bus[1]),
                   ('data_out', wires[component + '_out'])]
            m.Instance(add, 'm_add%d' % number, params, con)
        elif 'CMP' in component:
            m.EmbeddedCode(' ')
            m.EmbeddedCode('//CMP_%d Instantiation' % number)

            component_bus = []
            idx = 0
            for dict_key, values in core.items():
                for value in values:
                    if 'CMP_' + str(number) == str(value):
                        component_bus.append(wires[str(dict_key) + '_out'])
                        idx = idx + 1

            there_is_reg = False
            for bus in component_bus:
                if "REG" in str(bus):
                    there_is_reg = True
                    break

            if there_is_reg:
                if ("REG" in str(component_bus[1])):
                    component_bus[0], component_bus[1] = component_bus[1], component_bus[0]
            else:
                componet_id_0 = str(component_bus[0]).split('_')[1]
                componet_id_1 = str(component_bus[1]).split('_')[1]
                if (int(componet_id_0) < int(componet_id_1)):
                    component_bus[0], component_bus[1] = component_bus[1], component_bus[0]

            params = [('DATA_WIDTH', bus_width_out['CMP']), ('CENTROID_ID_WIDTH', centroid_id_width)]
            con = [('clk', clk),
                   ('data_in_0', component_bus[0]),
                   ('data_in_1', component_bus[1]),
                   ('data_out', wires[component + '_out'])]
            m.Instance(cmp, 'm_cmp%d' % number, params, con)
        elif 'IMM' in component:
            m.EmbeddedCode(' ')
            m.EmbeddedCode('//IMM_%d Instantiation' % number)

            # if number == 0:
            # cent_id = Int(0, centroid_id_width, 10)
            # else:
            # cent_id = Int(int(log2(number)), centroid_id_width, 10)
            cent_id = Int(int(number / dimensions), centroid_id_width, 10)

            cent_im_id = Int(number + 1, imm_id_width, 10)

            params = [('DATA_WIDTH', bus_width_out['IMM']),
                      ('CENTROID_ID_WIDTH', centroid_id_width),
                      ('CENTROID_ID', cent_id),
                      ('IMM_ID_WIDTH', imm_id_width),
                      ('IMM_ID', cent_im_id)]
            con = [('clk', clk),
                   ('centroid_configuration_in', kmeans_core_centroids_configurations_in),
                   ('data_out', wires[component + '_out'])]
            m.Instance(imm, 'm_imm%d' % number, params, con)
        elif 'QUAD' in component:
            m.EmbeddedCode(' ')
            m.EmbeddedCode('//QUAD_%d Instantiation' % number)

            component_bus = []
            idx = 0
            for dict_key, values in core.items():
                for value in values:
                    if 'QUAD_' + str(number) == str(value):
                        component_bus.append(wires[str(dict_key) + '_out'])
                        idx = idx + 1

            params = [('DATA_WIDTH_IN', data_width),
                      ('DATA_WIDTH_OUT', bus_width_out['QUAD']),
                      ('CENTROID_ID_WIDTH', centroid_id_width)]

            con = [('clk', clk),
                   ('data_in_0', component_bus[0]),
                   ('data_out', wires[component + '_out'])]
            m.Instance(quad, 'm_quad%d' % number, params, con)
        elif 'SUB' in component:
            m.EmbeddedCode(' ')
            m.EmbeddedCode('//SUB_%d Instantiation' % number)

            component_bus = []
            idx = 0
            for dict_key, values in core.items():
                for value in values:
                    if 'SUB_' + str(number) == str(value):
                        component_bus.append(wires[str(dict_key) + '_out'])
                        idx = idx + 1

            params = [('DATA_WIDTH', bus_width_out['SUB']), ('CENTROID_ID_WIDTH', centroid_id_width)]
            con = [('clk', clk),
                   ('data_in_0', component_bus[0]),
                   ('data_in_1', component_bus[1]),
                   ('data_out', wires[component + '_out'])]
            m.Instance(sub, 'm_sub%d' % number, params, con)
        elif 'REG' in component:
            m.EmbeddedCode(' ')
            m.EmbeddedCode('//REG_%d Instantiation' % number)

            component_bus = []
            idx = 0
            for dict_key, values in core.items():
                for value in values:
                    if 'REG_' + str(number) == str(value):
                        component_bus.append(wires[str(dict_key) + '_out'])
                        idx = idx + 1
            params = [('DATA_WIDTH', bus_width_out['REG'])]
            con = [('clk', clk),
                   ('data_in_0', component_bus[0]),
                   ('data_out', wires[component + '_out'])]
            m.Instance(reg, 'm_reg%d' % number, params, con)

    return m
