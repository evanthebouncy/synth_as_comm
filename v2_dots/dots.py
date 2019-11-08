import random
from matplotlib import pyplot as plt
from matplotlib.patches import Circle
import numpy as np

# ============================ CONSTS ===============================

QQ = ['all', 'some', '1', '2', '3', '4']
CC = ['any', 'B', 'R']
DD1 = ['any', 'Center', 'Corner', 'Edge']
DD2 = ['any', 'Bot', 'Top']
DD3 = ['any', 'Left', 'Right']

# ============================ PROGRAMS ==============================
def flip():
    return random.random() < 0.5

def random_loc():
    return random.randint(0, 3), random.randint(0, 3)

# generate a random program
def gen_prog():
    # a program consists of up to 4 dots, 2 red 2 blue
    b1 = None if flip() else random_loc()
    b2 = None if flip() else random_loc()
    r1 = None if flip() else random_loc()
    r2 = None if flip() else random_loc()

    placed_dots = [dot for dot in [b1, b2, r1, r2] if dot is not None]
    if len(set(placed_dots)) < len(placed_dots) or len(placed_dots) <= 1:
        return gen_prog()
    return [('B', b1), ('B', b2), ('R', r1), ('R', r2)]

def render_dots(dots, name='dots'):
    R = 0.1
    plt.figure()
    currentAxis = plt.gca(aspect='equal')

    for dot_c, dot_loc in dots:
        if dot_loc is not None:
            x, y = dot_loc
            currentAxis.add_patch(Circle((x/4+R, y/4+R), R, facecolor=dot_c))
    plt.savefig(f'drawings/{name}.png')

def prog_to_np1(prog):
    prog = [p for p in prog if p[1] is not None]
    blue_layer = np.zeros((4,4))
    red_layer = np.zeros((4,4))
    for dot_c, dot_loc in prog:
        if dot_c == 'B':
            blue_layer[dot_loc[0]][dot_loc[1]] = 1.0
        else:
            red_layer[dot_loc[0]][dot_loc[1]] = 1.0
    return blue_layer, red_layer
        
# ============================== SPECS =================================
def color(dot):
    return dot[0]

def loc(dot):
    def description1(dot):
        x, y = dot[1]
        if (x,y) in [(1,1),(1,2),(2,1),(2,2)]:
            return 'Center'
        if (x,y) in [(0,0),(0,3),(3,0),(3,3)]:
            return 'Corner'
        else:
            return 'Edge'
    def description2(dot):
        x, y = dot[1]
        if y in [0,1]:
            return 'Bot'
        else:
            return 'Top'
    def description3(dot):
        x, y = dot[1]
        if x in [0,1]:
            return 'Left'
        else:
            return 'Right'
    return description1(dot), description2(dot), description3(dot)

def describe_most_precise(dot):
    return (color(dot),) + loc(dot)

# attempt to unify some descriptions on a list of dots
def unify_descriptions(descs):
    features = [set() for _ in range(4)]
    for desc in descs:
        for i in range(len(features)):
            features[i].add(desc[i])
    unified = [list(feat)[0] if len(feat) == 1 else 'any' for feat in features]
    return tuple(unified)

# generate a description of a location kind
def gen_description_loc(dots):
    # filter out the legal dots
    dots_to_describe = [dot for dot in dots if dot[1] is not None]
    precise_descriptions = [describe_most_precise(dot) for dot in dots_to_describe]
    n_num = random.choice(list(range(1, len(dots_to_describe)+1)))
    sub_descriptions = random.sample(precise_descriptions, n_num)
    quantity = random.choice([str(n_num), 'some' if n_num < len(dots_to_describe) else 'all'])
    return (quantity,) + unify_descriptions(sub_descriptions)

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

# super hack
# get EVERY legal description of loc kind by just hardcore sampling a lot
# see if it sat . . . 
def sat_description_loc(loc_spec, dots):
    str_loc_spec = str(loc_spec)
    for i in range(200):
        if str(gen_description_loc(dots)) == str_loc_spec:
            return True
    return False

def get_rel(dot1, dot2):
    x1,y1 = dot1[1]
    x2,y2 = dot2[1]
    if abs(x1-x2)+abs(y1-y2) == 1:
        return 'Adj'
    if abs(x1-x2)+abs(y1-y2) == 2:
        return 'Near'
    else:
        return 'Far'

def unify_descriptions_rel(set1, set2, rel):
    def unify_set(aset):
        quantity = 'some' if flip() else str(len(aset))
        colors = list(set([x[0] for x in aset]))
        if len(colors) == 1:
            return (quantity, colors[0])
        else:
            return (quantity, 'RB')

    def unify_rel(rel):
        if len(set(rel)) == 1:
            return rel[0]
        else:
            return 'any_rel'

    return (unify_rel(rel), unify_set(set1), unify_set(set2))

# generate a description of the relation kind
def gen_description_rel(dots):
    # filter out the legal dots
    dots_to_describe = [dot for dot in dots if dot[1] is not None]
    def get_2_subsets():
        set1, set2 = [], []
        for d in dots_to_describe:
            goto = random.choice([1, 2, None])
            if goto == 1:
                set1.append(d)
            if goto == 2:
                set2.append(d)
            if goto == None:
                pass
        if len(set1) == 0 or len(set2) == 0:
            return get_2_subsets()
        return set1, set2
    set1, set2 = get_2_subsets()
    rels = []
    for d1 in set1:
        for d2 in set2:
            rels.append(get_rel(d1, d2))
    return unify_descriptions_rel(set1, set2, rels)

# super hack
# get EVERY legal description of rel kind by just hardcore sampling a lot
# see if it sat . . . 
def sat_description_rel(rel_spec, dots):
    str_rel_spec = str(rel_spec)
    for i in range(200):
        if str(gen_description_rel(dots)) == str_rel_spec:
            return True
    return False

# the literal speaker S0
# up to 2 descriptions of absolute locations
# up to 2 descriptions of relative locations
def S0(prog):
    loc_spec = list(sorted([gen_description_loc(prog) for _ in range(2)]))
    rel_spec = list(sorted([gen_description_rel(prog) for _ in range(2)]))
    return loc_spec, rel_spec

# the literal listener L0
# generate any program that satisfies the spec
def L0(spec):
    def sat(prog):
        loc_specs, rel_specs = spec
        for loc_spec in loc_specs:
            if not sat_description_loc(loc_spec, prog):
                return False
        for rel_spec in rel_specs:
            if not sat_description_rel(rel_spec, prog):
                return False
        return True

    for i in range(10000000):
        prog = gen_prog()
        if sat(prog):
            return prog

    assert 0, 'failed'
        
if __name__ == '__main__':
    prog = gen_prog()
    print (prog_to_np1(prog))
    render_dots(prog, "orig_prog")
    loc_spec, rel_spec = S0(prog)
    for spec_line in loc_spec:
        print (spec_line)
        print (description_loc_to_np(spec_line))
    for spec_line in rel_spec:
        print (spec_line)

    print ("orig prog ", prog)
    rec_prog = L0((loc_spec, rel_spec))
    print ("recovered prog ", rec_prog)
    render_dots(rec_prog, "recovered_prog")

    all_us = PS0(prog)
    print (len(all_us))
    print (all_us[0])

    all_ws = PL0((loc_spec, rel_spec))
    print (len(all_ws))
