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

REL = ['any', 'Adj', 'Near', 'Far']

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
    # if program too short redraw
    if len(set(placed_dots)) < len(placed_dots) or len(placed_dots) <= 1:
        return gen_prog()
    # knock out annoying symmetries in placements
    if r1 is not None and r2 is not None and r1 > r2:
        return gen_prog()
    if b1 is not None and b2 is not None and b1 > b2:
        return gen_prog()
    ret = [('B', b1), ('B', b2), ('R', r1), ('R', r2)]
    ret = [r for r in ret if r[1] is not None]
    return ret

def render_dots(dots, name='dots'):
    R = 0.1
    plt.figure()
    currentAxis = plt.gca(aspect='equal')

    for dot_c, dot_loc in dots:
        if dot_loc is not None:
            x, y = dot_loc
            currentAxis.add_patch(Circle((x/4+R, y/4+R), R, facecolor=dot_c))
    plt.savefig(f'drawings/{name}.png')
    plt.close()

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
            return (quantity, 'any')

    def unify_rel(rel):
        if len(set(rel)) == 1:
            return rel[0]
        else:
            return 'any'

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

# the literal speaker S0
# up to 2 descriptions of absolute locations
# up to 2 descriptions of relative locations
def S0(prog):
    loc_spec = list(sorted([gen_description_loc(prog) for _ in range(2)]))
    rel_spec = list(sorted([gen_description_rel(prog) for _ in range(2)]))
    return loc_spec, rel_spec
        
if __name__ == '__main__':
    prog = gen_prog()
    render_dots(prog, "orig_prog")
    loc_spec, rel_spec = S0(prog)
    for spec_line in loc_spec:
        print (spec_line)
    for spec_line in rel_spec:
        print (spec_line)

    # print ("orig prog ", prog)
    # rec_prog = L0((loc_spec, rel_spec))
    # print ("recovered prog ", rec_prog)
    # render_dots(rec_prog, "recovered_prog")

