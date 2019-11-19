import numpy as np
import random
from collections import namedtuple
from matplotlib import pyplot as plt
from matplotlib.patches import Circle

# ====================== CONSTS ===========================

# ------------------ consts for world ---------------------
W_COLOR = ['B', 'R']
W_L = 6
W_LOC = [(i,j) for i in range(W_L) for j in range(W_L)]
W_N_COLOR_DISTR = [2,3,3,4,4,4]

# ----------------- consts for utterance ------------------
U_QUANT = ['ALL', 'SOME', 1, 2, 3, 4]
U_COLOR = W_COLOR + ['DIFF', 'UNK']
U_LOC = W_LOC + ['CENTER', 'CORNER', 'EDGE', 'BOT', 'TOP', 'LEFT', 'RIGHT', 'DIFF', 'UNK']
U_REL = ['LEFT', 'ABOVE', 'TOUCH', 'CLOSE', 'FAR', 'HALGN', 'VALGN', 'DIFF', 'UNK']
def u_cost(uu):
    # 0 bit
    if uu in ['UNK', 'Yes', 'No', 'Ui', 'Uloc', 'Urel']:
        return 0
    # roughly 5 bits of information
    if uu in W_LOC:
        return 5
    # 2 bit of information
    if uu in ['1','2','3','4']:
        return 2
    else:
        return 1

def get_loc_attr(loc):
    lr = 'LEFT' if loc[0] < 3 else 'RIGHT'
    td = 'BOT' if loc[1] < 3 else 'TOP'
    can_edge = ['EDGE'] if (loc[0] in [0, 5] or loc[1] in [0, 5]) else []
    can_corner = ['CORNER'] if loc in [(0,0),(0,1),(1,0),(1,1),
                                       (0,5),(0,4),(1,5),(1,4),
                                       (5,0),(5,1),(4,0),(4,1),
                                       (5,5),(5,4),(4,5),(4,4)] else []
    can_center = ['CENTER'] if loc in [(2,2),(3,2),(2,3),(3,3)] else []

    ret = [loc, lr, td] + can_edge + can_corner + can_center + ['UNK']
    return ret

# ========================== W ===============================
# genreate a random w
def gen_w():
    n_color = random.choice(W_N_COLOR_DISTR)
    ret = () 
    booked_locs = set()
    for n in range(n_color):
        color = random.choice(W_COLOR)
        loc = random.choice(W_LOC)
        while loc in booked_locs:
            loc = random.choice(W_LOC)
        booked_locs.add(loc)
        ret += ((color, loc),)
    return ret

# render a w into /drawings/ directory
def render_w(w, name='w'):
    R = 0.08
    plt.figure()
    currentAxis = plt.gca(aspect='equal')

    for dot_c, dot_loc in w:
        if dot_loc is not None:
            x, y = dot_loc
            currentAxis.add_patch(Circle((x/6+R, y/6+R), R, facecolor=dot_c))
    plt.savefig(f'drawings/{name}.png')
    plt.close()

# ========================== U ===========================
# the REPL state for SPKer S(u|w), consisting of a world, and the utterance-so-far
SSPK = namedtuple('SSPK', 'w cost ref us info')

# Grammar for U
# U    - Ui | stop
# Ui   - Uloc | Urel
# Uloc - Name Balls M[Q] M[C] M[LOC]

class SREPL:

    def __init__(self):
        # the legal choices the agents can take
        self.legal_actions = {
                'U'      : ['Ui', 'stop'],
                'stop'   : [],
                'Ui'     : ['Uloc', 'Urel'],
                'Uloc'   : ['Bsel'],
                'Bsel'   : ['Yes', 'No'],
                'M[Q]'   : U_QUANT,
                'M[C]'   : U_COLOR,
                'M[Loc]' : U_LOC,

                }

    def init_sspk(self, w): 
        return SSPK(w, 0, [], [], {'state' : 'U', 
                                   'legal_actions' : self.legal_actions['U']}) 

    def render(self, sspk):
        return self.sspk

    def step(self, sspk, action_id):

        state = sspk.info['state']
        action = sspk.info['legal_actions'][action_id]
        next_cost = sspk.cost + u_cost(action) 

        if state == 'U':
            if action == 'stop':
                return 'stop'
            if action == 'Ui':
                next_state = action
                # if you have 2 things u can refer to them, else u Uloc only
                next_actions = self.legal_actions[next_state] if \
                        len(sspk.ref) >= 2 else ['Uloc']
                return sspk._replace(
                        cost = next_cost,
                        info = {'state' : next_state,
                                'legal_actions' : next_actions })

        if state == 'Ui':
            if action == 'Uloc':
                name = f"name{len(sspk.us)}"
                next_state = 'Bsel'
                next_actions = self.legal_actions[next_state]
                next_us = sspk.us + [['loc', name],]
                next_ref = sspk.ref + [[]]
                return sspk._replace(
                        cost = next_cost,
                        ref = next_ref,
                        us = next_us,
                        info = {'state' : next_state,
                                'legal_actions' : next_actions })
            if action == 'Urel':
                assert 0

        if state == 'Bsel':
            last_ref = sspk.ref[-1]
            more_ref = [1] if action == 'Yes' else [0]
            next_ref = sspk.ref[:-1] + [sspk.ref[-1] + more_ref]

            next_state = 'Bsel' if len(next_ref[-1]) < len(sspk.w) else 'M[Q]'
            
            next_actions = self.legal_actions[next_state]

            # force select, if we selected [0..0] for ref we must select 1 on last move
            if next_state == 'Bsel' and len(next_ref[-1]) + 1 == len(sspk.w) and sum(next_ref[-1]) == 0:
                next_actions = ['Yes']
            
            # force legal moves on M[Q]
            if next_state == 'M[Q]':
                next_actions = [str(sum(next_ref[-1])), 'SOME']
                if sum(sspk.ref[-1]) == len(sspk.w):
                    next_actions += ['ALL']

            return sspk._replace(
                        cost = next_cost,
                    ref = next_ref,
                    info = {'state' : next_state,
                            'legal_actions' : next_actions })

        
        if state == 'M[Q]':
            next_us = sspk.us[:-1] + [sspk.us[-1] + [action]]

            next_state = 'M[C]'
            next_actions = self.legal_actions[next_state]
            colors_idx = [i for i in range(len(sspk.w)) if sspk.ref[-1][i] == 1]
            colors = list(set([sspk.w[i][0] for i in colors_idx]))
            assert len(colors) > 0, "empty reference selected"
            if len(colors) == 1:
                next_actions = colors + ['UNK']
            else:
                next_actions = ['DIFF'] + ['UNK']

            return sspk._replace(
                        cost = next_cost,
                    us = next_us,
                    info = {'state' : next_state,
                            'legal_actions' : next_actions })

        if state == 'M[C]':
            next_us = sspk.us[:-1] + [sspk.us[-1] + [action]]
            next_state = 'M[Loc]'

            loc_idx = [i for i in range(len(sspk.w)) if sspk.ref[-1][i] == 1]
            locs = [sspk.w[i][1] for i in loc_idx]
            loc_attr = [set(get_loc_attr(loc)) for loc in locs]
            next_actions = list(set.intersection(*loc_attr))
            if next_actions == ['UNK']:
                next_actions += ['DIFF']

            return sspk._replace(
                        cost = next_cost,
                    us = next_us,
                    info = {'state' : next_state,
                            'legal_actions' : next_actions })

        if state == 'M[Loc]':
            next_us = sspk.us[:-1] + [sspk.us[-1] + [action]]
            next_state = 'U'
            next_actions = self.legal_actions[next_state]

            return sspk._replace(
                        cost = next_cost,
                    us = next_us,
                    info = {'state' : next_state,
                            'legal_actions' : next_actions })

        assert 0


class S0:

    def act(self, sspk):
        indexs = [_ for _ in range(len(sspk.info['legal_actions']))]
        return random.choice(indexs)

class Scopy:

    def __init__(self, seq):
        self.seq = seq
        self.idx = -1

    def act(self, sspk):
        self.idx += 1
        return self.seq[self.idx]

def speak(srepl, w, speaker):
    sspk = srepl.init_sspk(w)
    for i in range(30):
        print (sspk)
        action = speaker.act(sspk) 
        nxt_sspk = srepl.step(sspk, action)
        if nxt_sspk == 'stop':
            return sspk
        sspk = nxt_sspk




if __name__ == '__main__':
    w = gen_w()
    print (w) 
    render_w(w)

    srepl = SREPL()
    s0 = S0()
    spk = Scopy([0, 0, 0, 1, 0, 1, 2, 0, 1, 0, 1, 0, 1, 0])
    speak(srepl, w, s0)
