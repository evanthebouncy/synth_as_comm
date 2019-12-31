import random
from fake_fill import P, sample_E_params, sample_input
import tqdm
import pickle
import numpy as np

ALL_PROGS, L0VS = pickle.load(open("L0VS.p" ,"rb"))

# the literal listener upon hearing utterances
def L0(us):
    ret = set.intersection(*[L0VS[u] for u in us])
    pr = np.ones(len(ret))
    return ret, pr / np.sum(pr) 

# the literal speaker that utters all it can sans whats already being said
def S0(shape_repr_id, us=[]):
    shapes = ALL_PROGS[shape_repr_id]
    utters = []
    for i in range(L):
        for j in range(L):
            to_append = (i, j, shapes[i][j])
            if to_append not in us:
                utters.append(to_append)
    return utters

# get 1step S1 probability, PS1_1(u | w us)
# return a list of further uttrances and PS1_1(u | w us) normalised
def PS1_1(shape_repr_id, us):
    u_news = S0(shape_repr_id, us)
    vs_us = L0(us)[0] if len(us) > 0 else set()

    u_weights = []
    for u_new in u_news:
        vs_us_new = set.intersection(vs_us, L0([u_new])[0]) if len(vs_us) > 0 else L0([u_new])[0]
        u_weights.append(1 / len(vs_us_new))
    u_weights = np.array(u_weights)
    return u_news, u_weights / np.sum(u_weights)

# get a logPS1 score for a particular us upon shape_repr_id
def logPS1(shape_repr_id, us):
    logpr = 0.0
    for i in range(len(us)):
        to_utter = us[i]
        utters, utter_prob = PS1_1(shape_repr_id, us[:i]) 
        prob_idx = utters.index(to_utter)
        logpr += np.log(utter_prob[prob_idx])
    return logpr

# get the top1 utterance by S1
def get_top1_S1(shape_repr_id, n_utter):
    utters = []
    for i in range(n_utter):
        best_nxt = None
        best_score = -99999
        for nxt_utter in S0(shape_repr_id, utters):
            full_utter = utters + [nxt_utter]
            score = logPS1(shape_repr_id, full_utter)
            if score > best_score:
                best_score = score
                best_nxt = nxt_utter
        utters = utters + [best_nxt]
    return utters

# get PL1 from utterances us
def PL1(us, limit=500):
    shape_repr_ids = list(L0(us)[0])[:limit]
    shape_repr_id_weights = []
    for i, p in tqdm.tqdm(enumerate(shape_repr_ids)):
        shape_repr_id_weights.append(logPS1(p, us))
    return shape_repr_ids, shape_repr_id_weights

def interactive(listener, goal_prog_id):
    goal_prog = P.generate(ALL_PROGS[goal_prog_id])
    print ("target prog ")
    print (goal_prog_id)
    print (goal_prog)

    us = []
    while True:
        raw = input("input,output\n>>>").split(',')
        # UNDO UNDO LMAO
        if raw[0] == 'UNDO':
            us = us[:-1]
            if len(us) == 0:
                continue
        else:
            us.append(tuple(raw))

        prog_repr_ids, idd_weights = listener(us)
        print (f"{len(prog_repr_ids)} candidates remain")
        prog_reprs = list(prog_repr_ids)
        idx_weights = list(reversed(sorted(list(zip(idd_weights, range(len(idd_weights)))))))
        print (f"top3 {idx_weights[:3]}")
        top3 = [x[1] for x in idx_weights[:3]]
        for j, i in enumerate(top3):
            print ('candidate program ', i)
            print (P.generate(ALL_PROGS[prog_reprs[i]]))


if __name__ == '__main__':
    rand_id = random.choice([_ for _ in range(len(ALL_PROGS))])
    interactive(L0, rand_id)
    
