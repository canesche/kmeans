import re
from enum import Enum
from itertools import chain

import math


class Node:
    class Type(Enum):
        REG = 0
        ADD = 1
        IMM = 2
        IN = 3
        SUB = 4
        QUAD = 5
        CMP = 6
        EQ = 7
        CONST = 8
        ACC = 9

    @classmethod
    def get_node(cls, node_type, graph):
        index = node_type.value
        node_id = cls.next_id[index]
        cls.next_id[index] += 1
        node = Node(node_id, node_type)
        graph[node] = []
        return node

    @classmethod
    def reduce(cls, nodes, operation, graph):
        while len(nodes) > 1:
            queue = nodes
            nodes = []
            it = 0

            while it < len(queue):

                if it + 2 <= len(queue):
                    operator = cls.get_node(operation, graph)
                    graph[queue[it]].append(operator)
                    graph[queue[it + 1]].append(operator)
                    nodes.append(operator)
                    it += 2

                else:
                    reg = cls.get_node(cls.Type.REG, graph)
                    graph[queue[it]].append(reg)
                    nodes.append(reg)
                    it += 1

        return nodes[0]

    @classmethod
    def balance(cls, node, out, graph):
        nodes = [node]

        while (True):

            if len(nodes) * 2 < len(out):
                queue = nodes
                nodes = []

                for el in queue:
                    regl = cls.get_node(cls.Type.REG, graph)
                    regr = cls.get_node(cls.Type.REG, graph)
                    graph[el].append(regl)
                    graph[el].append(regr)
                    nodes.append(regl)
                    nodes.append(regr)

            else:
                queue = nodes
                it_queue = 0
                it_out = 0

                while it_out < len(out):

                    if len(out) - it_out > len(queue) - it_queue:
                        graph[queue[it_queue]].append(out[it_out])
                        graph[queue[it_queue]].append(out[it_out + 1])
                        it_out += 2

                    else:
                        graph[queue[it_queue]].append(out[it_out])
                        it_out += 1

                    it_queue += 1

                break

        return out

    @classmethod
    def delay(cls, node, n, graph):
        while n > 0:
            reg = Node.get_node(Node.Type.REG, graph)
            graph[node].append(reg)
            node = reg
            n -= 1
        return node

    @classmethod
    def print_dot(cls, graph):
        print("digraph {")

        for k, v in graph.items():

            for i in v:
                print("    {} -> {}".format(k, i))

        print("}")

    next_id = [0 for x in Type]

    def __init__(self, node_id, node_type):
        self.id = node_id
        self.type = node_type

    def __str__(self):
        return "{}_{}".format(self.type.name, self.id)


def generate_kmeans_core(k, dimensions):
    graph = {}

    inputs = [Node.get_node(Node.Type.IN, graph) for x in range(dimensions)]

    regs = [Node.get_node(Node.Type.REG, graph) for x in range(dimensions)]

    #accs = [[Node.get_node(Node.Type.ACC, graph) for x in range(dimensions)]
    #        for y in range(k)]

    imms = [[Node.get_node(Node.Type.IMM, graph) for x in range(dimensions)]
            for y in range(k)]

    subs = [[Node.get_node(Node.Type.SUB, graph) for x in range(k)]
            for y in range(dimensions)]

    balanced_inputs = list(chain(*[Node.balance(x, [regs[it], *subs[it]], graph)
                                   for it, x in enumerate(inputs)]))
    #balanced_inputs = list(chain(*[Node.balance(x, subs[it], graph) for it, x in enumerate(inputs)]))

    for i, reg in enumerate(regs):
        regs[i] = Node.delay(reg, 1 + math.ceil(math.log2(dimensions)) +
                              1 +
                             (0 if k < 3 else math.ceil(math.log2(k)) - 1),
                             graph)

    '''for i, reg in enumerate(regs):
        regs[i] = Node.delay(reg, 1 + math.ceil(math.log2(dimensions)) +
                             math.ceil(math.log2(k)) + 1 +
                             (0 if k < 3 else math.ceil(math.log2(k)) - 1),
                             graph)
    '''

    subs_ordered = []

    for K, imms_k in enumerate(imms):
        subs_ordered.append([])

        for dim, imm in enumerate(imms_k):
            graph[imm].append(subs[dim][K])
            subs_ordered[K].append(subs[dim][K])

        # print(*subs_ordered[K])

    inertias = []
    for subs_k in subs_ordered:
        to_reduce = []

        for sub in subs_k:
            quad = Node.get_node(Node.Type.QUAD, graph)
            graph[sub].append(quad)
            to_reduce.append(quad)

        inertias.append(Node.reduce(to_reduce, Node.Type.ADD, graph))

    cmp_node = Node.reduce(inertias, Node.Type.CMP, graph)

    # consts = [Node.get_node(Node.Type.CONST, graph) for x in range(k)]
    # eqs = [Node.get_node(Node.Type.EQ, graph) for x in range(k)]

    # Node.balance(cmp_node, eqs, graph)

    # for it, const in enumerate(consts):
    #    graph[const].append(eqs[it])

    # for i, eq in enumerate(eqs):
    #    Node.balance(eq, accs[i], graph)

    # accs_by_dim = [[0 for x in range(k)] for x in range(dimensions)]

    # for x in range(k):
    #    for y in range(dimensions):
    #        accs_by_dim[y][x] = accs[x][y]

    # for x, reg in enumerate(regs):
    #    Node.balance(reg, accs_by_dim[x], graph)

    Node.print_dot(graph)

    return graph


# generate_kmeans_core(3, 3)

def validate_configurations(external_data_width, data_width, dimensions):
    cache_line_fit = external_data_width % (dimensions * data_width) == 0

    if not cache_line_fit:
        return False

    return True


def split_modules(str_modules,dir):
    modules = str_modules.split('endmodule')
    for m in modules:
        m = m.strip(' \n')
        if m.strip('\n') != '':
            name = m.split(' ')[1]
            #name = name.replace('\n','')
            #name = name.replace('(', '')
            #name = name.replace(')', '')
            name = re.sub("[\n()]","",name)
            with open(dir+'/%s.v'%(name),'w') as fm:
                m = m + '\n\nendmodule'
                fm.write(m)