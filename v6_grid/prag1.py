from grid import *
import tqdm
import pickle
import numpy as np

L0VS = pickle.load(open("L0VS.p" ,"rb"))

# the literal listener upon hearing utterances
def L0(us):
    ret = set.intersection(*[L0VS[u] for u in us])
    pr = np.ones(len(ret)) + 1e-4 * np.random.random(len(ret))
    return ret, pr / np.sum(pr) 

# the literal speaker that utters all it can sans whats already being said
def S0(prog_tup, us=[]):
    shapes = render_shapes(unserialize(prog_tup))
    utters = []
    for i in range(L):
        for j in range(L):
            to_append = ((i, j), shapes[(i,j)] if (i,j) in shapes else 'EMPTY')
            if to_append not in us:
                utters.append(to_append)
    return utters

# get 1step S1 probability, PS1_1(u | w us)
# return a list of further uttrances and PS1_1(u | w us) normalised
def PS1_1(prog_tup, us):
    u_news = S0(prog_tup, us)
    vs_us = L0(us)[0] if len(us) > 0 else set()

    u_weights = []
    for u_new in u_news:
        vs_us_new = set.intersection(vs_us, L0([u_new])[0]) if len(vs_us) > 0 else L0([u_new])[0]
        u_weights.append(1 / len(vs_us_new))
    u_weights = np.array(u_weights)
    return u_news, u_weights / np.sum(u_weights)

# get a logPS1 score for a particular us upon prog_tup
def logPS1(prog_tup, us):
    logpr = 0.0
    for i in range(len(us)):
        to_utter = us[i]
        utters, utter_prob = PS1_1(prog_tup, us[:i]) 
        prob_idx = utters.index(to_utter)
        logpr += np.log(utter_prob[prob_idx])
    return logpr

# get PL1 from utterances us
def PL1(us):
    progs = list(L0(us)[0])
    prog_weights = []
    #print (len(progs))
    #if len(progs) > 100:
    #    print ("too long")
    #    return L0(us)

    for i, p in tqdm.tqdm(enumerate(progs)):
        prog_weights.append(logPS1(p, us))
    return progs, prog_weights

def interactive(listener):
    _, shapes = gen_legal_prog_shape()
    draw(shapes, 'target')
    us = []
    while True:
        raw = input("i j SHAPE COLOR \n>>>").split(' ')
        # UNDO UNDO LMAO
        if raw[0] == 'UNDO':
            us = us[:-1]
            if len(us) == 0:
                continue
        else:
            coords = int(raw[0]), int(raw[1])
            shape = raw[2]
            if shape == 'EMPTY':
                us.append((coords, 'EMPTY'))
            else:
                us.append((coords, (shape, raw[3])))

        prog_tups, prog_weights = listener(us)
        print (f"{len(prog_tups)} candidates remain")
        prog_tups = list(prog_tups)
        idx_weights = list(reversed(sorted(list(zip(prog_weights, range(len(prog_weights)))))))
        print (f"top3 {idx_weights[:3]}")
        top3 = [x[1] for x in idx_weights[:3]]
        for j, i in enumerate(top3):
            draw(render_shapes(unserialize(prog_tups[i])), f"candidate_{j}")


if __name__ == '__main__':
    interactive(PL1)
    
