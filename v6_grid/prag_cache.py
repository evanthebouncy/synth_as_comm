from grid import L, gen_legal_prog_shape, render_shapes, serialize, shape_to_repr
import pickle

def get_version_space():
    # version space
    vs = dict()
    seen_progs = set()
    seen_shapes = set()
    len_progs = []
    for i in range(100000000):
        prog, shapes = gen_legal_prog_shape()
        prog_tup = serialize(prog)
        shape_repr = shape_to_repr(shapes)
        if (prog_tup not in seen_progs) and (shape_repr not in seen_shapes):
            seen_progs.add(prog_tup)
            seen_shapes.add(shape_repr)
            for i in range(L):
                for j in range(L):
                    key = ((i,j), 'EMPTY' if (i,j) not in shapes else shapes[(i,j)])
                    if key not in vs:
                        vs[key] = set()
                    vs[key].add(prog_tup)
        if i % 1000 == 0:
            print (len(seen_progs), sum([len(v) for v in vs.values()]))
            pickle.dump(vs, open('L0VS.p', 'wb'))
            print ('dumped pickle')
            len_progs.append(len(seen_progs))
            if len(len_progs) > 10 and len_progs[-1] == len_progs[-9]:
                print ('were done here')
                return

if __name__ == '__main__':
    # get_version_space()
