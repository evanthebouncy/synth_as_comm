import torch
import numpy as np
from dots import *
from prag1 import *

# turn a program into a numpy 
def prog_to_np(prog):
    prog = [p for p in prog if p[1] is not None]
    blue_layer = np.zeros((4,4))
    red_layer = np.zeros((4,4))
    for dot_c, dot_loc in prog:
        if dot_c == 'B':
            blue_layer[dot_loc[0]][dot_loc[1]] = 1.0
        else:
            red_layer[dot_loc[0]][dot_loc[1]] = 1.0
    return blue_layer, red_layer
        

# description to a numpy array
def description_loc_to_np(desc):
    q, c, d1, d2, d3 = desc
    ret = np.zeros((5,6))
    ret[0][QQ.index(q)] = 1.0
    ret[1][CC.index(c)] = 1.0
    ret[2][DD1.index(d1)] = 1.0
    ret[3][DD2.index(d2)] = 1.0
    ret[4][DD3.index(d3)] = 1.0
    return ret

# description to a numpy array
def description_rel_to_np(desc):
    rel, (q1, c1), (q2, c2) = desc
    ret = np.zeros((5,6))
    ret[0][REL.index(rel)] = 1.0
    ret[1][REL_Q.index(q1)] = 1.0
    ret[2][REL_C.index(c1)] = 1.0
    ret[3][REL_Q.index(q2)] = 1.0
    ret[4][REL_C.index(c2)] = 1.0
    return ret

def prog_spec_to_np(prog, spec):
    loc_spec, rel_spec = spec
    locnp = [description_loc_to_np(ls) for ls in loc_spec]
    relnp = [description_rel_to_np(ls) for ls in rel_spec]
    together = np.array(locnp + relnp)
    return prog_to_np(prog), together

# make a S1 sampler based off of PS1
def get_S1(PS0, PL0):

    def S1(prog):
        specs, weights = PS1(prog, PS0, PL0)
        idx = np.random.choice(list(range(len(specs))), p = weights)
        return specs[idx]

    return S1


def get_S1_data(S1):
    prog = gen_prog()
    spec = S1(prog)
    return prog, spec



if __name__ == '__main__':
    PS0, PL0 = load_S0_L0_from_cache()

    S1 = get_S1(PS0, PL0)
    prog, spec = get_S1_data(S1)
    print (prog, spec)
