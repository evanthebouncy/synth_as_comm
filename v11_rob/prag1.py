import random
from fake_fill import P, sample_E_params, sample_input
import tqdm
import pickle
import numpy as np

ALL_PROGS, ALL_INPUTS, L0VS = pickle.load(open("L0VS.p" ,"rb"))

# a notion of same program in the sense of function equivalence
def same_prog(p1, p2):
    assert 0, "we dont need this now"
    for inp in ALL_INPUTS:
        if p1(inp) != p2(inp):
            return False
    return True

# the literal listener upon hearing utterances
def L0(us):
    ret = set.intersection(*[L0VS[u] for u in us])
    pr = np.ones(len(ret))
    return ret, pr / np.sum(pr) 

# the literal speaker that utters all it can sans whats already being said
def S0(prog_id, us=[]):
    prog = P.generate(ALL_PROGS[prog_id])
    utters = []
    for inp in ALL_INPUTS:
        to_append = (inp, prog(inp))
        if to_append not in us:
            utters.append(to_append)
    return utters

# a heuristic for a good candidate is simply longest
def Slong(prog_id):
    prog = P.generate(ALL_PROGS[prog_id])
    xx = [(len(prog(inp)), inp, prog(inp)) for inp in ALL_INPUTS]
    return list(reversed(sorted(xx)))[:10]
    

# get 1step S1 probability, PS1_1(u | w us)
# return a list of further uttrances and PS1_1(u | w us) normalised
def PS1_1(prog_id, us):
    u_news = S0(prog_id, us)
    vs_us = L0(us)[0] if len(us) > 0 else set()

    u_weights = []
    for u_new in u_news:
        vs_us_new = set.intersection(vs_us, L0([u_new])[0]) if len(vs_us) > 0 else L0([u_new])[0]
        u_weights.append(1 / len(vs_us_new))
    u_weights = np.array(u_weights)
    return u_news, u_weights / np.sum(u_weights)

# get a logPS1 score for a particular us upon prog_id
def logPS1(prog_id, us):
    logpr = 0.0
    for i in range(len(us)):
        to_utter = us[i]
        utters, utter_prob = PS1_1(prog_id, us[:i]) 
        prob_idx = utters.index(to_utter)
        logpr += np.log(utter_prob[prob_idx])
    return logpr

# get the top1 utterance by S1
def get_top1_S1(prog_id, n_utter):
    utters = []
    for i in range(n_utter):
        best_nxt = None
        best_score = -99999
        for nxt_utter in tqdm.tqdm(S0(prog_id, utters)):
            full_utter = utters + [nxt_utter]
            score = logPS1(prog_id, full_utter)
            if score > best_score:
                best_score = score
                best_nxt = nxt_utter
        utters = utters + [best_nxt]
    return utters

# get PL1 from utterances us
def PL1(us, limit=500):
    prog_ids = list(L0(us)[0])[:limit]
    prog_id_weights = []
    for i, p in tqdm.tqdm(enumerate(prog_ids)):
        prog_id_weights.append(logPS1(p, us))
    return prog_ids, prog_id_weights

def interactive(listener, goal_prog_id):
    goal_prog = P.generate(ALL_PROGS[goal_prog_id])
    print ("target prog ")
    print (goal_prog_id)
    print (goal_prog)
    print (Slong(goal_prog_id))

    us = []
    while True:
        raw = input("new input [output will be generated]\n>>>")
        # UNDO UNDO LMAO
        if raw == 'UNDO':
            us = us[:-1]
            if len(us) == 0:
                continue
        # do a new program 
        if raw == 'NEW':
            rand_id = random.choice([_ for _ in range(len(ALL_PROGS))])
            interactive(listener, rand_id)
            return
        # do a new program 
        if raw == 'AGAIN':
            interactive(listener, goal_prog_id)
            return
        else:
            print (20 * "-")
            print ("added input-output example ", (raw, goal_prog(raw)))
            us.append((raw, goal_prog(raw)))

        prog_idx_ids, idd_weights = listener(us)
        print (f"{len(prog_idx_ids)} candidates remain")
        prog_idxs = list(prog_idx_ids)
        idx_weights = list(reversed(sorted(list(zip(idd_weights, range(len(idd_weights)))))))
        print (f"top3 {idx_weights[:3]}")
        top3 = [x[1] for x in idx_weights[:3]]
        for j, i in enumerate(top3):
            print ('candidate program ', i)
            print (P.generate(ALL_PROGS[prog_idxs[i]]))
        if prog_idxs[top3[0]] == goal_prog_id:
            print ("YOU FUCKIN WON THE GAME")



if __name__ == '__main__':
    rand_id = random.choice([_ for _ in range(len(ALL_PROGS))])
    rand_id = 616
    interactive(PL1, rand_id)
    
