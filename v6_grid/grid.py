import numpy as np
import random
from matplotlib import pyplot as plt
from matplotlib.patches import Circle
from matplotlib.patches import Rectangle

# ========================== CONSTANTS ============================
L = 7
SHAPES = ['CUBE', 'SPHERE', 'EMPTY']
COLORS = ['R', 'G', 'B']

# alternating pattern selections
def choose_patt(pattern_pick, index_pick):
    patterns = [lambda x : 0,
                lambda x : 1,
                lambda x : 0 if x % 2 else 1,
                lambda x : 1 if x % 2 else 2,
                lambda x : 2 if x % 2 else 0,
                lambda x : 2,
                ]
    indexs = ['i', 'j', 'i+j', 'i+j+1']
    patt = patterns[pattern_pick]
    index = indexs[index_pick]
    def pattern(i,j):
        return patt(eval(index))
    return pattern

# renders the program into a dictionary of (i,j) => (shape, color)
def render_shapes(prog):
    i_start, i_end = prog['irange']
    j_start, j_end = prog['jrange']
    patt_shape = choose_patt(*prog['patt_shape'])
    patt_color = choose_patt(*prog['patt_color'])

    ret = dict()
    for i in range(i_start, i_end+1):
        for j in range(j_start, j_end+1):
            shape, color = SHAPES[patt_shape(i,j)], COLORS[patt_color(i,j)]
            if shape != 'EMPTY':
                ret[(i,j)] = (shape, color)
    return ret

# draws the shapes onto a canvas
def draw(shapes, name):
    R = 0.9 / 2 / L
    plt.figure()
    currentAxis = plt.gca(aspect='equal')

    for coord in shapes:
        shape, color = shapes[coord]
        x,y = coord
        if shape == 'CUBE':
            currentAxis.add_patch(Rectangle((x/L, y/L), 2*R,2*R, facecolor=color))
        if shape == 'SPHERE':
            currentAxis.add_patch(Circle((x/L+R, y/L+R), R, facecolor=color))
    plt.savefig(f'drawings/{name}.png')
    plt.close()


# sample a random program by randomly sampling its parameters
def gen_rand_prog():
    def gen_range():
        start = random.choice([_ for _ in range(L)])
        end = random.choice([_ for _ in range(L)])
        if start + 2 <= end:
            return (start, end)
        else:
            return gen_range()

    prog = { 'irange' : gen_range(),
             'jrange' : gen_range(),
             'patt_shape' : (random.randint(0,4), random.randint(0,3)),
             'patt_color' : (random.randint(0,5), random.randint(0,3)),
             }
    return prog

# generate a legal program, where legality is defined loosely
def gen_legal_prog_shape():
    prog = gen_rand_prog()
    shapes = render_shapes(prog)
    if len(shapes) >= 1:
        return prog, shapes
    else:
        return gen_legal_prog_shape()

# turn program into a tuple to be stored
def serialize(prog):
    ret = prog['irange'] + prog['jrange'] + prog['patt_shape'] + prog['patt_color']
    return ret
def unserialize(tup):
    prog = { 'irange' : tup[0:2],
             'jrange' : tup[2:4],
             'patt_shape' : tup[4:6],
             'patt_color' : tup[6:8],
             }
    return prog

# turn shape into a cononical repr so to keep duplicate programs out
def shape_to_repr(shapes):
    return tuple(sorted(list(shapes.items())))
def unrepr_shape(shape_repr):
    return dict(shape_repr)

if __name__ == '__main__':
    # prog = gen_rand_prog()
    # shapes = render_shapes(prog)
    prog, shapes = gen_legal_prog_shape()
    print (prog)
    print (unserialize(serialize(prog)))
    print (shapes)
    print (shape_to_repr(shapes))
    draw(shapes, 'prog')
