import numpy as np
import random
import collections

Block = collections.namedtuple('Block', 'c w h')
PlacedBlock = collections.namedtuple('PlacedBlock', 'c w h x y')

L = 8
BLOCK_W = [1,2,3]
BLOCK_H = [2,3,4,5]
BLOCK_C = ['R', 'G', 'B']

def gen_block_dim():
    w = random.choice(BLOCK_W)
    h = random.choice(BLOCK_H)
    if w + h > 6:
        return gen_block_dim()
    if np.random.random() < 0.5:
        return (w,h)
    else:
        return (h,w)

def gen_block():
    return Block(*(random.choice(BLOCK_C),) + gen_block_dim())

# take a group of blocks, and randomly drop them in a tetris fashoin
def random_drop_blocks(blocks):
    # get the countour for y axis
    def get_y_countour(placed_blocks):
        ret = dict([(i,0) for i in range(L)])
        for pb in placed_blocks:
            for x in range(pb.x, pb.x+pb.w):
                ret[x] = max(ret[x], pb.y+pb.h)
        return ret

    def drop(b, dropped):
        bx = random.choice(range(L - b.w))
        bx_min, bx_max = bx, bx + b.w

        countour = get_y_countour(dropped)
        hh = max(countour[x] for x in range(bx_min, bx_max))
        return PlacedBlock(b.c, b.w, b.h, bx, hh)

    bs = [b for b in blocks]
    random.shuffle(bs)
    ret = []
    for b in bs:
        placed_block = drop(b, ret)
        if placed_block.y + placed_block.h >= L:
            return random_drop_blocks(blocks)
        ret.append(placed_block)
    return ret

# take a group of blocks, sample a random 'program' of dropped blocks
# from a subset of the blockss
def random_program(blocks):
    bs = [b for b in blocks]
    subset = np.array([1.5 ** i for i in range(len(bs))])
    subset_prob = subset / sum(subset)
    num_blocks = np.random.choice([i+1 for i in range(len(bs))], p=subset_prob)
    random.shuffle(bs)
    bs = bs[:num_blocks]
    return random_drop_blocks(bs)

def sample_good_program(blocks, spec, budget):
    best = 0
    ret = None
    for _ in range(budget):
        prog = random_program(blocks)
        score = spec(prog)
        if score >= best:
            best = score
            ret = prog
    return ret

def render_placed_blocks(placed_blocks, name='placed_blocks'):
    from matplotlib import pyplot as plt
    from matplotlib.patches import Rectangle
    plt.figure()
    currentAxis = plt.gca()

    for pb in placed_blocks:
        currentAxis.add_patch(Rectangle((pb.x/L, pb.y/L), pb.w/L, pb.h/L,facecolor=pb.c,edgecolor='black'))
    
    plt.savefig(f'drawings/{name}.png')

# ======================== SPEC ======================
# 2 kinds of predicates, atomic and compositional
class Pred:
    def __str__(self):
        return self.__repr__()
    @staticmethod
    def sample():
        return Comp.sample(3)

# ----------------------- atomic predicates ---------------------
class Atomic(Pred):
    @staticmethod
    def sample():
        atoms = [
        lambda : Red(),
        lambda : Green(),
        lambda : Blue(),
        lambda : Wide(),
        lambda : Tall(),
        lambda : Base(),
        lambda : Solid(),
        ]

        return random.choice(atoms)()

class Color(Atomic):
    def __init__(self):
        super(Color, self).__init__()
    def get_color(self, placed_blocks):
        r, g, b = 0, 0, 0
        for pb in placed_blocks:
            mass = pb.w  * pb.h
            if pb.c == 'R':
                r += mass
            if pb.c == 'G':
                g += mass
            if pb.c == 'B':
                b += mass
        return np.array([r,g,b]) / sum([r,g,b])

class Red(Color):
    def __init__(self):
        super(Red, self).__init__()
    def __repr__(self):
        return 'Red'
    def __call__(self, placed_blocks):
        return self.get_color(placed_blocks)[0]

class Green(Color):
    def __init__(self):
        super(Green, self).__init__()
    def __repr__(self):
        return 'Green'
    def __call__(self, placed_blocks):
        return self.get_color(placed_blocks)[1]

class Blue(Color):
    def __init__(self):
        super(Blue, self).__init__()
    def __repr__(self):
        return 'Blue'
    def __call__(self, placed_blocks):
        return self.get_color(placed_blocks)[2]

class Wide(Atomic):
    def __init__(self):
        super(Wide, self).__init__()
    def __repr__(self):
        return 'Wide'
    def __call__(self, placed_blocks):
        left = L
        right = 0
        for pb in placed_blocks:
            left = min(left, pb.x)
            right = max(right, pb.x+pb.w)
        return (right - left) / L

class Tall(Atomic):
    def __init__(self):
        super(Tall, self).__init__()
    def __repr__(self):
        return 'Tall'
    def __call__(self, placed_blocks):
        bot = L
        top = 0
        for pb in placed_blocks:
            bot = min(bot, pb.y)
            top = max(top, pb.y+pb.h)
        return (top - bot) / L

class Base(Atomic):
    def __init__(self):
        super(Base, self).__init__()
    def __repr__(self):
        return 'Base'
    def __call__(self, placed_blocks):
        base_w = sum([pb.w for pb in placed_blocks if pb.y == 0])
        return base_w / L

class Solid(Atomic):
    def __init__(self):
        super(Solid, self).__init__()
    def __repr__(self):
        return 'Solid'
    def __call__(self, placed_blocks):
        ww = Wide()(placed_blocks) * L
        hh = Tall()(placed_blocks) * L
        vol = ww * hh 
        mass = sum([pb.w * pb.h for pb in placed_blocks])
        return mass / vol

# --------------------- composite predicates ----------------------
class Comp(Pred):
    @staticmethod
    def sample(n):
        if n == 1:
            return Atomic.sample()
        else:
            gen_Atom = lambda : Atomic.sample()
            gen_Not = lambda : Not(Comp.sample(n-1))
            gen_And = lambda : And(Comp.sample(n-1),Comp.sample(n-1))
            gen_Or = lambda : Or(Comp.sample(n-1),Comp.sample(n-1))
            return random.choice([gen_Atom, gen_Not, gen_And, gen_Or])()

class Not(Comp):
    def __init__(self, pred):
        super(Not, self).__init__()
        self.pred = pred
    def __repr__(self):
        return f"Not({self.pred})"
    def __call__(self, placed_blocks):
        return 1.0 - self.pred(placed_blocks)

class And(Comp):
    def __init__(self, pred1, pred2):
        super(And, self).__init__()
        self.pred1, self.pred2 = pred1, pred2
    def __repr__(self):
        return f"And({self.pred1}, {self.pred2})"
    def __call__(self, placed_blocks):
        return min(self.pred1(placed_blocks), self.pred2(placed_blocks))

class Or(Comp):
    def __init__(self, pred1, pred2):
        super(Or, self).__init__()
        self.pred1, self.pred2 = pred1, pred2
    def __repr__(self):
        return f"Or({self.pred1}, {self.pred2})"
    def __call__(self, placed_blocks):
        return max(self.pred1(placed_blocks), self.pred2(placed_blocks))

if __name__ == '__main__':
    print (gen_block())

    blocks = [gen_block() for _ in range(4)]
    pred = Pred.sample()
    print (pred)
    render_placed_blocks(random_drop_blocks(blocks), "pieces")

    # print (pred(random_program(blocks)))
    # stacked_blocks = sample_good_program(blocks, pred, 100)
    # render_placed_blocks(stacked_blocks)
    # print (pred(stacked_blocks))

